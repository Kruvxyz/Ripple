from RoutineManager import Routine, Task
import time
import random

def dummy_task():
    time.sleep(30)
    return True

dummy_task = Task("dummy", dummy_task)
dummy_routine = Routine(
    name="dummy",
    description="This is a dummy routine",
    task=dummy_task,
    interval=5,
    condition_function=lambda: True if random.randint(0, 1) == 1 else False,
    retry_delay=60,
    retry_limit=5
)