from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
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
        recommendations["total_recommendations"] = recommendations.get("strongBuy", 0) + \
            recommendations.get("buy", 0) + recommendations.get("hold", 0) + \
            recommendations.get("sell", 0) + recommendations.get("strongSell", 0)
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
    
def is_traded_today(symbol: str) -> bool:
    DAY_IN_SEC = 60*60*24

    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    last_trade_time = hist.index[-1]
    last_trade_time_utc = last_trade_time.tz_convert(timezone.utc)
    current_time_utc = datetime.now(timezone.utc)
    time_diff = current_time_utc - last_trade_time_utc
    if time_diff.total_seconds() < DAY_IN_SEC:
        return True
    else:
        return False
    
def get_stock_data(symbol: str) -> Dict[str, Optional[float]]:
    stock = yf.Ticker(symbol)
    return_data = {}
    try:
        return_data["p_to_e_ratio"] = stock.info["trailingPE"]
    except:
        return_data["p_to_e_ratio"] = None
    
    try:
        return_data["market_cap"] = stock.info["marketCap"]
    except:
        return_data["market_cap"] = None
    
    return return_data

def get_last_earnings(symbol: str) -> Dict[str, Any]:
    stock = yf.Ticker(symbol)
    quarterly_financials = stock.quarterly_financials
    last_reported_date = quarterly_financials.keys()[0]
    quarterly_income_stmt = stock.quarterly_income_stmt
    last_reported_net_income = quarterly_income_stmt.keys()[0]
    assert last_reported_date == last_reported_net_income, "Dates do not match"
    last_reported_revenue = quarterly_financials[last_reported_date].loc["Total Revenue"]
    last_reported_eps = quarterly_income_stmt[quarterly_income_stmt.keys()[0]].loc["Diluted EPS"]
    return {
        "date": last_reported_date,
        "revenue": last_reported_revenue,
        "eps": last_reported_eps
    }
