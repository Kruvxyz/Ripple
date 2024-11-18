from typing import Dict
from Routine import Routine

def gen_routines_managment_routine(routines: Dict[str, Routine], routines_status_handler: Dict[str, str]) -> Routine:
    def routines_managment_function() -> bool:
        print("Checking if threads are alive")
        print(routines)
        try:
            for routine_name, routine in routines.items():
                print(f"{routine_name} is alive: {routine.is_alive()}")
                if not routine.is_alive():
                    routines_status_handler[routine_name] = "Dead"
        except Exception as e:
            print(f"Error in routine managment function: {e}")
            return False
        print("done checking routines")
        return True
    
    return Routine(
        "Routines_Managment", 
        "This routine verify that routines are alive and report if not.",
        routines_managment_function,
        60 # 1 minute
    )