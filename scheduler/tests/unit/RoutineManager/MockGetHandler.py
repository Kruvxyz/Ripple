from unittest.mock import MagicMock
from datetime import datetime

class MockRoutine:
    def __init__(
            self, 
            name: str, 
            description: str, 
            retry_delay: int = 5*60,
            retry_limit: int = 5
        ) -> None:
        self.id = MagicMock()
        self.name = name
        self.description = description
        self.status = "waiting"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.retry_delay = retry_delay
        self.retry_limit = retry_limit
        self.error = ""
        self.tasks = MagicMock()

    def __repr__(self) -> str:
        return f"<MockRoutine | {self.name} | {self.status}>"


def gen_mock_handlers(name):
    """
    Mock functions to simulate database interactions without using an actual database or SQLAlchemy.

    These mock functions are used to:
    - Avoid the overhead of setting up and tearing down a database.
    - Ensure tests run quickly and deterministically.
    - Focus on testing the logic of the code rather than the database interactions.

    The `MagicMock` class from the `unittest.mock` module is used to create mock objects that can simulate the behavior of the database methods.
    """
    def session(self):
        return MagicMock()
    
    def gen_routine(description):
        return MockRoutine(name, description)
    
    def update_status(status):
        return MagicMock()
    
    def update_error(error):
        return MagicMock()
    
    def create_new_task(task):
        return MagicMock(return_value="New Task")
    
    def gen_task_handlers(task):
        return MagicMock(), MagicMock(), MagicMock()
    
    return session, gen_routine, update_status, update_error, create_new_task, gen_task_handlers