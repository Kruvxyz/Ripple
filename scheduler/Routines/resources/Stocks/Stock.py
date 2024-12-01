from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Stock(Base):
    __tablename__ = 'stocks'
    id = Column("id", Integer, primary_key=True)
    symbol = Column("symbol", String(300), unique=True, nullable=False)
    name = Column("name", String(300))
    summary = Column("summary", Text, default="")
    status = Column("status", String(300), default="active")
    created_at = Column("created_at", DateTime, default=datetime.now)
    summaries = relationship("StockDataSummary", back_populates="stock")
    prices = relationship("StockPrice", back_populates="stock", order_by="StockPrice.timestamp.desc()")
    earnings = relationship("StockEarnings", back_populates="stock", order_by="StockEarnings.earnings_date.desc()")
    # price = relationship("StockPrice", back_populates="stock")

    @property
    def latest_price(self):
        """Convenience property to get the latest price."""
        if self.prices:
            return self.prices[0].price  # Assuming prices are ordered by timestamp
        return None

    def __init__(
            self,
            symbol: str,
            name: str,
    ) -> None:
        self.symbol = symbol
        self.name = name

    def __repr__(self) -> str:
        return f"<Stock | {self.symbol} | {self.name} | {self.summary} | {self.latest_price}>"



class StockDataSummary(Base):
    __tablename__ = 'stocks_data_summaries'
    id = Column("id", Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column("date", DateTime, default=datetime.now)
    p_to_e_ratio = Column("p_to_e_ratio", Float)
    market_cap = Column("market_cap", Float)
    open_price = Column("open_price", Float)
    close_price = Column("close_price", Float)
    high_price = Column("high_price", Float)
    low_price = Column("low_price", Float)
    recommendations_strong_buy = Column("recommendations_strong_buy", Integer)
    recommendations_buy = Column("recommendations_buy", Integer)
    recommendations_sell = Column("recommendations_sell", Integer)
    recommendations_hold = Column("recommendations_hold", Integer)
    recommendations_strong_sell = Column("recommendations_strong_sell", Integer)
    total_recommendations = Column("total_recommendations", Integer)
    created_at = Column("created_at", DateTime, default=datetime.now)
    stock = relationship("Stock", back_populates="summaries")

    def __init__(
            self,
            stock_id: int,
            date: Optional[datetime],
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
        self.stock_id = stock_id
        self.date = date
        self.p_to_e_ratio = p_to_e_ratio
        self.market_cap = market_cap
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price
        self.recommendations_strong_buy = recommendations_strong_buy
        self.recommendations_buy = recommendations_buy
        self.recommendations_sell = recommendations_sell
        self.recommendations_hold = recommendations_hold
        self.recommendations_strong_sell = recommendations_strong_sell
        self.total_recommendations = total_recommendations

    @property
    def day_update(self):
        return self.date.date()
    
    def __repr__(self) -> str:
        return f"<StockSummary | {self.stock.symbol} | {self.date}>"


class StockPrice(Base):
    __tablename__ = 'stocks_raw'
    id = Column("id", Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    price = Column("price", Float)
    timestamp = Column("timestamp", DateTime, default=datetime.now)
    created_at = Column("created_at", DateTime, default=datetime.now)
    stock = relationship("Stock", back_populates="prices")
    def __init__(
            self,
            stock_id: int,
            price: float,
            timestamp: Optional[datetime],
    ) -> None:
        self.stock_id = stock_id
        self.price = price
        if timestamp:
            self.timestamp = timestamp

    def __repr__(self) -> str:
        return f"<StockPrice | {self.stock.symbol} | {self.timestamp} | {self.price}>"
    
class StockEarnings(Base):
    __tablename__ = 'stocks_earnings'
    id = Column("id", Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    earnings_date = Column("earnings_date", DateTime)
    earnings_per_share = Column("earnings_per_share", Float)
    revenue = Column("revenue", Float)
    link = Column("link", String(300))
    is_reported = Column("is_reported", Boolean, default=False)
    created_at = Column("created_at", DateTime, default=datetime.now)
    updated_at = Column("updated_at", DateTime, default=datetime.now, onupdate=datetime.now)
    stock = relationship("Stock", back_populates="earnings")

    def __init__(
            self,
            stock_id: int,
            earnings_date: datetime,
            is_reported: bool,
            earnings_per_share: Optional[float],
            revenue: Optional[float],
            link: Optional[str],
    ) -> None:
        self.stock_id = stock_id
        self.earnings_date = earnings_date
        self.is_reported = is_reported
        self.earnings_per_share = earnings_per_share
        self.revenue = revenue
        self.link = link

    def __repr__(self) -> str:
        return f"<StockEarnings | {self.stock.symbol} | {self.earnings_date} | {self.earnings_per_share} | {self.revenue}>"
