import asyncio
from collections.abc import Callable
from shared import Message, get_latest_pending_command, update_routine_status, update_command_status, get_routine_status, update_task_status, get_task
# from Routine import Routine
# from routines.system.routines_managment import gen_routines_managment_routine
import logging
from typing import Any, Dict, Optional, List
from db import init_db
from .Routine import Routine
from .Status import RoutineStatus
from .StatusUpdater import StatusUpdater
from shared.Status import CommandStatus

logger = logging.getLogger(__name__)

TIME_TO_SLEEP = 10 # FIXME: consider to reduce the time

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class RoutineManager:
    """
    The RoutineManager class is responsible for managing routines. 
    It provides functionality to start, stop, restart, and check the status of routines. 
    Additionally, it serves as an interface for users to add new routines and interact with existing ones.
    """
    def __init__(self, *args, **kwargs):
        self.routines: List[Routine] = []
        self.routines_map_tasks: List[asyncio.Task[None]] = {}
        self.status_updater = StatusUpdater()

        init_db()

    def add_routine(self, routine: Routine) -> bool:
        # check routine name is unique
        existed_routine = self.get_routine(routine.name)
        if existed_routine is not None:
            logger.error(f"Routine with name {routine.name} already exists")
            return False
        
        self.routines.append(routine)
        logger.info(f"self.routines: {self.routines}")
        self.status_updater.routine_status_updater(routine.name, RoutineStatus.WAITING)
        
    def get_routine(self, routine_name: str) -> Optional[Routine]:
        logger.info(f"Routine Manager: get routine {routine_name}")
        for routine in self.routines:
            if routine.name == routine_name:
                logger.info(f"Routine Manager: Routine found: {routine_name}")
                return routine
        logger.info(f"Routine Manager: Routine '{routine_name}' not found")
        return None
    
    async def main_coroutine(self):
        """
        The main coroutine of the RoutineManager class.
        This coroutine is responsible for updating the status of routines and handling new commands.
        It runs in an infinite loop, periodically checking the status of routines and processing new commands.
        """
        logger.info("Routine Manager: Main coroutine")
        # try:
        while True:
            logger.info("Routine Manager: Main coroutine loop")

            for routine in self.routines:
                logger.debug(f"Routine Manager {routine.name}: Update statuses")
                self.status_updater.routine_status_updater(routine.name, routine.status)
                self.status_updater.task_status_updater(routine.name, routine.task.status, routine.task.id)

                logger.debug(f"Routine status: {routine.name}: step ")
                await routine.step()

            logger.info("Routine Manager: Get commands")
            command = get_latest_pending_command()
            logger.info(f"command : {command}")
            if command is None:
                logger.info("No new command")
                await asyncio.sleep(TIME_TO_SLEEP)
                logger.info("done sleeping")
                continue

            if command.routine not in [routine.name for routine in self.routines]:
                logger.warning(f"fail to find routine: {command.routine} in routines: {[routine.name for routine in self.routines]}")
                update_command_status(command, CommandStatus.ERROR_UNKNOWN_ROUTINE)

            logger.info(f"Routine Manager: {command.routine}, {command.command}")
            routine = self.get_routine(command.routine)
            # Handle unknown routine or command
            if routine is None:
                logger.error(f"Unknown routine or command: {command.routine}, {command.command}")
                update_command_status(command, CommandStatus.DONE)
                logger.error("Task done")
                continue

            # Handle the command
            update_command_status(command, CommandStatus.RUNNING)
            if command.command == "start":
                logger.info(f"Starting routine: {command.routine}")
                await routine.start()
                                    
            elif command.command == "cancel":
                logger.info(f"Cancelling routine: {command.routine}")
                await routine.cancel()

            elif command.command == "execute":
                logger.info(f"Executing routine: {command.routine}")
                await routine.execute()
                
            else:
                logger.warning(f"Unknown command: {command.command}")

            update_command_status(command, CommandStatus.DONE)
