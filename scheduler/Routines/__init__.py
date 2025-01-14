# Tests
from .Dummy import dummy_routine
from .test import test_routine  

# News
from .ArticlesDBInitiation import article_db_init_routine
from .ynet import ynet_routine
from .walla import walla_routine
from .cnn import cnn_routine
from .bbc import bbc_news_routine, bbc_world_routine, bbc_UK_routine, bbc_business_routine, bbc_politics_routine, bbc_health_routine, bbc_education_routine, bbc_science_and_environment_routine, bbc_technology_routine, bbc_entertainment_and_arts_routine, bbc_africa_routine, bbc_asia_routine, bbc_europe_routine, bbc_latin_america_routine, bbc_middle_east_routine, bbc_us_and_canada_routine, bbc_england_routine, bbc_northern_ireland_routine, bbc_scotland_routine, bbc_wales_routine
from .skynews import skynews_home_routine, skynews_UK_routine, skynews_world_routine, skynews_US_routine, skynews_business_routine, skynews_politics_routine, skynews_technology_routine, skynews_entertainment_routine, skynews_strange_routine

# Stocks
from .StocksInitiation import stocks_db_init_routine
from .StocksPrice import stocks_price_routine
from .StocksDaily import stocks_daily_routine
from .StocksEarnings import stocks_earnings_routine