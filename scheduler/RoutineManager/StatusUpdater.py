import logging
import time
from .rabbitMQ import send_message
from .Status import TaskInstanceStatus
from typing import Optional

logger = logging.getLogger(__name__)

class StatusUpdater:
    def __init__(self):
        self.routines_current_status = {}
        self.tasks_current_status = {}

    def task_status_updater(
        self,
        routine_name: str,
        status: str,
        task_id: Optional[int] = None
    ) -> bool:
        if status == TaskInstanceStatus.PENDING:
            return True
        if task_id is None:
            return True
        if self.tasks_current_status.get(task_id, None) != status:
            logger.debug(f"task_status_updater - {routine_name} task_id {task_id} updating status to {status}")
            send_message(
                "status_updates",
                {
                    "type": "task_status",
                    "routine": routine_name,
                    "task_id": task_id,
                    "status": status,
                    "epoch": int(time.time())
                }
            )
            self.tasks_current_status[task_id] = status
            logger.info(f"task_status_updater - {routine_name} task_id {task_id} updated status to {status}")
        return True
    
    def routine_status_updater(
        self, 
        routine_name: str, 
        status: str
    ) -> bool:
        if self.routines_current_status.get(routine_name, None) != status:
            logger.debug(f"routine_status_updater - {routine_name} updating routine status to {status}")
            send_message(
                "status_updates",
                {
                    "type": "routine_status",
                    "routine": routine_name,
                    "status": status,
                    "epoch": int(time.time())
                }
            )
            self.routines_current_status[routine_name] = status
            logger.info(f"routine_status_updater - {routine_name} updated routine status to {status}")
        return True
    