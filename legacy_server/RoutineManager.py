from datetime import datetime
import time
import threading
from collections.abc import Callable
from Routine import Routine
from routines.system.routines_managment import gen_routines_managment_routine

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class RoutineManager:
    def __init__(self):
        
        self.routines = []
        self.routines_map_threads = {} 
        self.routines_map_last_update = {}
        self.routines_map_status = {}
        self.routines_map_last_error = {}
        self.routines_map_kill_switch = {}
        # self.routines_map_interval = {}
        # self.routines_next_check = {}

        self.add_system_routines_managment()

    def add_system_routines_managment(self):
        routines_managment_routine = gen_routines_managment_routine(self.routines_map_threads, self.routines_map_status)
        routines_managment_routine_name = routines_managment_routine.name
        routines_managment_routine.set_handlers(self.gen_update_routine_status(routines_managment_routine_name), self.gen_update_routine_error(routines_managment_routine_name))
        self.routines.append(routines_managment_routine)

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
    
    def gen_kill_switch(self, routine_name: str) -> Callable[[], bool]:
        def kill_switch() -> bool:
            print(f"Checking kill switch for {routine_name}")
            return self.routines_map_kill_switch.get(routine_name, False)
        return kill_switch
         
    def add_routine(self, routine: Routine):
        # check routine name is unique
        for r in self.routines:
            if r.name == routine.name:
                raise Exception(f"Routine with name {routine.name} already exists")
        
        routine.set_handlers(self.gen_update_routine_status(routine.name), self.gen_update_routine_error(routine.name), self.gen_kill_switch(routine.name))
        self.routines.append(routine)

    def restart_routine(self, routine_name: str):
        # for routine in self.routines:
            # if routine.name == routine_name:
        # Terminate the thread
        self.routines_map_threads[routine_name].terminate()
        
        # Start the thread
        self.routines_map_threads[routine_name] = threading.Thread(target=self.routines_map_threads[routine_name].run)
        self.routines_map_threads[routine_name].start()
        

    def start(self):
        print("------------------Routine Manager started----------------")
        for routine in self.routines:
            self.routines_map_status[routine.name] = "Initiating"
            try:
                self.routines_map_threads[routine.name] = threading.Thread(target=routine.run)
                self.routines_map_threads[routine.name].start()
                self.routines_map_last_error[routine.name] = ""
            except Exception as e:
                self.routines_map_status[routine.name] = "Initiating Failed"
                self.routines_map_last_error[routine.name] = str(e)
            self.routines_map_last_update[routine.name] = self.now()

    def stop_routine(self, routine_name: str) -> bool:
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