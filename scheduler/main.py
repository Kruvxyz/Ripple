import asyncio
import logging
import sys
from RoutineManager.RoutineManager import RoutineManager
from RoutineManager.Routine import Routine
from RoutineManager.Task import Task

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
    logger.info("Starting RoutineManager")
    routine_manager = RoutineManager()

    logger.info("Adding routines to RoutineManager")

    # Dummy
    from Routines import dummy_routine, test_routine
    routine_manager.add_routine(dummy_routine)
    routine_manager.add_routine(test_routine)

    # Articles
    from Routines import article_db_init_routine, ynet_routine, walla_routine, cnn_routine, bbc_routine
    routine_manager.add_routine(article_db_init_routine)
    routine_manager.add_routine(ynet_routine)
    routine_manager.add_routine(walla_routine)
    routine_manager.add_routine(cnn_routine)
    routine_manager.add_routine(bbc_routine)

    # Stocks
    from Routines import stocks_db_init_routine, stocks_price_routine, stocks_daily_routine, stocks_earnings_routine
    # routine_manager.add_routine(stocks_db_init_routine) # Blocking routine
    routine_manager.add_routine(stocks_price_routine)
    routine_manager.add_routine(stocks_daily_routine)
    routine_manager.add_routine(stocks_earnings_routine)

    logger.info("Starting RoutineManager")
    asyncio.run(routine_manager.main_coroutine())