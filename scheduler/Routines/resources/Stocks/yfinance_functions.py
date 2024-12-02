from datetime import datetime, timezone, timedelta
from typing import Any, Dict
import yfinance as yf


def get_stock_data(symbol: str) -> Dict[str, Dict[Any, Any]]:
    price = get_price(symbol).get("price", None)
    recommendations = get_recommendations(symbol).get("recommendations", None)
    return {
        "symbol": symbol,
        "price": price,
        "recommendations": recommendations
    }

def get_price(symbol: str) -> Dict[str, int]:
    stock = yf.Ticker(symbol)
    try:
        price = stock.fast_info.last_price
    except:
        price = None
    return {
        "price": price
    }

def get_recommendations(symbol: str) -> Dict[str, Dict[Any, Any]]:
    stock = yf.Ticker(symbol)
    try:
        recommendations = stock.recommendations.to_dict(orient="records")[0]
    except:
        recommendations = {}

    return {
        "recommendations": recommendations
    }

def get_stock_daily(symbol: str) -> Dict[str, Any]:
    stock = yf.Ticker(symbol)
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    yesterday = today - timedelta(days=1)
    # tomorrow = today + timedelta(days=1)
    return_data = {}
    try:
        data = stock.history(start=yesterday, end=today).iloc[-1,:]
        return_data = {
            "success": True,
            "open": data.Open,
            "high": data.High,
            "low": data.Low,
            "close": data.Close,
            "date": yesterday
        }
    except Exception as e:
        return_data = {
            "success": False,
            "error": str(e)
        }
    return return_data

def is_market_open():
    # Get stock data for a specific symbol (e.g., 'AAPL' for Apple)
    ticker_symbol = "AAPL"
    ticker = yf.Ticker(ticker_symbol)
    
    # Fetch the historical intraday data (1-minute interval)
    hist = ticker.history(period="1d", interval="1m")
    
    # Get the most recent entry
    last_trade_time = hist.index[-1]
    
    # Convert the last trade time to UTC for comparison
    last_trade_time_utc = last_trade_time.tz_convert(timezone.utc)
    
    # Get the current time in UTC
    current_time_utc = datetime.now(timezone.utc)
    
    # Calculate the time difference between now and the last trade time
    time_diff = current_time_utc - last_trade_time_utc
    
    # If the last trade occurred within the last few minutes, the market is open
    if time_diff.total_seconds() < 300:  # 5 minutes threshold
        return True
    else:
        return False
    
