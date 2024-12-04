from RoutineManager import Routine, Task
from .resources.Stocks.yfinance_functions import is_traded_today, get_recommendations, get_stock_daily, get_stock_data
from .resources.Stocks import add_stock_summary, is_stock_updated_today, get_stocks_list
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def get_current_time_in_et():
    # Get current UTC time
    utc_now = datetime.now(timezone.utc)

    # Define offsets
    est_offset = timedelta(hours=-5)  # Standard Time (UTC-5)
    edt_offset = timedelta(hours=-4)  # Daylight Saving Time (UTC-4)

    # Define the start and end dates for DST in 2024
    # DST in the US: Second Sunday in March to the first Sunday in November
    dst_start = datetime(2024, 3, 10, 2, 0, tzinfo=timezone.utc)
    dst_end = datetime(2024, 11, 3, 2, 0, tzinfo=timezone.utc)

    # Determine whether it's DST or standard time
    if dst_start <= utc_now < dst_end:
        et = timezone(edt_offset)  # EDT (UTC-4)
    else:
        et = timezone(est_offset)  # EST (UTC-5)

    # Convert current UTC time to ET
    et_now = utc_now.astimezone(et)
    return et_now

def trigger() -> bool:
    now = get_current_time_in_et()
    market_close_time_start = now.replace(hour=16, minute=0, second=0, microsecond=0)
    market_close_time_end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now.strftime('%A') in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        if market_close_time_start <= now < market_close_time_end:
            all_stocks = get_stocks_list()
            logger.debug(f"StocksDaily | Checking if stocks are updated for {len(all_stocks)} stocks")
            for stock in all_stocks:
                if not is_stock_updated_today(stock.symbol):
                    logger.info("StocksDaily | triggered")
                    return True
            
    logger.info("StocksDaily | not triggered")
    return False

def task() -> bool:
    all_stocks = get_stocks_list()
    for stock in all_stocks:
        try:
            if not is_stock_updated_today(stock.symbol) and is_traded_today(stock.symbol):
                recommendations = get_recommendations(stock.symbol).get("recommendations", {})
                stock_daily = get_stock_daily(stock.symbol)
                stock_daily_date = get_stock_data(stock.symbol)
                add_stock_summary(
                    stock.symbol, 
                    datetime.now(),
                    p_to_e_ratio=stock_daily_date.get("p_to_e_ratio", None),
                    market_cap=stock_daily_date.get("market_cap", None),
                    open_price=stock_daily.get("open", None),
                    close_price=stock_daily.get("close", None),
                    high_price=stock_daily.get("high", None),
                    low_price=stock_daily.get("low", None),
                    recommendations_strong_buy=recommendations.get("strongBuy", None),
                    recommendations_buy=recommendations.get("buy", None),
                    recommendations_sell=recommendations.get("sell", None),
                    recommendations_hold=recommendations.get("hold", None),
                    recommendations_strong_sell=recommendations.get("strongSell", None),
                    total_recommendations=recommendations.get("total_recommendations", None)
                )
                logger.info(f"Stock summary added for {stock.symbol}: {datetime.now()}")
            else:
                logger.info(f"Stock summary already added for {stock.symbol}: {datetime.now()}")
        except Exception as e:
            logger.error(f"Error adding stock summary for {stock.symbol} with error: {e}")

    return True

stocks_daily_routine = Routine(
    name="Stocks_Daily_Summary",
    description="Update the daily summary for all stocks",
    condition_function=trigger,
    task=Task("Stocks_Daily_Summary_Task", task),
)