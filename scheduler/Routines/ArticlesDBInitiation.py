from RoutineManager import Routine, Task
from .resources.Articles import init_db


article_db_init_routine = Routine(
    name="initiate_db",
    description="This routine initiates the articles database. Should run only once.",
    task=Task("initiate_db", init_db),
    interval=5,
    condition_function=lambda: True,
    retry_delay=60,
    retry_limit=5,
    run_once=True
)