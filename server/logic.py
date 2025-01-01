import json
import logging

from typing import Any, Dict, List
from rabbitMQ import send_message

logger = logging.getLogger(__name__)

MAX_TASKS = 5
routines = {}

def reset_routines():
    routines.clear()

def get_routines_list() -> List[str]:
    routines_list = [routine for routine in routines.keys()]
    return routines_list

def get_state(routine_name: str) -> Dict[str, Any]:
    routine_state = routines.get(routine_name, {
                "status": None,
                "tasks": {}
            })
    return routine_state

def send_message_to_scheduler(command: str, routine_name: str):
    send_message(
        "commands", 
        {
            "command": command,
            "routine": routine_name
        }
    )

def handle_message(ch, method, _properties, body: bytes):
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
            routine_state = routines.get(routine, {
                "status": None,
                "epoch": 0,
                "tasks": {}
            })
            if epoch < routine_state["epoch"]:
                logger.debug(f"handle_message | Ignoring outdated message for routine {routine}")
                return
            routine_state["status"] = status
            routines[routine] = routine_state
            logger.debug(f"handle_message | Routine {routine} status updated to {status}")

        elif message_type == "task_status":
            logger.debug(f"handle_message | Updating routine {routine} task {task_id} status to {status}")
            routine_state = routines.get(routine, {
                "status": None,
                "epoch": 0,
                "tasks": {}
            })
            tasks = routine_state.get("tasks", {})
            if epoch < tasks.get(task_id, {}).get("epoch", 0):
                logger.debug(f"handle_message | Ignoring outdated message for task {task_id}")
                return
            tasks[task_id] = {"epoch": epoch, "status": status}
            if len(tasks) > MAX_TASKS:
                del tasks[min(tasks)]
            routine_state["tasks"] = tasks
            routines[routine] = routine_state
            logger.debug(f"handle_message | Routine {routine} task {task_id} status updated to {status}")

        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

    except Exception as e:
        logger.error(f"handle_message | Error handling message {body}: {e}")