import asyncio
from collections.abc import Callable
from shared import session, Message, get_latest_pending_command, update_routine_status, update_command_status, get_routine_status, update_task_status, get_task
# from Routine import Routine
# from routines.system.routines_managment import gen_routines_managment_routine
import logging
from typing import Any, Dict, Optional, List
from db import init_db
from .Routine import Routine
from .Status import RoutineStatus

logger = logging.getLogger(__name__)

TIME_TO_SLEEP = 1 # 1 second

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
        # self.add_system_routines_managment() #FIXME: temporarily disabled

        init_db()

    # FIXME: temporarily disabled
    # def add_system_routines_managment(self):
    #     routines_managment_routine = gen_routines_managment_routine(self.routines_map_threads, self.routines_map_status)
    #     routines_managment_routine_name = routines_managment_routine.name
    #     routines_managment_routine.set_handlers(self.gen_update_routine_status(routines_managment_routine_name), self.gen_update_routine_error(routines_managment_routine_name))
    #     self.routines.append(routines_managment_routine)

    def update_routine_status(self, routine_name: str, status: RoutineStatus, error: Optional[str] = None) -> bool:
        # TODO: allowed statuses
        # if status not in [RoutineStatus.PENDING, RoutineStatus.WAITING, RoutineStatus.CANCELED, RoutineStatus.RUNNING, RoutineStatus.STARTING, ]: # allowed status
        #     logger.error(f"Invalid status: {status} for routine: {routine_name}")
        #     return False
        logger.info(f"Updating routine status for {routine_name} to {status}")
        return update_routine_status(routine_name, status, error) # update DB
    
    # not in use - review if needed
    def update_routine_error(self, routine_name: str, error: str) -> bool:
        logger.info(f"Updating routine error for {routine_name} to {error}")
        return update_routine_status(routine_name, RoutineStatus.ERROR, error) # update DB

    # WORK IN PROGRESS    
    # def update_task_status(self, routine_name: str, task_id: int, status: str, error: Optional[str] = None) -> bool:
    #     logger.info(f"Updating task status for {routine_name} to {status}")
    #     return update_routine_status(routine_name, status, error)
    
    def add_routine(self, routine: Routine) -> bool:
        # check routine name is unique
        existed_routine = self.get_routine(routine.name)
        if existed_routine is not None:
            logger.error(f"Routine with name {routine.name} already exists")
            return False
        
        self.routines.append(routine)
        logger.info(f"self.routines: {self.routines}")
        return self.update_routine_status(routine.name, RoutineStatus.PENDING)
        
    def get_routine(self, routine_name: str) -> Optional[Routine]:
        logger.info(f"Routine Manager: get routine {routine_name}")
        for routine in self.routines:
            if routine.name == routine_name:
                logger.info(f"Routine Manager: Routine found: {routine_name}")
                return routine
        logger.info(f"Routine Manager: Routine '{routine_name}' not found")
        return None
    
    # TODO: complete the implementation
    # What is there to do for completion?
    async def cancel_routine(self, routine_name: str) -> None:
        logger.info(f"Cancelling routine: {routine_name} : called")
        routine_task = self.routines_map_tasks.get(routine_name, None)
        # Safely cancel the task
        if routine_task is not None:
            logger.info(f"Cancelling routine: {routine_name} : {routine_task}")
            try:
                routine_task.cancel()
                logger.info(f"rouine({routine_name}).cancel()")
                await routine_task
                logger.info(f"rouine({routine_name}).await()")
                self.routines_map_tasks[routine_name] = None
                self.update_routine_status(routine_name, RoutineStatus.CANCELED)

            except Exception as e:
                logger.error(f"Failed to cancel routine: {routine_name} with error: {e}")
                # self.update_routine_status(
                #     routine_name, 
                #     RoutineStatus.UNKNOWN, 
                #     error="Cancelling Failed with error: " + str(e)
                # )
        else:
            logger.error(f"Fail to retrive routine task: {routine_name} | self.routines_map_tasks: {self.routines_map_tasks}")
            # self.update_routine_error(routine_name, "Fail to retrive routine task")

    async def start_routine(self, routine_name: str):
        logger.info(f"Routine Manager: start routine {routine_name}")
        routine_task = self.routines_map_tasks.get(routine_name, None)
        if routine_task is not None:
            logger.error(f"Fail to start routine,Routine already running: {routine_name}")
            return
        
        routine = self.get_routine(routine_name)
        if routine is not None:
            self.update_routine_status(routine_name, RoutineStatus.STARTING)
            self.routines_map_tasks[routine_name] = asyncio.create_task(routine.run())
            self.update_routine_status(routine_name, RoutineStatus.RUNNING)

    async def restart_routine(self, routine_name: str): 
        logger.info(f"cancle routine: {routine_name}")
        await self.cancel_routine(routine_name)

        logger.info(f"Starting routine: {routine_name}")
        await self.start_routine(routine_name)

        logger.info(f"Routine started: {routine_name}")
    
    async def main_coroutine(self):
        """
        The main coroutine of the RoutineManager class.
        This coroutine is responsible for updating the status of routines and handling new commands.
        It runs in an infinite loop, periodically checking the status of routines and processing new commands.
        """
        logger.info("Routine Manager: Main coroutine")
        while True:
            logger.info("Routine Manager: Main coroutine loop")

            logger.info("Routine Manager: Push commands")
            for routine in self.routines:
                logger.info(f"Routine status: {routine.name}, {routine.get_status()} {get_routine_status(routine.name)}")
                if routine.get_status() != get_routine_status(routine.name):
                    logger.info(f"Routine status: {routine.name}, {routine.get_status()}")
                    self.update_routine_status(routine.name, routine.get_status(), routine.get_error())

                logger.info(f"Routine task status: {routine.name}, {routine.task.status}")
                routine_task_instance = routine.task.get_instance()
                logger.info(f"Routine task instance: {routine.name}, {routine_task_instance}")
                if routine_task_instance is not None:
                    last_task = get_task(routine.name, routine_task_instance.id)
                    latest_task_status = None if not last_task else last_task.status
                    if latest_task_status is None or latest_task_status != routine_task_instance.status:
                        logger.info(f"Task status update: {routine.name}, {routine_task_instance}")
                        update_task_status(routine.name, routine_task_instance.id, routine_task_instance.status, routine_task_instance.error)

            logger.info("Routine Manager: Get commands")
            command = get_latest_pending_command()
            logger.info(f"command : {command}")
            if command is None:
                logger.info("No new command")
                await asyncio.sleep(TIME_TO_SLEEP)
                continue

            if command.routine not in [routine.name for routine in self.routines]:
                logger.error(f"Failed", "Unknown routine")
                update_command_status(command, "Unknown routine")

            logger.info(f"Routine Manager: {command.routine}, {command.command}")
            routine = self.get_routine(command.routine)

            # Handle unknown routine or command
            if routine is None or command.command not in ["start", "cancel"]: #, "execute"]:
                logger.error(f"Unknown routine or command: {command.routine}, {command.command}")
                update_command_status(command, "Done")
                logger.error("Task done")
                continue

            # Handle the command
            update_command_status(command, "Running")
            if command.command == "start": # or command == "restart":
                logger.info(f"Starting routine: {command.routine}")
                await self.start_routine(command.routine)
                                    
            elif command.command == "cancel":
                logger.info(f"Cancelling routine: {command.routine}")
                await self.cancel_routine(command.routine)

            # TODO: Implement execute command
            # elif command == "execute":
            #     logger.info(f"Executing routine: {routine_name}")
            #     await self.cancel_routine(routine_name)
            #     self.routines_map_tasks[routine_name] = asyncio.create_task(routine.execute())
                
            else:
                logger.error(f"Unknown command: {command.command}")

            update_command_status(command, "Done")




    async def start(self):
        logger.info("Routine Manager: started")

        # Start the routines
        logger.info("Starting routines")
        for routine in self.routines:
            logger.info(f"Starting routine: {routine.name}")
            await self.start_routine(routine.name)
            logger.info(f"Routine started: {routine.name}")

        # Start the main coroutine
        logger.info("Starting main coroutine")
        await self.main_coroutine()

    

    # # FIXME: can be remove - was only for initial testing
    # async def run(self):
    #     print("------------------Routine Manager started----------------")
    #     while True:
    #         print("Running")
    #         await asyncio.sleep(1)

