from collections.abc import Callable
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError
import time
import logging
from db import gen_routine_handlers
from .Status import RoutineStatus, TaskInstanceStatus 
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
    - PENDING: Routine initial state before running
    - WAITING: Routine is waiting for the condition to be met
    - EXECUTING / RUNNING: Routine is currently being executed, this means the task is running

    Routines are made of 2 parts:
    - Trigger (condition to be met before executing the routine's task)
    - Task (function to be executed when trigger is met will run on separate threads (Thread Pool Executor / Process Pool Executor))
    Routines can be stopped, started, and paused.
    """
    def __init__(
            self, 
            name: str, 
            description: str, 
            task: Task, 
            interval: int, 
            condition_function:Optional[Callable[[], bool]]=None,
            condition_function_args: Optional[str]=None,
            condition_interval: int=60, # default 1 minute
            retry_delay: int=5*60, # default 5 minutes
            retry_limit: int=5, # default 5 retries
            timeout_limit: int=60*60 # default 1 hour
        ) -> None:
        self.name = name
        self.description = description
        self.task = task
        self.interval = interval
        self.condition_function = condition_function
        self.condition_interval = condition_interval
        self.retry_delay = retry_delay
        self.retry_limit = retry_limit
        self.timeout_limit = timeout_limit

        # Handlers
        self.session, self.gen_routine, self.update_status, self.update_error, self.create_new_task, self.gen_update_task = gen_routine_handlers(self.name)
        self.current_task_db_instance = None

        # State
        self.num_retries = 0


        # Update DB
        self.routine = self.gen_routine(description)       

    # FIXME: remove and work directly with DB
    # def set_handlers(
    #         self, 
    #         update_status_function: Callable[[str], bool], 
    #         update_error_function: Callable[[str], bool], 
    #         # kill_switch: Optional[Callable[[], bool]] = None
    #     ) -> None:
    #     self.update_status_function = update_status_function
    #     self.update_error_function = update_error_function
    #     # self.kill_switch = kill_switch

    def calculate_sleep_preiod(self) -> int:
        return self.interval

    def get_status(self) -> Optional[str]:
        if self.routine is not None:
            return self.routine.status
        return None
    
    def get_task_status(self) -> Optional[str]:
        #TODO: implement
        pass

    
    def get_error(self):
        return self.routine.error
    
    async def run(self) -> None:
        print(f"------------------{self.name}: Routine started----------------")
        self.update_status(RoutineStatus.PENDING)
        while True:
            try:
                logger.info(f"Routine started: {self.name}")

                logger.info(f"Routine {self.name} : Checking task status and update routine status if needed")
                if self.current_task_db_instance is not None:
                    self.session.refresh(self.current_task_db_instance)
                    if self.current_task_db_instance.status == TaskInstanceStatus.RUNNING:
                        await asyncio.sleep(1) #FIXME: remove magic number

                    elif self.current_task_db_instance.status == TaskInstanceStatus.ERROR:
                        self.num_retries += 1
                        self.update_status(RoutineStatus.RETRYING)
                        self.update_error("Task failed to complete")
                        self.release_task()
                        await asyncio.sleep(self.retry_delay)
                        self.set_new_task()
                        await self.run_and_wait_task_at_thread_pool_executor()
                        continue

                    else:
                        self.release_task()
                        self.update_status(RoutineStatus.WAITING)
                        self.num_retries = 0

                # trigger validation
                logger.info(f"Routine {self.name} : Checking trigger")
                if self.condition_function is None:
                    print(f"-----------{self.name}: CONDITION FUNCTION NOT SET -----------")
                    self.update_error("Condition function not set")
                    return None

                # check if condition is met
                if not self.condition_function():
                    self.update_status(RoutineStatus.WAITING)
                    print(f"-----------{self.name}: CONDITION FUNCTION FAILURE -----------")
                    # time.sleep(self.condition_interval)
                    await asyncio.sleep(self.calculate_sleep_preiod())
                    continue

                print(f"-----------{self.name}: RUNNING FUNCTION-----------")
                logger.info(f"Routine {self.name} : Running task")
                self.update_status(RoutineStatus.RUNNING)
                self.set_new_task()
                await self.run_and_wait_task_at_thread_pool_executor()
                logger.info(f"Routine {self.name} : loop completed")

                await asyncio.sleep(self.calculate_sleep_preiod()) #FIXME: remove magic number


            except Exception as e:
                if self.num_retries >= self.retry_limit:
                    self.update_error("Retry limit reached for the routine")
                    logger.error("Retry limit reached for the routine")
                    return None

                print(f"Error running function with error: {e}")
                logger.error(f"Error running function with error: {e}")
                self.num_retries += 1
                await asyncio.sleep(self.retry_delay)
                continue

            except asyncio.CancelledError:
                self.update_status(RoutineStatus.CANCELED)
                print("Cancelled with asyncio.CancelledError")
                logger.info("Cancelled with asyncio.CancelledError")
                break

            except asyncio.exceptions.CancelledError:
                self.update_status(RoutineStatus.CANCELED)
                print("Cancelled with asyncio.CancelledError")
                logger.info("Cancelled with asyncio.exceptions.CancelledError")
                break

        logger.info(f"Routine finished: {self.name}")

    def set_new_task(self):
        #TODO: cleanup
        logger.info(f"Routine {self.name} : Setting new task")
        self.current_task_db_instance = self.create_new_task()
        logger.info(f"Routine {self.name} : Task created: {self.current_task_db_instance}")
        logger.info(f"Routine {self.name} : Task created: {self.current_task_db_instance} with status: {self.current_task_db_instance.status} and id: {self.current_task_db_instance.id}")
        ## gen task handlers
        self.task.set(self.current_task_db_instance, self.gen_update_task)
        # print("Generating task handlers")
        # update_task_status, update_task_error, update_task_completed = self.gen_update_task(self.current_task_db_instance)
        # print("Task handlers generated")

        # # update task with handlers
        # print("Setting task handlers")
        # self.task.set_handlers(update_task_status, update_task_error, update_task_completed)
        # logger.info(f"Task {self.current_task_db_instance.id} handlers set")
    
    def release_task(self):
        self.current_task_db_instance = None
        self.task.release()

    def run_task_at_thread_pool_executor(self):
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor()
        future = loop.run_in_executor(executor, self.task.run)
        return future
    
    async def run_and_wait_task_at_thread_pool_executor(self):
        try:
            loop = asyncio.get_running_loop()
            executor = ThreadPoolExecutor()
            future = loop.run_in_executor(executor, self.task.run)
            result = await asyncio.wait_for(future, timeout=self.timeout_limit) 
            return result

        # TODO: there is nothing really happen when timeout error occurs. Therefore we should not be waiting for that
        except asyncio.TimeoutError: 
            future.cancel()
            print("Task timed out and will be cancelled.")
        
    def run_task(self):
        self.set_new_task()
        future = self.run_task_at_thread_pool_executor()
        return future
