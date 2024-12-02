from collections.abc import Callable
from datetime import datetime
import os
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import create_engine, exc, Engine
from typing import Iterable, Optional, Tuple
from RoutineManager.Status import RoutineStatus, TaskInstanceStatus 
from .Stock import Stock, StockDataSummary, StockPrice, StockEarnings

logger = logging.getLogger(__name__)


def connect_with_retry(db_url, retries=5, delay=2):
    for i in range(retries):
        try:
            engine = create_engine(db_url)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")


def generate_engine(retries=5, delay=2):
    MYSQL_USER = os.environ.get("MYSQL_ARTICLES_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_ARTICLES_PASSWORD")
    MYSQL_HOST = os.environ.get("MYSQL_ARTICLES_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_ARTICLES_DATABASE")
    connection_string = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    print(f"Connecting to database with connection string: {connection_string}")
    logger.info(f"Connecting to database with connection string: {connection_string}")

    for i in range(retries):
        try:
            engine = create_engine(connection_string, echo=True)
            # Try connecting
            with engine.connect() as connection:
                print("Successfully connected to the database!")
                return engine
        except exc.OperationalError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after several attempts.")

def generate_session(engine: Engine):
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)  # Thread-safe session
    return Session()

def init_db() -> bool:
    engine = generate_engine()
    try:
        Stock.metadata.create_all(engine)
        StockDataSummary.metadata.create_all(engine)
        StockPrice.metadata.create_all(engine)
        StockEarnings.metadata.create_all(engine)

    except Exception as e:
        logger.error(f"Error: {e}")
        engine.dispose()
        return False
    
    finally:
        engine.dispose()

    from .db_init import set_db_with_stocks_list
    result = set_db_with_stocks_list(generate_session(engine))
    engine.dispose()
    return result
     
def add_stock_price(
        symbol: str,
        price: float,
        date: Optional[datetime],
    ) -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.error(f"add_stock_price | Stock with symbol {symbol} not found")
            return
        if not date:
            stock_price = StockPrice(stock.id, price)
        else:
            stock_price = StockPrice(stock.id, price, date)
        session.add(stock_price)
        session.commit()
        logger.debug(f"add_stock_price | Stock price added with symbol {symbol} and price {price}")
    except Exception as e:
        logger.error(f"add_stock_price | Error adding stock price with symbol {symbol} and price {price} with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()

    return None

def add_stock_summary(
        symbol: str,
        date: datetime,
        p_to_e_ratio: Optional[float],
        market_cap: Optional[float],
        open_price: Optional[float],
        close_price: Optional[float],
        high_price: Optional[float],
        low_price: Optional[float],
        recommendations_strong_buy: Optional[int],
        recommendations_buy: Optional[int],
        recommendations_sell: Optional[int],
        recommendations_hold: Optional[int],
        recommendations_strong_sell: Optional[int],
        total_recommendations: Optional[int],
    ) -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.error(f"add_stock_summary | Stock with symbol {symbol} not found")
            return
        stock_summary = StockDataSummary(
            stock.id,
            date,
            p_to_e_ratio,
            market_cap,
            open_price,
            close_price,
            high_price,
            low_price,
            recommendations_strong_buy,
            recommendations_buy,
            recommendations_sell,
            recommendations_hold,
            recommendations_strong_sell,
            total_recommendations
        )
        session.add(stock_summary)
        session.commit()
        logger.debug(f"add_stock_summary | Stock summary added with symbol {symbol} and date {date}")
    except Exception as e:
        logger.error(f"add_stock_summary | Error adding stock summary with symbol {symbol} and date {date} with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()

def add_stock_earnings(
        symbol: str,
        earnings_date: datetime,
        eps: float,
        revenue: float,
        is_reported: bool,
    ) -> None:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.error(f"add_stock_earnings | Stock with symbol {symbol} not found")
            return
        stock_earnings = StockEarnings(
            stock.id,
            earnings_date,
            is_reported,
            eps,
            revenue,
            None
        )
        session.add(stock_earnings)
        session.commit()
        logger.debug(f"add_stock_earnings | Stock earnings added with symbol {symbol} and date {earnings_date}")
    except Exception as e:
        logger.error(f"add_stock_earnings | Error adding stock earnings with symbol {symbol} and date {earnings_date} with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()

def get_stock(symbol: str) -> Optional[Stock]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        return stock
    except Exception as e:
        logger.error(f"get_stock | Error getting stock with symbol {symbol} with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()
        
def get_stocks_list(active_only: bool = True) -> Iterable[Stock]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        if active_only:
            stocks = session.query(Stock).filter(Stock.status == 'active').all()
        else:
            stocks = session.query(Stock).all()
        return stocks
    except Exception as e:
        logger.error(f"get_stocks_list | Error getting stocks with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()

def is_stock_updated_today(symbol: str) -> bool:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.error(f"is_stock_updated_today | Stock with symbol {symbol} not found")
            return False
        stock_summary = session.query(StockDataSummary).filter(StockDataSummary.stock_id == stock.id).order_by(StockDataSummary.date.desc()).first()
        if not stock_summary:
            return False
        return stock_summary.date.date() == datetime.now().date()
    except Exception as e:
        logger.error(f"is_stock_updated_today | Error checking if stock with symbol {symbol} is updated today with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()
    return False

def get_stock_last_earning_date(symbol: str) -> Optional[Tuple[datetime, bool]]:
    engine = generate_engine()
    session = generate_session(engine)
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.error(f"get_stock_last_earning_date | Stock with symbol {symbol} not found")
            return None
        stock_earning = session.query(StockEarnings).filter(StockEarnings.stock_id == stock.id).order_by(StockEarnings.date.desc()).first()
        if not stock_earning:
            return None
        return (stock_earning.earnings_date, stock_earning.is_reported)
    except Exception as e:
        logger.error(f"get_stock_last_earning_date | Error getting last earning date for stock with symbol {symbol} with error: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()
    return None