import unittest
from unittest.mock import MagicMock, patch
import sys

from tests.unit.Mocks.MockGetHandler import gen_mock_handlers

from Routines.StocksDaily import trigger, task


class TestStocksDaily(unittest.TestCase):
    def test_task(self):
        is_stock_updated_today = sys.modules["Routines.resources.Stocks"].is_stock_updated_today
        is_traded_today = sys.modules["Routines.resources.Stocks.yfinance_functions"].is_traded_today
        mock_get_stock_daily = sys.modules["Routines.resources.Stocks.yfinance_functions"].get_stock_daily

        # no update
        is_stock_updated_today.return_value = True
        is_traded_today.return_value = True
        self.assertTrue(task())
        mock_get_stock_daily.assert_not_called()

        is_stock_updated_today.return_value = False
        is_traded_today.return_value = False
        self.assertTrue(task())
        mock_get_stock_daily.assert_not_called()

        is_stock_updated_today.return_value = True
        is_traded_today.return_value = False
        self.assertTrue(task())
        mock_get_stock_daily.assert_not_called()

        # Update
        is_stock_updated_today.return_value = False
        is_traded_today.return_value = True
        self.assertTrue(task())
        mock_get_stock_daily.assert_called()

        # Exception
        mock_get_stock_daily.reset_mock()
        mock_get_stock_daily.side_effect = Exception 
        is_stock_updated_today.return_value = False
        is_traded_today.return_value = True
        with self.assertLogs('Routines.StocksDaily', level='ERROR') as log:
            task_done = task()
            self.assertIn('Error adding stock summary', log.output[0])

        self.assertTrue(task_done)
        mock_get_stock_daily.assert_called()

if __name__ == '__main__':
    unittest.main()