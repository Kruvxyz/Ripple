from Routine import Routine

def gen_user_interface_manager_routine() -> Routine:
    def user_interface_manager_function() -> bool:
        print("User Interface Manager")
        # read new inputs from user
        # 
        # generate new tasks
        # 
        # send an update to user
        # 

        return True
    
    return Routine(
        "User_Interface_Manager", 
        "This routine manage the user interface.",
        user_interface_manager_function,
        1 # 1 minute
    )