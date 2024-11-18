from .yf import is_market_open, get_price, get_recommendations, get_stock_daily #, get_stock_data
from Routine import Routine
from shared.models import Stock, StockPrice, StockRecommendation, StockDailyStates


def gen_stock_daily_states_routine(session) -> Routine:
    def stock_daily_states_function() -> bool:
        for stock in session.query(Stock).all():
            stock_data = get_stock_daily(stock.symbol)
            if stock_data.get("success", False):
                try:
                    session.add(StockDailyStates(
                        stock.symbol, 
                        stock_data["open"],
                        stock_data["high"],
                        stock_data["low"],
                        stock_data["close"],
                        stock_data["date"]
                        ))
                    session.commit()
                except:
                    print(f"Error in adding price for {stock.symbol}")
                    session.rollback()
            else:
                print(f"Error in getting data for {stock.symbol}: error: {stock_data.get('error', 'Unknown')}")
        return True
    
    return Routine(
        "Stock_Daily_Summary",
        "This routine collect the stock daily stats for all stocks (in db) and push it to the database",
        stock_daily_states_function,
        23*60*60, # 24 hours
        retry_delay=60*60, # 1 hour
        retry_limit=999
    )

def gen_stock_price_routine(session) -> Routine:
    def stock_price_function() -> bool:
        print("Start collecting data for each stock")
        for stock in session.query(Stock).all():
            price = get_price(stock.symbol)
            if price.get("price", None) is not  None:
                try:
                    session.add(StockPrice(stock.symbol, price["price"]))
                    session.commit()
                except:
                    print(f"Error in adding price for {stock.symbol}")
                    session.rollback()

        return True

    return Routine(
        "Stock_Price", 
        "This routine collects stock prices for all stocks in the database.",
        stock_price_function, 
        10*60, # 10 minutes 
        is_market_open, # Only run when the market is open
    )  

def gen_stock_recommendation_routine(session) -> Routine:
    def stock_recommendation_function() -> bool:
        print("Start collecting data for each stock")
        for stock in session.query(Stock).all():
            print(f"running recommendation for {stock.symbol}")
            recommendations = get_recommendations(stock.symbol)
            if recommendations.get("recommendations", None) is not  None:
                try:
                    buy = recommendations["recommendations"]["buy"] + recommendations["recommendations"]["strongBuy"]
                    hold = recommendations["recommendations"]["hold"]
                    sell = recommendations["recommendations"]["sell"] + recommendations["recommendations"]["strongSell"]   
                    session.add(StockRecommendation(stock.symbol, "yf", buy, hold, sell))
                    # session.add(StockRecommendation(stock.symbol, "yf", 10, 10, 10))
                    session.commit()
                except:
                    print(f"Error in adding recommendation for {stock.symbol}")
                    session.rollback()
        return True
    
    return Routine(
        "Stock_Recommendation",
        "This routine collects stock recommendations for all stocks in the database.",
        stock_recommendation_function,
        12*60*60, # 12 hours
    )

    #         data = get_stock_data(stock.symbol)
    #         if data.get("price", None) is not  None:
    #             session.add(StockPrice(stock.symbol, data["price"]))
    #             should_commit = True
    #         if data.get("recommendations", None) is not None:
    #             try:
    #                 buy = data["recommendations"]["buy"] + data["recommendations"]["strongBuy"]
    #                 hold = data["recommendations"]["hold"]
    #                 sell = data["recommendations"]["sell"] + data["recommendations"]["strongSell"]   
    #                 session.add(StockRecommendation(stock.symbol, "yf", buy, hold, sell))
    #                 print("Adding recommendation")
    #                 should_commit = True
    #             except:
    #                 print(f"Error in adding recommendation for {stock.symbol}")

    #         print("Finish collecting data - updating database")
    #         if should_commit:
    #             session.commit()
    #     print("Finish updating database")
    #     return True

    # return Routine(
    #     "Stock_Price", 
    #     "This routine collects stock prices for all stocks in the database.",
    #     stock_price_function, 
    #     10*60, # 10 minutes 
    #     is_market_open, # Only run when the market is open
    # )