from RoutineManager import Routine, Task
from Routines.resources.Stocks import init_db

stocks_db_init_routine = Routine(
    name="initiate_stocks_db",
    description="This routine initiates the stocks database. Should run only once.",
    task=Task("initiate_stocks_db_task", init_db),
    interval=5,
    condition_function=lambda: True,
    retry_delay=60,
    retry_limit=5,
    run_once=True,
    timeout_limit=60*60*24,
)