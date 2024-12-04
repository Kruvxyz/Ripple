import unittest
from unittest.mock import patch
from tests.unit.Mocks.Stocks import Stock

from Routines.StocksPrice import get_stocks_price_task

class TestStocksPrice(unittest.TestCase):
    def test_get_stock_price_task_empty_list(self):
        task_done = get_stocks_price_task([])
        self.assertEqual(task_done, True)

    def test_get_stocks_price_task_list_not_empty(self):
        list_of_stocks = [Stock("AAPL"), Stock("GOOGL")]
        task_done = get_stocks_price_task(list_of_stocks)
        self.assertEqual(task_done, True)
    
    def test_get_stocks_price_task_exception(self):
        list_of_stocks = [Stock("AAPL"), Stock("GOOGL")]
        with patch("Routines.StocksPrice.get_price", side_effect=Exception) as mock_get_price:
            with self.assertLogs('Routines.StocksPrice', level='ERROR') as log:
                task_done = get_stocks_price_task(list_of_stocks)
                self.assertIn('Error getting stock price with error:', log.output[0])
            self.assertEqual(task_done, False)
            mock_get_price.assert_called()


if __name__ == '__main__':
    unittest.main()
