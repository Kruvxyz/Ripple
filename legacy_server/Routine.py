from collections.abc import Callable
from typing import Optional
import time


class Routine:
    def __init__(
            self, 
            name: str, 
            description: str, 
            function: Callable[[], bool], 
            interval: int, 
            condition_function:Optional[Callable[[], bool]]=None,
            condition_interval: int=5*60, # 5 minutes
            retry_delay: int=5*60, # 5 minutes
            retry_limit: int=5
        ) -> None:
        self.name = name
        self.description = description
        self.function = function
        self.interval = interval
        self.condition_function = condition_function
        self.condition_interval = condition_interval
        self.retry_delay = retry_delay
        self.retry_limit = retry_limit

        # Handlers
        self.update_status_function = None
        self.update_error_function = None
        self.kill_switch = None

        # State
        self.num_retries = 0

    def set_handlers(
            self, 
            update_status_function: Callable[[str], bool], 
            update_error_function: Callable[[str], bool], 
            kill_switch: Optional[Callable[[], bool]] = None
        ) -> None:
        self.update_status_function = update_status_function
        self.update_error_function = update_error_function
        self.kill_switch = kill_switch

    def run(self):
        print(f"------------------{self.name}: Routine started----------------")
        self.update_status_function("Routine started")
        self.update_error_function("")
        
        while self.num_retries < self.retry_limit:
            if self.kill_switch is not None:
                if self.kill_switch():
                    print(f"-----------{self.name}: KILL SWITCH ACTIVATED -----------")
                    self.update_status_function("Kill switch activated")
                    break

            if self.condition_function is not None:
                if not self.condition_function():
                    print(f"-----------{self.name}: CONDITION FUNCTION FAILURE -----------")
                    self.update_status_function("waiting")
                    time.sleep(self.condition_interval)
                    continue

            try:
                print(f"-----------{self.name}: RUNNING FUNCTION-----------")
                self.update_status_function("running")
                function_status = self.function()
                if not function_status:
                    self.update_failure("Fail to run function")
                    time.sleep(self.retry_delay)
                    continue

            except Exception as e:
                self.update_failure(f"Error running function with error: {e}")
                time.sleep(self.retry_delay)
                continue

            print(f"-----------{self.name}: RUN SUCCESSFULL-----------")

            self.update_status_function("Function ran successfully")
            self.update_error_function("")

            # Reset the number of retries
            self.num_retries = 0

            # Wait for the interval
            time.sleep(self.interval)

        self.update_status_function("Routine finished")
        self.update_error_function("Retry limit reached for the routine")

    def update_failure(self, error: str):
        print(f"-----------{self.name}: FAILURE-----------")
        self.update_error_function(error)
        self.update_status_function("Failed to run function")
        self.num_retries += 1