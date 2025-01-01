import unittest
from unittest.mock import patch, MagicMock
from logic import reset_routines, get_routines_list, get_state, send_message_to_scheduler, handle_message


class TestLogic(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_routines_list(self):
        reset_routines()
        self.assertEqual(get_routines_list(), [])

    def test_get_state(self):
        reset_routines()
        self.assertEqual(get_state("test"), {"status": None, "tasks": {}})

    @patch("logic.send_message")
    def test_send_message_to_scheduler(self, mock_send_message):
        send_message_to_scheduler("test_command", "test_routine")
        mock_send_message.assert_called_once_with("commands", {"command": "test_command", "routine": "test_routine"})

    def test_handle_message_routine_status(self):
        reset_routines()
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status", "epoch": 0}')
        self.assertEqual(get_state("test"), {"status": "test_status", "epoch": 0, "tasks": {}})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status2", "epoch": 1}')
        self.assertEqual(get_state("test"), {"status": "test_status2", "epoch": 1, "tasks": {}})

    def test_flow(self):
        reset_routines()
        self.assertEqual(get_routines_list(), [])
        self.assertEqual(get_state("test"), {"status": None, "tasks": {}})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": "test", "status": "test_status", "epoch": 0}')
        self.assertEqual(get_routines_list(), ["test"])
        self.assertEqual(get_state("test"), {"status": "test_status", "tasks": {}, "epoch": 0})
        handle_message(MagicMock(), MagicMock(), None, b'{"type": "task_status", "routine": "test", "task_id": 12, "status": "test_status","epoch": 1}')
        self.assertEqual(get_state("test"), {"status": "test_status", "tasks": {12: {"status": "test_status", "epoch": 1}}, "epoch": 0})

    @patch('logging.error')
    def test_handle_message_assert_exception(self, mock_log_error):
        reset_routines()
        with self.assertRaises(AssertionError):
            handle_message(MagicMock(), MagicMock(), None, b'{"type": "routine_status", "routine": null, "status": "test_status", "epoch": 0}')
            mock_log_error.assert_called_with(
                "Error handling message b'...': Routine must be a string"
            )


if __name__ == '__main__':
    unittest.main()