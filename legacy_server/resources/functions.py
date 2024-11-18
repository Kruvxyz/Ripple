# import yfinance as yf
# from datetime import datetime, timezone


# def is_market_open():
#     # Get stock data for a specific symbol (e.g., 'AAPL' for Apple)
#     ticker_symbol = "AAPL"
#     ticker = yf.Ticker(ticker_symbol)
    
#     # Fetch the historical intraday data (1-minute interval)
#     hist = ticker.history(period="1d", interval="1m")
    
#     # Get the most recent entry
#     last_trade_time = hist.index[-1]
    
#     # Convert the last trade time to UTC for comparison
#     last_trade_time_utc = last_trade_time.tz_convert(timezone.utc)
    
#     # Get the current time in UTC
#     current_time_utc = datetime.now(timezone.utc)
    
#     # Calculate the time difference between now and the last trade time
#     time_diff = current_time_utc - last_trade_time_utc
    
#     # If the last trade occurred within the last few minutes, the market is open
#     if time_diff.total_seconds() < 300:  # 5 minutes threshold
#         return True
#     else:
#         return False