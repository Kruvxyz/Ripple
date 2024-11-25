import unittest
from unittest.mock import MagicMock
from RoutineManager.Task import Task  # Import the class to be tested
from RoutineManager.Status import TaskStatus

class TestTask(unittest.TestCase):
    def setUp(self):
        pass

    def test_task(self):
        task = Task("test_task")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.is_set, False)

    def test_run_failure(self):
        # not set function
        task = Task("test_task")
        task.update_task_status = MagicMock()
        task.update_task_completed = MagicMock()
        self.assertEqual(task.update_task_status.called, False)
        self.assertEqual(task.update_task_completed.called, False)
        with self.assertRaises(ValueError) as context:
            task.run()
        self.assertEqual(str(context.exception), "Task function is not set")

        # not set task
        task = Task("test_task", function=lambda: True)
        task.update_task_status = MagicMock()
        task.update_task_completed = MagicMock()
        self.assertEqual(task.update_task_status.called, False)
        self.assertEqual(task.update_task_completed.called, False)
        with self.assertRaises(ValueError) as context:
            task.run()
        self.assertEqual(str(context.exception), "Task is not set")

    def test_set_run_release(self):
        update_task_status = MagicMock()
        update_task_completed = MagicMock()
        update_task_error = MagicMock()
        gen_handlers = MagicMock(return_value=(update_task_status, update_task_error, update_task_completed))

        # set task
        task = Task("test_task", function=lambda: True)
        self.assertEqual(task.status, TaskStatus.PENDING)   
        self.assertEqual(task.is_set, False)
        db_instance = MagicMock()
        db_instance.id = 1
        self.assertEqual(update_task_status.called, False)
        task.set(db_instance, gen_handlers)
        self.assertEqual(update_task_status.called, True)
        self.assertEqual(task.update_task_status, update_task_status)
        self.assertEqual(task.update_task_completed, update_task_completed) 
        self.assertEqual(task.update_task_error, update_task_error)
        self.assertEqual(task.status, TaskStatus.READY)
        self.assertEqual(task.is_set, True)

        self.assertEqual(task.get_instance(), db_instance)

        # run task
        self.assertEqual(update_task_completed.called, False)
        result = task.run()
        self.assertEqual(update_task_completed.called, True)
        self.assertEqual(result, True)
        self.assertEqual(task.status, TaskStatus.DONE)

        # release task
        task.release()
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.is_set, False)

if __name__ == '__main__':
    unittest.main()