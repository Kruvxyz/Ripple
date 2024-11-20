import unittest
from unittest.mock import MagicMock, patch
import sys


class TestRoutineManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock modules
        mock_shared = MagicMock()
        sys.modules["shared"] = mock_shared

        mock_db = MagicMock()
        mock_db.init_db = MagicMock()
        sys.modules["db"] = mock_db

    def setUp(self):
        # Import after mocking
        from RoutineManager.RoutineManager import RoutineManager
        self.routine_manager = RoutineManager()

    def test_get_routine(self):
        dummy_routine = MagicMock()
        dummy_routine.name = "dummy"

        test_routine_name = "test"
        test_routine = MagicMock()
        test_routine.name = test_routine_name
        self.routine_manager.routines = [dummy_routine, test_routine]
        routine = self.routine_manager.get_routine(test_routine_name)
        self.assertEqual(routine, test_routine)


if __name__ == '__main__':
    unittest.main()