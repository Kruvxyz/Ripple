from .rabbitMQ import receive_message
from typing import Any, Dict, Optional

class CommandService:
    def __init__(self):
        pass

    def get_commands(self) -> Optional[Dict[str, Any]]:
        return receive_message("commands")