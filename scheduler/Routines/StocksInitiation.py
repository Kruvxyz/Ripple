import asyncio
from RoutineManager import Routine, Task, Trigger
from Routines.resources.Stocks import init_db

async def async_task() -> bool:
    return await asyncio.to_thread(init_db())

stocks_db_init_routine = Routine(
    name="initiate_stocks_db",
    description="This routine initiates the stocks database. Should run only once.",
    task=Task("initiate_stocks_db_task", async_function=async_task),
    interval=5,
    trigger=Trigger(
        name="initiate_stocks_db_trigger",
        function=lambda: True
    ),
    retry_delay=60,
    retry_limit=5,
    run_once=True,
    timeout_limit=60*60*24,
)