from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Stock(Base):
    __tablename__ = 'stocks'
    symbol = Column("symbol", String(30), unique=True, primary_key=True)
    name = Column("name", String(300))

    def __init__(self, symbol: str, name: str) -> None:
        self.symbol = symbol
        self.name = name

    def __repr__(self) -> str:
        return f"<Stock {self.symbol} {self.name}>"

class StockPrice(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), ForeignKey("stocks.symbol"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    def __init__(self, symbol: str, price: int) -> None:
        self.symbol = symbol
        self.price = price

    def __repr__(self) -> str:
        return f"<StockPrice {self.symbol} {self.price}>"

class StockOfTheDay(Base):
    __tablename__ = 'stock_of_the_day'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), ForeignKey("stocks.symbol"))
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    def __init__(self, symbol: str, reasoning: str) -> None:
        self.symbol = symbol
        self.reasoning = reasoning

    def __repr__(self) -> str:
        return f"<StockOfTheDay {self.symbol} {self.reasoning}>"


class StockDailyStates(Base):
    __tablename__ = 'stock_daily_states'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), ForeignKey("stocks.symbol"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date = Column(DateTime)
    timestamp = Column(DateTime, default=datetime.now)

    def __init__(self, symbol: str, open: float, high: float, low: float, close: float, date: datetime) -> None:
        self.symbol = symbol
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.date = date

    def __repr__(self) -> str:
        return f"<StockDailyStates {self.symbol} {self.open} {self.high} {self.low} {self.close} {self.date}>"
    
class StockRecommendation(Base):
    __tablename__ = 'stock_recommendations'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), ForeignKey("stocks.symbol"))
    source = Column(String(100))
    buy = Column(Integer)
    hold = Column(Integer)
    sell = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    def __init__(self, symbol: str, source: str, buy: int, hold: int, sell: int) -> None:
        self.symbol = symbol
        self.source = source
        self.buy = buy
        self.hold = hold
        self.sell = sell

    def __repr__(self) -> str:
        return f"<StockRecommendation {self.symbol} {self.source} {self.buy} {self.hold} {self.sell}>"
    
class StockEarnings(Base):
    __tablename__ = 'stock_earnings'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), ForeignKey("stocks.symbol"))
    revenue = Column(Float)
    net_income = Column(Float)
    diluted_shares = Column(Float)
    earnings = Column(Float)
    eps = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)
    def __init__(self, symbol: str, earnings: int) -> None:
        self.symbol = symbol
        self.earnings = earnings
    def __repr__(self) -> str:
        return f"<StockEarnings {self.symbol} {self.earnings}>"
