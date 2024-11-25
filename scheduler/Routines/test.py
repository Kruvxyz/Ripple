from RoutineManager import Routine, Task
import time
import random

def dummy_task():
    time.sleep(30)
    return True if random.randint(0, 1) == 1 else False

dummy_task = Task("test_routine", dummy_task)
test_routine = Routine(
    name="test_routine",
    description="This is a test routine",
    task=dummy_task,
    interval=5,
    condition_function=lambda: True if random.randint(0, 1) == 1 else False,
    retry_delay=30,
    retry_limit=5
)