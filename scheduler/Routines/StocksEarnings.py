from RoutineManager import Routine, Task, Trigger
from .resources.Stocks.yfinance_functions import get_last_earnings
from .resources.Stocks import add_stock_earnings, get_stock_last_earning_date, get_stocks_list, Stock
import asyncio
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def is_stock_updated_to_date(symbol: str, latest_earning_date: datetime) -> bool:
    last_earning = get_stock_last_earning_date(symbol)
    if last_earning is None:
        return False
    else:
        last_earning_date = last_earning[0]
        return last_earning_date.date() == latest_earning_date.date()

def stock_trigger(stock: Stock, now: datetime) -> bool:
    last_earnings_raw = get_last_earnings(stock.symbol)
    last_earnings = last_earnings_raw.get("date", None)
    logger.debug(f"StocksEarnings | Checking if stocks are updated for {stock.symbol} with last earnings {last_earnings_raw}")
    if not last_earnings_raw.get("success", False) or last_earnings is None:
        logger.warning(f"Failed getting last earnings for stock with symbol {stock.symbol}")
        return False
    if now.date() >= last_earnings.date() and  last_earnings.date() + timedelta(days=3) >= now.date() :
        logger.debug(f"StocksEarnings | triggered for {stock.symbol}")
        if not is_stock_updated_to_date(stock.symbol, last_earnings):
            logger.info("StocksEarnings | triggered")
            return True
        
async def trigger_earnings() -> bool:
    now = datetime.now(timezone.utc)
    stocks_list = get_stocks_list()
    for stock in stocks_list:
        if await asyncio.to_thread(stock_trigger(stock, now)):
            return True
    logger.info("StocksEarnings | not triggered")
    return False

def stock_earnings(stock: Stock) -> None:
    try:
        last_earnings = get_last_earnings(stock.symbol)
        last_earnings_date = last_earnings.get("date", None)
        last_earnings_eps = last_earnings.get("eps", None)
        last_earnings_revenue = last_earnings.get("revenue", None)
        if last_earnings_date is None:
            logger.warning(f"Error getting last earnings for stock with symbol {stock.symbol}")
            return 
        if not is_stock_updated_to_date(stock.symbol, last_earnings_date):
            add_stock_earnings(
                stock.symbol, 
                last_earnings_date,
                last_earnings_eps,
                last_earnings_revenue,
                True
            )
            logger.debug(f"Stock earnings added for {stock.symbol} with date {last_earnings}")

    except Exception as e:
        logger.error(f"Error adding stock earnings with symbol {stock.symbol} with error: {e}")

async def task_earnings() -> bool:
    stocks_list = get_stocks_list()
    for stock in stocks_list:
        await asyncio.to_thread(stock_earnings(stock))
    return True

stocks_earnings_routine = Routine(
    name="Stocks_Earnings",
    description="Update the earnings for all stocks",
    task=Task("Stocks_Earnings_Task", async_function=task_earnings),
    trigger=Trigger("Stocks_Earnings_Trigger", async_function=trigger_earnings),
    interval=60*60*24
)