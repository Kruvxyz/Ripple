from RoutineManager import Routine, Task
from .resources.Stocks.Stock import StockPrice
from .resources.Stocks import get_stocks_list, add_stock_price
from .resources.Stocks.yfinance_functions import is_market_open, get_price
import logging

logger = logging.getLogger(__name__)


def get_stocks_price_task() -> bool:
    stocks = get_stocks_list()
    try:
        for stock in stocks:
            price = get_price(stock.symbol).get("price", None)
            if price:
                add_stock_price(stock.symbol, price)
                logger.info(f"Stock price added for {stock.symbol} with price {price}")
            else:
                logger.error(f"Error getting stock price for {stock.symbol}")

    except Exception as e:
        logger.error(f"Error getting stock price with error: {e}")
        return False
    
    return True

stocks_price_routine = Routine(
    name="Stocks Price",
    description="Get the price of all stocks in the database",
    condition_function=is_market_open,
    task=Task("stocks price task", get_stocks_price_task),
)