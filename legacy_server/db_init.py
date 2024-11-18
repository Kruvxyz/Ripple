from resources.db_connection import generate_session
from resources.stocks_list import get_stock_symbol_name_pairs
from shared.models import Base, Stock
from sqlalchemy import Engine
import numpy as np


def init_db(engine: Engine):
    # engine = generate_engine()
    Base.metadata.create_all(bind=engine)

    # Initialize the database with stock symbols and names
    session = generate_session(engine)

    stocks_list = get_stock_symbol_name_pairs()
    for symbol, name in stocks_list:
        if symbol is np.nan or name is np.nan or symbol is None or name is None or symbol == "" or name == "" or symbol == "None" or name == "None" or symbol == "nan" or name == "nan":
            continue
        stock = Stock(symbol, name)
        session.add(stock) 

    try:
        session.commit()

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()  # Rollback the changes on error
        # raise e
    
    finally:
        session.close()
