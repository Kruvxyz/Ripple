import unittest
from unittest.mock import patch, MagicMock

from tests.unit.Mocks.MockGetHandler import gen_mock_handlers
from Routines.StocksPrice import get_stocks_price_task
import sys

class TestStocksPrice(unittest.TestCase):
    def test_get_stock_price_task_empty_list(self):
        task_done = get_stocks_price_task([])
        self.assertEqual(task_done, True)


if __name__ == '__main__':
    unittest.main()
