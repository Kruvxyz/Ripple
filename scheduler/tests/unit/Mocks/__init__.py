import sys  
"""
This module sets up mock objects for unit testing.

Modules:
    sys: Provides access to some variables used or maintained by the interpreter.
    unittest.mock: Library for creating mock objects for testing.

Functions:
    gen_mock_handlers: Generates mock handlers for testing purposes.

Mocks:
    mock_db: A MagicMock object that mocks the `db` module.
        - gen_routine_handlers: Mock method returning generated mock handlers.
        - generate_engine: Mock method for generating engine.
    mock_resources: A MagicMock object that mocks the `resources` module.
        - Stocks: Mock class for stock-related functions.
            - get_stocks_list: Mock method returning None.
            - add_stock_price: Mock method returning None.
            - yfinance_functions: Mock class for yfinance-related functions.
                - is_market_open: Mock method returning True.
                - get_price: Mock method returning a dictionary with a price key.

The mock objects are inserted into `sys.modules` to replace the actual modules during testing.
"""

from unittest.mock import MagicMock
from .MockGetHandler import gen_mock_handlers

# Mock `db` and `resources` before importing anything else
mock_db = MagicMock()
mock_db.gen_routine_handlers = MagicMock(return_value=gen_mock_handlers("mocked_handlers"))
mock_db.generate_engine = MagicMock()
sys.modules["db"] = mock_db

mock_resources = MagicMock()
mock_resources.Articles = MagicMock()
mock_resources.Articles.init_db = MagicMock()
mock_resources.Articles.routine_factory = MagicMock()
mock_resources.Articles.routine_factory.gen_routine = MagicMock()
mock_resources.Stocks = MagicMock()
mock_resources.Stocks.get_stocks_list = MagicMock(return_value=None)
mock_resources.Stocks.add_stock_price = MagicMock(return_value=None)
mock_resources.Stocks.yfinance_functions = MagicMock()
mock_resources.Stocks.yfinance_functions.is_market_open = MagicMock(return_value=True)
mock_resources.Stocks.yfinance_functions.get_price = MagicMock(return_value={"price": 1.0})
sys.modules["Routines.resources"] = mock_resources
sys.modules["Routines.resources.Articles"] = mock_resources.Articles
sys.modules["Routines.resources.Articles.init_db"] = mock_resources.Articles.init_db
sys.modules["Routines.resources.Articles.routine_factory"] = mock_resources.Articles.routine_factory
sys.modules["Routines.resources.Articles.routine_factory.gen_routine"] = mock_resources.Articles.routine_factory.gen_routine
sys.modules["Routines.resources.Stocks"] = mock_resources.Stocks
sys.modules["Routines.resources.Stocks.yfinance_functions"] = mock_resources.Stocks.yfinance_functions
