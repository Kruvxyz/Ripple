import unittest
from unittest.mock import patch, MagicMock
from logic import Logic, send_message_to_scheduler, handle_message


class TestLogic(unittest.TestCase):
    def setUp(self):
        self.logic = Logic()

    def test_get_routines_list(self):
        self.logic.reset_routines()
        self.assertEqual(self.logic.get_routines_list(), [])

    def test_get_state(self):
        self.logic.reset_routines()
        self.assertEqual(self.logic.get_state("test"), {"status": None, "tasks": {}})

    @patch("logic.send_message")
    def test_send_message_to_scheduler(self, mock_send_message):
        send_message_to_scheduler("test_command", "test_routine")
        mock_send_message.assert_called_once_with("commands", {"command": "test_command", "routine": "test_routine"})

    def test_handle_message_routine_status(self):
        self.logic.reset_routines()
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status", "epoch": 0}')
        self.assertEqual(self.logic.get_state("test"), {"status": "test_status", "epoch": 0, "tasks": {}})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status2", "epoch": 1}')
        self.assertEqual(self.logic.get_state("test"), {"status": "test_status2", "epoch": 1, "tasks": {}})

    def test_flow(self):
        self.logic.reset_routines()
        self.assertEqual(self.logic.get_routines_list(), [])
        self.assertEqual(self.logic.get_state("test"), {"status": None, "tasks": {}})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status", "epoch": 0}')
        self.assertEqual(self.logic.get_routines_list(), ["test"])
        self.assertEqual(self.logic.get_state("test"), {"status": "test_status", "tasks": {}, "epoch": 0})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "task_status", "routine": "test", "task_id": 12, "status": "test_status","epoch": 1}')
        self.assertEqual(self.logic.get_state("test"), {"status": "test_status", "tasks": {12: {"status": "test_status", "epoch": 1}}, "epoch": 0})

    @patch('logging.error')
    def test_handle_message_assert_exception(self, mock_log_error):
        self.logic.reset_routines()
        with self.assertRaises(AssertionError):
            handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": null, "status": "test_status", "epoch": 0}')
            mock_log_error.assert_called_with(
                "Error handling message b'...': Routine must be a string"
            )


if __name__ == '__main__':
    unittest.main()