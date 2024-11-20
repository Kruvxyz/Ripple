import unittest
from unittest.mock import MagicMock, patch
from .MockGetHandler import gen_mock_handlers
from RoutineManager.Status import RoutineStatus
import sys
    
class TestRoutine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mock_db = MagicMock()
        mock_db.gen_routine_handlers = MagicMock(return_value=gen_mock_handlers("test"))
        sys.modules["db"] = mock_db

    def setUp(self):
        from RoutineManager.Routine import Routine

        self.INTERVAL = 1
        # self.assertFalse(mock_handler.called)
        self.trigger = False
        # with patch("gen_routine_handlers", MagicMock()):
        # with patch.object(Routine, "db.gen_routine_handlers", MagicMock()):
        self.routine = Routine(
            name="test",
            description="test",
            task=None,
            interval=self.INTERVAL,
            condition_function=lambda: self.trigger,
            condition_function_args=None,
            retry_delay=self.INTERVAL,
            retry_limit=5,
            timeout_limit=60,
        )
        # self.assertFalse(mock_handler.called)
        

    def test_calculate_sleep_preiod(self):
        self.assertEqual(self.routine.calculate_sleep_preiod(), self.INTERVAL)

    def test_get_status(self):
        self.assertEqual(self.routine.get_status(), RoutineStatus.WAITING) 

    def test_set_new_task(self):
        self.routine.create_new_task = MagicMock(return_value="new_task")
        self.routine.task = MagicMock()
        self.routine.set_new_task()
        self.assertEqual(self.routine.current_task_db_instance, "new_task")
    
    def test_release_task(self):
        self.routine.task = MagicMock()
        self.routine.release_task()
        self.assertIsNone(self.routine.current_task_db_instance)

if __name__ == '__main__':
    unittest.main()
