from RoutineManager import Routine, Task, Trigger
import time
import random

trigger=Trigger("test_trigger", lambda: True if random.randint(0, 1) == 1 else False)
dummy_task = Task("test_routine", lambda: True if random.randint(0, 1) == 1 else False)

test_routine = Routine(
    name="test_routine",
    description="This is a test routine",
    task=dummy_task,
    trigger=trigger,
    interval=5,
    retry_delay=30,
    retry_limit=5
)