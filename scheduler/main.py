import asyncio
import logging
import sys
import random
from RoutineManager.RoutineManager import RoutineManager
from RoutineManager.Routine import Routine
from RoutineManager.Task import Task
from shared import init_queue_db

# Set logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
    )

logger = logging.getLogger(__name__)
logger.info("Logger configured successfully")

if __name__ == "__main__":
    logger.info("Initializing DB")
    init_queue_db()

    logger.info("Starting RoutineManager")
    routine_manager = RoutineManager()

    logger.info("Adding routines to RoutineManager")

    # TODO: Add routines to the RoutineManager
    dummy_task = Task()
    test_routine = Routine(
        name="test_routine",
        description="This is a test routine",
        task=dummy_task,
        interval=5,
        condition_function=lambda: True if random.randint(0, 1) == 1 else False,
        condition_interval=5*60,
        retry_delay=5*60,
        retry_limit=5
    )
    routine_manager.add_routine(test_routine)

    logger.info("Starting RoutineManager")
    asyncio.run(routine_manager.start())