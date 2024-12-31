from typing import Any, Iterable, Optional
from RoutineManager import Routine, Task, Trigger
from Routines.resources.Stocks import add_stock_price, get_stocks_list, Stock
from Routines.resources.Stocks.yfinance_functions import is_market_open, get_price
import asyncio
import logging


logger = logging.getLogger(__name__)


def add_stock_function(stock: Stock) -> None:
    price = get_price(stock.symbol).get("price", None)
    if price:
        add_stock_price(stock.symbol, price)
        logger.debug(f"Stock price added for {stock.symbol} with price {price}")
    else:
        logger.error(f"Error getting stock price for {stock.symbol}")


async def get_stocks_price_task(stocks : Optional[Iterable[Any]] = None) -> bool:
    if stocks is None:
        stocks = get_stocks_list()
    try:
        for stock in stocks:
            await asyncio.to_thread(add_stock_function(stock))
    except Exception as e:
        logger.error(f"Error getting stock price with error: {e}")
        return False
    
    return True

stocks_price_routine = Routine(
    name="Stocks_Price",
    description="Get the price of all stocks in the database",
    task=Task("Stocks_Price_Task", async_function=get_stocks_price_task),
    trigger=Trigger("Stocks_Price_Trigger", is_market_open),
    timeout_limit=60*60*24,
)