from RoutineManager import Routine, Task
import time
import random

dummy_task = Task(lambda: time.sleep(30))
test_routine = Routine(
    name="test_routine",
    description="This is a test routine",
    task=dummy_task,
    interval=5,
    condition_function=lambda: True if random.randint(0, 1) == 1 else False,
    retry_delay=5*60,
    retry_limit=5
)