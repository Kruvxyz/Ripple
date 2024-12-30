from collections.abc import Callable
from sqlalchemy.exc import ResourceClosedError
from typing import Any, Tuple, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError
import time
import logging
from db import gen_routine_handlers, reattach_routine
from .Trigger import Trigger
from .Status import RoutineStatus, TaskInstanceStatus, TriggerInstanceStatus 
from .Task import Task

logger = logging.getLogger(__name__)


class Routine:
    """
    Routines are asynchronous tasks that run at a specified interval. 
    Routine flow:
    1. check if task is set.
        1.1 if set - check if running.
            1.1.1. If running: sleep and return to 1
            1.1.2. If error: increase retry count rerun task
            1.1.3. else: release task
    2. check if trigger
        2.1 Trigger: run task
        2.2 Not trigger: sleep and return to 1
    3. wait for task to complete
    4. release task

    States:
    - WAITING: Routine is waiting for the condition to be met
    - PENDING: Routine is preparing to run the task
    - RUNNING: Routine is currently executing the task
    - DONE: Routine has completed the task and is resetting
    - ERROR: Routine encountered an error and will retry
    - RETRY: Routine is retrying the task after an error
    - FAIL: Routine has failed after exceeding retry limit
    - COMPLETE: Routine has completed its run-once task
    - CANCELED: Routine has been canceled
    """
    def __init__(
            self, 
            name: str, 
            description: str, 
            task: Task, 
            trigger: Trigger,
            interval: int = 60, 
            retry_delay: int = 5*60, # default 5 minutes
            retry_limit: int = 5, # default 5 retries
            timeout_limit: int = 60*60, # default 1 hour
            gen_handler: Any = None,
            run_once: bool = False
        ) -> None:
        self.name = name
        self.description = description
        self.task = task
        self.trigger = trigger
        self.interval = interval
        self.retry_delay = retry_delay
        self.retry_limit = retry_limit
        self.timeout_limit = timeout_limit
        self.run_once = run_once
        self.status = RoutineStatus.WAITING

        # Handlers
        if gen_handler is None:
            gen_handler = gen_routine_handlers
        self.session, self.gen_routine, self.update_status, self.update_error, self.create_new_task, self.gen_task_handlers = gen_handler(self.name)
        self.current_task_db_instance = None

        # State
        self.num_retries = 0

        # Update DB
        self.routine = self.gen_routine(description)       

    def get_task_status(self) -> Optional[str]:
        if self.task is not None:
            return self.task.status
        return None
    
    def get_task_id(self) -> Optional[int]:
        if self.current_task_db_instance is not None:
            return self.current_task_db_instance.id
        return None
    
    async def step(self) -> bool:
        logger.debug(f"Routine {self.name}: step")

        # WAITING
        # Next steps: [PENDING]
        if self.status == RoutineStatus.WAITING:
            logger.debug(f"Routine {self.name} : Waiting for condition to be met")
            if self.trigger.status == TriggerInstanceStatus.RUNNING:
                if not self.trigger.is_busy():
                    try:
                        result = await self.trigger.get_result()
                        if result:
                            self.status = RoutineStatus.PENDING
                    except Exception as e:
                        logger.warning(f"Routine {self.name} : trigger exception {e}")
            else:
                await self.trigger.run()

        # PENDING / RETRY
        # Nex steps: [RUNNING]
        elif self.status == RoutineStatus.PENDING or self.status == RoutineStatus.RETRY:
            logger.info(f"Routine {self.name} : Preparing task")
            self.set_new_task()
            self.status = RoutineStatus.RUNNING
        
        # RUNNING
        # Next steps: [DONE, ERROR, COMPLETE]
        elif self.status == RoutineStatus.RUNNING:
            logger.info(f"Routine {self.name} : Running task")
            if self.task.status == TaskInstanceStatus.RUNNING:
                if not self.task.is_busy():
                    try:
                        result = await self.task.get_result()
                        if result:
                            if self.run_once:
                                self.status = RoutineStatus.COMPLETE
                            else:
                                self.status = RoutineStatus.DONE
                        else:
                            self.status = RoutineStatus.ERROR
                            self.num_retries += 1
                    except Exception as e:
                        logger.warning(f"Routine {self.name} : task exception {e}")
            else:
                await self.task.run()
                
        # DONE
        # Next steps: [WAITING]
        elif self.status == RoutineStatus.DONE:
            logger.info(f"Routine {self.name}: Done")
            self.release_task()
            self.num_retries = 0
            self.status = RoutineStatus.WAITING

        # ERROR
        # Next steps: [RETRY, FAIL]
        elif self.status == RoutineStatus.ERROR:
            logger.info(f"Routine {self.name}: Error")
            self.release_task()
            if self.num_retries >= self.retry_limit:
                logger.error("Retry limit reached for the routine")
                self.status = RoutineStatus.FAIL
            else:
                self.status = RoutineStatus.RETRY

        # FAIL
        # Next steps: [None]
        elif self.status == RoutineStatus.FAIL:
            logger.info(f"Routine {self.name}: Fail")
            return False
        
        # COMPLETE
        # Next steps: [None]
        elif self.status == RoutineStatus.COMPLETE:
            self.release_task()
            logger.info("Routine {self.name} : Run once routine completed")
            return True

        elif self.status == RoutineStatus.CANCELED:
            logger.info(f"Routine {self.name}: Canceled")
            return False

    def set_new_task(self):
        #TODO: cleanup
        logger.info(f"Routine {self.name} : Setting new task")
        self.current_task_db_instance = self.create_new_task()
        logger.info(f"Routine {self.name} : Task created: {self.current_task_db_instance}")
        ## gen task handlers
        self.task.set(self.current_task_db_instance, self.gen_task_handlers)
        logger.info(f"Routine {self.name} : Task set")

    def release_task(self):  
        self.current_task_db_instance = None
        self.task.release()

    async def cancel(self) -> None:
        if self.status == RoutineStatus.RUNNING:
            await self.task.cancel()
        if self.status == RoutineStatus.PENDING:
            await self.trigger.cancel()
        self.release_task() #FIXME: check if this is needed
        self.status = RoutineStatus.CANCELED
        logger.info(f"Routine {self.name} : Canceled")

    async def start(self) -> None:
        if self.status == RoutineStatus.CANCELED:
            self.status = RoutineStatus.WAITING

    async def execute(self) -> None:
        if self.status != RoutineStatus.RUNNING:
            self.status = RoutineStatus.PENDING
            self.trigger.cancel()
