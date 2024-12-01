import os
import logging
import numpy as np
import pandas as pd
from typing import Iterable, Tuple
from .Stock import Stock
from . import get_stock
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_stock_symbol_name_pairs() -> Iterable[Tuple[str, str]]:
    path = os.path.join(os.getcwd(), "Routines", "resources", "Stocks", "files", "nasdaq_screener_1727977170140.csv")
    stocks_df = pd.read_csv(path)
    return zip(stocks_df["Symbol"], stocks_df["Name"])


def set_db_with_stocks_list(session: Session) -> bool:
    stocks_list = get_stock_symbol_name_pairs()
    for symbol, name in stocks_list:
        if symbol is np.nan or name is np.nan or symbol is None or name is None or symbol == "" or name == "" or symbol == "None" or name == "None" or symbol == "nan" or name == "nan":
            logger.info(f"Skipping stock | {symbol} | {name}")
            continue
        exist_stock = get_stock(symbol)
        if exist_stock:
            logger.info(f"Stock already exists | {symbol} | {name}")
            continue
        stock = Stock(symbol, name)
        session.add(stock) 
        logger.info(f"Stock added | {symbol} | {name}")

    try:
        session.commit()

    except Exception as e:
        logger.error(f"Error: {e}")
        session.rollback()  # Rollback the changes on error
        session.close()
        return False
    
    finally:
        session.close()

    return True