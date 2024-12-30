from RoutineManager import Routine, Task, Trigger
from Routines.resources.Articles import init_db


article_db_init_routine = Routine(
    name="initiate_db",
    description="This routine initiates the articles database. Should run only once.",
    task=Task("initiate_db", init_db),
    interval=5,
    trigger=Trigger(
        name="initiate_db_trigger",
        function=lambda: True
    ),
    retry_delay=60,
    retry_limit=5,
    run_once=True
)