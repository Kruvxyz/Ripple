import asyncio
import logging
import sys
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

    from Routines import dummy_routine, test_routine, db_init_routine, ynet_routine

    routine_manager.add_routine(db_init_routine)
    routine_manager.add_routine(ynet_routine)
    routine_manager.add_routine(dummy_routine)
    routine_manager.add_routine(test_routine)

    logger.info("Starting RoutineManager")
    asyncio.run(routine_manager.start())