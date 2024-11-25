from collections.abc import Callable
import random
from typing import Optional
from .Status import TaskStatus, TaskInstanceStatus
import logging

logger = logging.getLogger(__name__)

class Task:
    def __init__(self,
        function: Optional[Callable[[], None]] = None,         
        ) -> None:
        self.function = function
        self.status = TaskStatus.PENDING
        self.is_set = False
        self.id = None
        self.task_db_instance = None
        self.update_task_status = None
        self.update_task_error = None
        self.update_task_completed = None
        self.previous_task_instance = None

    def run(self) -> bool:
        # Validate task before running
        if self.function is None:
            raise ValueError("Task function is not set")
        if not self.is_set:
            raise ValueError("Task is not set")
                
        # Execute task
        try:
            self.status = TaskStatus.RUNNING
            self.update_task_status(TaskInstanceStatus.RUNNING)
            task_result = self.function()
            self.update_task_completed()
            self.status = TaskInstanceStatus.DONE if task_result else TaskInstanceStatus.ERROR
            return task_result
        
        except Exception as e:
            self.update_task_error(e)
            self.status = TaskInstanceStatus.ERROR
            return False
        
    def set(self, task_db_instance, gen_handlers, fuctnion: Optional[Callable[[], bool]]=None):
        if fuctnion is not None:
            self.function = fuctnion
        if self.function is None:
            raise ValueError("Task function is not set")
        
        self.id = task_db_instance.id
        self.task_db_instance = task_db_instance
        self.set_handlers(*gen_handlers(task_db_instance))
        self.status = TaskStatus.READY
        self.is_set = True
        self.update_task_status(TaskInstanceStatus.PENDING)
        logger.info(f"Task {self.id} : Task set")

    def set_handlers(self, update_task_status, update_task_error, update_task_completed):
        self.update_task_status = update_task_status
        self.update_task_error = update_task_error
        self.update_task_completed = update_task_completed
        self.status = TaskStatus.READY
        logger.info(f"Task {self.id} : Task handlers set")

    def release(self):
        id = self.id # logging only
        self.previous_task_instance = self.task_db_instance
        self.id = None
        self.task_db_instance = None
        self.update_task_status = None
        self.update_task_error = None
        self.update_task_completed = None
        self.status = TaskStatus.PENDING
        self.is_set = False
        logger.info(f"Task {id} : Task released")

    def get_instance(self):
        if self.task_db_instance is None:
            return self.previous_task_instance
        return self.task_db_instance
    
dummy_task = Task()