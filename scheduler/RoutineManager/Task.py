import time
import random
from .Status import TaskStatus, TaskInstanceStatus
import logging

logger = logging.getLogger(__name__)

class Task:
    def __init__(self):
        self.status = TaskStatus.PENDING
        self.is_set = False
        self.id = None
        self.task_db_instance = None
        self.update_task_status = None
        self.update_task_error = None
        self.update_task_completed = None
        self.previous_task_instance = None

    def run(self) -> bool:
        try:
            self.status = TaskStatus.RUNNING
            print("dummy task running")
            self.update_task_status(TaskInstanceStatus.RUNNING)
            time.sleep(30)
            print("dummy task is done")
            self.update_task_completed()
            return True if random.randint(0, 1) == 1 else False
        
        except Exception as e:
            self.update_task_error(e)
            return False
        
    def set(self, task_db_instance, gen_handlers):
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