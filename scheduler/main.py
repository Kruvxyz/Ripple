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
    from Routines import article_db_init_routine, ynet_routine, walla_routine, cnn_routine
    routine_manager.add_routine(article_db_init_routine)
    routine_manager.add_routine(ynet_routine)
    routine_manager.add_routine(walla_routine)
    routine_manager.add_routine(cnn_routine)
    # BBC
    from Routines import bbc_news_routine, bbc_world_routine, bbc_UK_routine, bbc_business_routine, bbc_politics_routine, bbc_health_routine, bbc_education_routine, bbc_science_and_environment_routine, bbc_technology_routine, bbc_entertainment_and_arts_routine, bbc_africa_routine, bbc_asia_routine, bbc_europe_routine, bbc_latin_america_routine, bbc_middle_east_routine, bbc_us_and_canada_routine, bbc_england_routine, bbc_northern_ireland_routine, bbc_scotland_routine, bbc_wales_routine
    routine_manager.add_routine(bbc_news_routine)
    routine_manager.add_routine(bbc_world_routine)
    routine_manager.add_routine(bbc_UK_routine)
    routine_manager.add_routine(bbc_business_routine)
    routine_manager.add_routine(bbc_politics_routine)
    routine_manager.add_routine(bbc_health_routine)
    routine_manager.add_routine(bbc_education_routine)
    routine_manager.add_routine(bbc_science_and_environment_routine)
    routine_manager.add_routine(bbc_technology_routine)
    routine_manager.add_routine(bbc_entertainment_and_arts_routine)
    routine_manager.add_routine(bbc_africa_routine)
    routine_manager.add_routine(bbc_asia_routine)
    routine_manager.add_routine(bbc_europe_routine)
    routine_manager.add_routine(bbc_latin_america_routine)
    routine_manager.add_routine(bbc_middle_east_routine)
    routine_manager.add_routine(bbc_us_and_canada_routine)
    routine_manager.add_routine(bbc_england_routine)
    routine_manager.add_routine(bbc_northern_ireland_routine)
    routine_manager.add_routine(bbc_scotland_routine)
    routine_manager.add_routine(bbc_wales_routine)
    # Skynews
    from Routines import skynews_home_routine, skynews_UK_routine, skynews_world_routine, skynews_US_routine, skynews_business_routine, skynews_politics_routine, skynews_technology_routine, skynews_entertainment_routine, skynews_strange_routine
    routine_manager.add_routine(skynews_home_routine)
    routine_manager.add_routine(skynews_UK_routine)
    routine_manager.add_routine(skynews_world_routine)
    routine_manager.add_routine(skynews_US_routine)
    routine_manager.add_routine(skynews_business_routine)
    routine_manager.add_routine(skynews_politics_routine)
    routine_manager.add_routine(skynews_technology_routine)
    routine_manager.add_routine(skynews_entertainment_routine)
    routine_manager.add_routine(skynews_strange_routine)

    # Stocks
    from Routines import stocks_db_init_routine, stocks_price_routine, stocks_daily_routine, stocks_earnings_routine
    # routine_manager.add_routine(stocks_db_init_routine) # Blocking routine
    routine_manager.add_routine(stocks_price_routine)
    routine_manager.add_routine(stocks_daily_routine)
    routine_manager.add_routine(stocks_earnings_routine)

    logger.info("Starting RoutineManager")
    asyncio.run(routine_manager.main_coroutine())