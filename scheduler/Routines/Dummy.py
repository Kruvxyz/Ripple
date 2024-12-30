from RoutineManager import Routine, Task, Trigger
import time
import random

def dummy_task():
    time.sleep(30)
    return True

dummy_task = Task("dummy", dummy_task)
trigger = Trigger("dummy", lambda: True if random.randint(0, 1) == 1 else False)
dummy_routine = Routine(
    name="dummy",
    description="This is a dummy routine",
    task=dummy_task,
    interval=5,
    trigger=trigger,
    retry_delay=60,
    retry_limit=5
)