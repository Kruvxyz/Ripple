from collections.abc import Callable
import random
from typing import Optional
from .Status import TaskInstanceStatus
import logging

logger = logging.getLogger(__name__)

class Task:
    def __init__(
            self,
            name: str,
            function: Optional[Callable[[], None]] = None,         
        ) -> None:
        self.name = name
        self.function = function
        self.status = TaskInstanceStatus.PENDING
        self.is_set = False
        self.id = None
        self.task_db_instance = None
        self.update_task_status = None
        self.update_task_error = None
        self.update_task_completed = None
        self.previous_task_instance = None

    def _set_status(self, status: TaskInstanceStatus):
        logger.info(f"Task {self.id} : Task status set to {status}")
        self.status = status
        if self.is_set:
            self.update_task_status(status)
            logger.info(f"Task {self.id} : Task status updated to {status}")

    def _set_completed(self):
        logger.info(f"Task {self.id} : Task completed")
        self.status = TaskInstanceStatus.DONE
        if self.is_set:
            self.update_task_completed()
            logger.info(f"Task {self.id} : Task completed updated")

    def _set_error(self, error: str):
        logger.error(f"Task {self.id} : Task failed with error {error}")
        self.status = TaskInstanceStatus.ERROR
        if self.is_set:
            self.update_task_error(error)
            logger.error(f"Task {self.id} : Task error updated")

    def run(self) -> bool:
        # Validate task before running
        if self.function is None:
            raise ValueError("Task function is not set")
        if not self.is_set:
            raise ValueError("Task is not set")
                
        # Execute task
        try:
            self._set_status(TaskInstanceStatus.RUNNING)
            task_result = self.function()
            logger.debug(f"Task {self.id} : Task executed with result {task_result}")
            if task_result:
                self._set_completed()
            else:
                self._set_error("Task failed")
            return task_result
        
        except Exception as e:
            self._set_error(f"task {self.name}:{self.id} failed with error:\n{e}")
            return False
        
    def set(self, task_db_instance, gen_handlers, fuctnion: Optional[Callable[[], bool]]=None):
        if fuctnion is not None:
            self.function = fuctnion
        if self.function is None:
            raise ValueError("Task function is not set")
        
        self.id = task_db_instance.id
        self.task_db_instance = task_db_instance
        self.set_handlers(*gen_handlers(task_db_instance))
        self.is_set = True
        self._set_status(TaskInstanceStatus.READY)
        logger.info(f"Task {self.id} : Task set")

    def set_handlers(self, update_task_status, update_task_error, update_task_completed):
        self.update_task_status = update_task_status
        self.update_task_error = update_task_error
        self.update_task_completed = update_task_completed
        logger.info(f"Task {self.id} : Task handlers set")

    def release(self):
        self.is_set = False 
        id = self.id # logging only
        self.previous_task_instance = self.task_db_instance
        self.id = None
        self.task_db_instance = None
        self.update_task_status = None
        self.update_task_error = None
        self.update_task_completed = None
        self._set_status(TaskInstanceStatus.PENDING)
        logger.info(f"Task {id} : Task released")

    def get_instance(self):
        if self.task_db_instance is None:
            return self.previous_task_instance
        return self.task_db_instance
    