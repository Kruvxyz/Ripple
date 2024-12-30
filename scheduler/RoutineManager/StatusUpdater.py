from shared import update_routine_status, update_task_status
import logging


logger = logging.getLogger(__name__)

class StatusUpdater:
    def __init__(self):
        self.routines_current_status = {}
        self.tasks_current_status = {}

    def task_status_updater(
        self,
        routine_name: str,
        status: str,
        task_id: int
    ) -> bool:
        if self.tasks_current_status.get(routine_name, None) != status:
            logger.debug(f"task_status_updater - {routine_name} task_id {task_id} updating status to {status}")
            update_task_status(routine_name, task_id, status)
            self.tasks_current_status[routine_name] = status
            logger.info(f"task_status_updater - {routine_name} task_id {task_id} updated status to {status}")

    def routine_status_updater(
        self, 
        routine_name: str, 
        status: str
    ) -> bool:
        if self.routines_current_status.get(routine_name, None) != status:
            logger.debug(f"routine_status_updater - {routine_name} updating routine status to {status}")
            update_routine_status(routine_name, status)
            self.routines_current_status[routine_name] = status
            logger.info(f"routine_status_updater - {routine_name} updated routine status to {status}")
        return True
    