from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock
import sys

from Routines.StocksEarnings import trigger_earnings, task_earnings
from tests.unit.Mocks.MockGetHandler import gen_mock_handlers

class TestStocksEarnings(unittest.TestCase):

    def test_trigger_no_previous_earning_reported(self):
        last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_stock_last_earning_date = sys.modules["Routines.resources.Stocks"].get_stock_last_earning_date
        get_stock_last_earning_date.return_value = None

        # Trigger within window of 4 days (today and 3 days before)
        last_earnings.return_value = {"date": datetime.today(), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=1), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=2), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=3), "success": True}
        self.assertTrue(trigger_earnings())

        # Don't trigger if earnings are not within window
        last_earnings.return_value = {"date": datetime.today() - timedelta(days=10), "success": True}
        self.assertFalse(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() + timedelta(days=1), "success": True}
        self.assertFalse(trigger_earnings())


    def test_trigger_previous_earning_reported(self):
        last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_stock_last_earning_date = sys.modules["Routines.resources.Stocks"].get_stock_last_earning_date
        get_stock_last_earning_date.return_value = [datetime(2024, 1, 1)]

        # Trigger within window of 4 days (today and 3 days before)
        last_earnings.return_value = {"date": datetime.today(), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=1), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=2), "success": True}
        self.assertTrue(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() - timedelta(days=3), "success": True}
        self.assertTrue(trigger_earnings())

        # Don't trigger if earnings are not within window
        last_earnings.return_value = {"date": datetime.today() - timedelta(days=10), "success": True}
        self.assertFalse(trigger_earnings())

        last_earnings.return_value = {"date": datetime.today() + timedelta(days=1), "success": True}
        self.assertFalse(trigger_earnings())

    def test_trigger_earnings_already_updated(self):
        last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_stock_last_earning_date = sys.modules["Routines.resources.Stocks"].get_stock_last_earning_date
        get_stock_last_earning_date.return_value = [datetime.today()]

        last_earnings.return_value = {"date": datetime.today(), "success": True}
        self.assertFalse(trigger_earnings())        

    def test_task_earning_error(self):
        get_last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_last_earnings.return_value = {"date": None, "eps": 1.0, "revenue": 1.0, "success": True}

        with self.assertLogs('Routines.StocksEarnings', level='ERROR') as log:
            task_earnings()
            self.assertIn('Error getting last earnings for stock with symbol', log.output[0])

    def test_task_earning(self):
        get_last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_last_earnings.return_value = {"date": datetime.today(), "eps": 1.0, "revenue": 1.0, "success": True}
        add_stock_earnings = sys.modules["Routines.resources.Stocks"].add_stock_earnings
        add_stock_earnings.return_value = None

        self.assertTrue(task_earnings())

    def test_task_earning_exception(self):
        add_stock_earnings = sys.modules["Routines.resources.Stocks"].add_stock_earnings
        add_stock_earnings.side_effect = Exception

        get_last_earnings = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_last_earnings
        get_last_earnings.return_value = {"date": datetime.today(), "eps": 1.0, "revenue": 1.0, "success": True}

        get_stock_last_earning_date = sys.modules["Routines.resources.Stocks"].get_stock_last_earning_date
        get_stock_last_earning_date.return_value = None


        with self.assertLogs('Routines.StocksEarnings', level='ERROR') as log:
            task_earnings()
            self.assertIn('Error adding stock earnings with symbol', log.output[0])

        get_last_earnings.side_effect = None

if __name__ == '__main__':
    unittest.main()  