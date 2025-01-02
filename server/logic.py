import json
import logging

from typing import Any, Dict, List
from rabbitMQ import send_message

logger = logging.getLogger(__name__)


def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class Logic:
    def __init__(self):
        self.MAX_TASKS = 5
        self.routines = {}

    def reset_routines(self):
        self.routines.clear()

    def get_routines_list(self) -> List[str]:
        routines_list = [routine for routine in self.routines.keys()]
        return routines_list

    def get_state(self, routine_name: str) -> Dict[str, Any]:
        routine_state = self.routines.get(routine_name, {
                    "status": None,
                    "tasks": {}
                })
        return routine_state

    def get_routine_state(self, routine_name: str) -> Dict[str, Any]:
        logger.debug(f"get_routine_state | Getting state for routine {routine_name}")
        routine_status = self.routines.get(routine_name, None)
        logger.debug(f"get_routine_state | Routine status: {routine_status}")
        if routine_status is None:
            logger.debug(f"get_routine_state | Routine {routine_name} not found. Creating new entry")
            routine_status = {
                "epoch": 0,
                "status": None,
                "tasks": {}
            }
            logger.debug(f"get_routine_state | Routine {routine_name} created: {routine_status}")
            self.routines[routine_name] = routine_status
        logger.debug(f"get_routine_state | Returning routine {routine_status}")
        return routine_status
    
    def get_task_state(self, routine_name: str, task_id: int) -> Dict[str, Any]:
        routine_state = self.get_routine_state(routine_name)
        tasks = routine_state.get("tasks", None)
        if tasks is None:
            tasks = {}
            routine_state["tasks"] = tasks

        task_status = tasks.get(task_id, None)
        if task_status is None:
            task_status = {"epoch": 0, "status": None}
            routine_state["tasks"][task_id] = task_status

        return routine_state["tasks"][task_id]
    
    def update_routine_status(self, routine_name: str, status: str, epoch: int) -> None:
        routine_state = self.get_routine_state(routine_name)
        logger.debug(f"update_routine_status | Updating routine {routine_state} status to {status} at {epoch}")
        if epoch < routine_state["epoch"]:
            logger.debug(f"handle_message | Ignoring outdated message for routine {routine_name}")
            return
        routine_state["status"] = status
        routine_state["epoch"] = epoch

    def update_task_status(self, routine_name: str, task_id: int, status: str, epoch: int) -> None:
        routine_state = self.get_routine_state(routine_name)
        task_state = self.get_task_state(routine_name, task_id)
        logger.debug(f"update_task_status | Updating task {task_state} task {task_id} status to {status} at {epoch}")
        if epoch < task_state["epoch"]:
            logger.debug(f"handle_message | Ignoring outdated message for task {task_id}")
            return
        task_state["epoch"] = epoch
        task_state["status"] = status
        
        if len(routine_state["tasks"]) > self.MAX_TASKS:
            del routine_state["tasks"][min(routine_state["tasks"])]


def send_message_to_scheduler(command: str, routine_name: str):
    send_message(
        "commands", 
        {
            "command": command,
            "routine": routine_name
        }
    )

def handle_message(ch, method, _properties, body: bytes):
    logic = Logic()
    try:
        logger.debug(f"handle_message | Received message: {body}")
        message = json.loads(body)
        message_type = message["type"]
        routine = message["routine"]
        if type(routine) is not str:
            raise AssertionError("Routine must be a string")
        status = message["status"]
        epoch = message["epoch"]
        task_id = message.get("task_id", None)
        if message_type == "routine_status":
            logger.debug(f"handle_message | Updating routine {routine} status to {status}")
            logic.update_routine_status(routine, status, epoch)
            logger.debug(f"handle_message | Routine {routine} status updated to {status}")

        elif message_type == "task_status":
            logger.debug(f"handle_message | Updating routine {routine} task {task_id} status to {status}")
            logic.update_task_status(routine, task_id, status, epoch)
            logger.debug(f"handle_message | Routine {routine} task {task_id} status updated to {status}")

        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

    except Exception as e:
        logger.error(f"handle_message | Error handling message {body}: {e}")