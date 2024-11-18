from datetime import datetime
import asyncio
import time
import threading
from collections.abc import Callable
# from Routine import Routine
# from routines.system.routines_managment import gen_routines_managment_routine
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


# @singleton
# class RoutineManagerQueue:
#     """
#     The RoutineManagerQueue class is responsible for managing the queue of routines.
#     """
#     def __init__(self) -> None:
#         self.queue = asyncio.Queue()

    # @classmethod
    # async def put(cls, request) -> bool:
    #     command = request(1)
    #     if command not in ["start", "stop", "execute"]:
    #         raise ValueError("Invalid command")
    #     await cls.queue.put(request)
    #     return True

    # @classmethod
    # async def get(cls) -> Dict[str, Any]:
    #     return await cls.queue.get()
    
    # @classmethod
    # async def task_done(cls) -> None:
    #     await cls.queue.task_done()

    # @classmethod
    # async def join(cls) -> None:
    #     await cls.queue.join()


@singleton
class RoutineManager:
    """
    The RoutineManager class is responsible for managing routines. 
    It provides functionality to start, stop, restart, and check the status of routines. 
    Additionally, it serves as an interface for users to add new routines and interact with existing ones.
    """
    def __init__(self, *args, **kwargs):
        self.queue = asyncio.Queue()

        self.routines = []
        # self.routines_map_threads = {} 
        self.routines_map_tasks = {}
        self.routines_map_last_update = {}
        self.routines_map_status = {}
        self.routines_map_last_error = {}
        # self.routines_map_kill_switch = {}
        # self.routines_map_interval = {}
        # self.routines_next_check = {}

        # self.add_system_routines_managment() #FIXME: temporarily disabled

    # FIXME: temporarily disabled
    # def add_system_routines_managment(self):
    #     routines_managment_routine = gen_routines_managment_routine(self.routines_map_threads, self.routines_map_status)
    #     routines_managment_routine_name = routines_managment_routine.name
    #     routines_managment_routine.set_handlers(self.gen_update_routine_status(routines_managment_routine_name), self.gen_update_routine_error(routines_managment_routine_name))
    #     self.routines.append(routines_managment_routine)

    def gen_update_routine_status(self, routine_name: str) -> Callable[[str], bool]:
        def update_routine_status(status: str) -> bool:
            print(f"Updating routine status for {routine_name} to {status}")
            self.routines_map_status[routine_name] = status
            self.routines_map_last_update[routine_name] = self.now()
            return True
        return update_routine_status
    
    def gen_update_routine_error(self, routine_name: str) -> Callable[[str], bool]:
        def update_routine_error(error: str) -> bool:
            self.routines_map_last_error[routine_name] = error
            self.routines_map_last_update[routine_name] = self.now()
            return True
        return update_routine_error
    
    # FIXME: disabled
    # def gen_kill_switch(self, routine_name: str) -> Callable[[], bool]:
    #     def kill_switch() -> bool:
    #         print(f"Checking kill switch for {routine_name}")
    #         return self.routines_map_kill_switch.get(routine_name, False)
    #     return kill_switch

    # FIXME: temporarily disabled         
    # def add_routine(self, routine: Routine):
    #     # check routine name is unique
    #     for r in self.routines:
    #         if r.name == routine.name:
    #             raise Exception(f"Routine with name {routine.name} already exists")
        
    #     routine.set_handlers(self.gen_update_routine_status(routine.name), self.gen_update_routine_error(routine.name), self.gen_kill_switch(routine.name))
    #     self.routines.append(routine)

    def restart_routine(self, routine_name: str):
        # for routine in self.routines:
            # if routine.name == routine_name:
        # Terminate the thread
        self.routines_map_threads[routine_name].terminate()
        
        # Start the thread
        self.routines_map_threads[routine_name] = threading.Thread(target=self.routines_map_threads[routine_name].run)
        self.routines_map_threads[routine_name].start()
        

    def get_routine(self, routine_name: str):
        for routine in self.routines:
            if routine.name == routine_name:
                return routine
        return None
    
    async def cancle_routine(self, routine_name: str):
        logger.info(f"Cancelling routine: {routine_name} : called")
        self.routines_map_status[routine_name] = "Cancelling"
        self.routines_map_last_update[routine_name] = self.now()
        self.routines_map_last_error[routine_name] = ""

        logger.info(f"Cancelling routine: {routine_name} : get task")
        task = self.routines_map_tasks.get(routine_name, None)
        # Safely cancel the task
        if task is not None:
            logger.info(f"Cancelling task: {routine_name} : {task}")
            try:
                task.cancel()
                logger.info(f"Task cancelled: {routine_name}")
                await task
                logger.info(f"Task cancelled completed: {routine_name}")
                self.routines_map_tasks[routine_name] = None
                logger.info(f"Task set to None: {routine_name}")
            # except asyncio.CancelledError:
            #     logger.info(f"Task cancelled: {routine_name}")
            except Exception as e:
                logger.error(f"Error cancelling task: {routine_name} : {str(e)}")

    async def run_routine(self, routine):  #: Routine):
        logger.info(f"Running routine: {routine.name}")

        # Cancel the routine if it is already running
        await self.cancle_routine(routine.name)

        # Start the routine as a async task
        logger.info(f"Initiate task: {routine.name}")
        self.routines_map_tasks[routine.name] = asyncio.create_task(routine.run())
        logger.info(f"Task initiated: {routine.name}")

        # Update the status
        self.routines_map_status[routine.name] = "Initiating"
        self.routines_map_last_update[routine.name] = self.now()
        self.routines_map_last_error[routine.name] = ""
        logger.info(f"Routine initiated: {routine.name}")
    
    async def main_coroutine(self):
        while True:
            routine_name, command = await self.queue.get()
            logger.info(f"Routine Manager: {routine_name}, {command}")
            routine = self.get_routine(routine_name)

            # Handle unknown routine or command
            if routine is None or command not in ["start", "stop", "execute"]:
                logger.error(f"Unknown routine or command: {routine_name}, {command}")
                await self.queue.task_done()
                logger.error("Task done")
                continue

            # Handle the command
            if command == "start" or command == "restart":
                logger.info(f"Starting routine: {routine_name}")
                await self.run_routine(routine)
                                    
            elif command == "cancle":
                logger.info(f"Cancelling routine: {routine_name}")
                await self.cancle_routine(routine_name)

            # TODO: Implement execute command
            # elif command == "execute":
            #     logger.info(f"Executing routine: {routine_name}")
            #     await self.cancle_routine(routine_name)
            #     self.routines_map_tasks[routine_name] = asyncio.create_task(routine.execute())
                
            else:
                logger.error(f"Unknown command: {command}")

            self.queue.task_done()

    async def start_routine(self, routine_name: str) -> asyncio.Task:
        self.routines_map_threads[routine_name] = threading.Thread(target=self.routines_map_threads[routine_name].run)
        self.routines_map_threads[routine_name].start()
        self.routines_map_last_update[routine_name] = self.now()


    async def start(self):
        logger.info("Routine Manager started")

        # Start the routines
        logger.info("Starting routines")
        for routine in self.routines:
            logger.info(f"Starting routine: {routine.name}")
            await self.run_routine(routine)
            logger.info(f"Routine started: {routine.name}")

        # Start the main coroutine
        logger.info("Starting main coroutine")
        await self.main_coroutine()
        # await self.run()

    # def start(self):
    #     print("------------------Routine Manager started----------------")
    #     for routine in self.routines:
    #         self.routines_map_status[routine.name] = "Initiating"
    #         try:
    #             self.routines_map_threads[routine.name] = threading.Thread(target=routine.run)
    #             self.routines_map_threads[routine.name].start()
    #             self.routines_map_last_error[routine.name] = ""
    #         except Exception as e:
    #             self.routines_map_status[routine.name] = "Initiating Failed"
    #             self.routines_map_last_error[routine.name] = str(e)
    #         self.routines_map_last_update[routine.name] = self.now()

    async def awaitstop_routine(self, routine_name: str) -> bool:
        #FIXME: should add a graceful stop
        self.routines_map_kill_switch[routine_name] = True
        return True

    def get_routine_status(self, routine_name: str):
        return {
            "status": self.routines_map_status.get(routine_name, None),
            "last_update": self.routines_map_last_update.get(routine_name, None),
            "last_error": self.routines_map_last_error.get(routine_name, None),
        }
    
    def now(self):
        return datetime.fromtimestamp(time.time())
    
    async def run(self):
        print("------------------Routine Manager started----------------")
        while True:
            print("Running")
            await asyncio.sleep(1)


# PUSH COMMANDS
    def put_nowait(self, request) -> bool:
        command = request(1)
        if command not in ["start", "stop", "execute"]:
            raise ValueError("Invalid command")
        self.queue.put_nowait(request)
        return True
    
    async def put(self, request) -> bool:
        command = request(1)
        if command not in ["start", "stop", "execute"]:
            raise ValueError("Invalid command")
        await self.queue.put(request)
        return True

    async def get(self) -> Dict[str, Any]:
        return await self.queue.get()
    
    # async def task_done(self) -> None:
    #     await self.queue.task_done()

    # async def join(self) -> None:
    #     await self.queue.join()