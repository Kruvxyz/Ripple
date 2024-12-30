from abc import ABC

class Executor(ABC):
    def __init__(self):
        pass

    def is_busy(self) -> bool:
        return True
    
    async def cancel(self) -> bool:
        return True

    async def get_result(self) -> bool:
        return True
    
    async def run(self) -> bool:
        return True
    
    async def async_function(self):
        return self.function()