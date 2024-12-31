from collections.abc import Awaitable, Callable
from typing import Optional
from .Executor import Executor
from .Status import TriggerInstanceStatus
import asyncio
import logging

logger = logging.getLogger(__name__)

class Trigger(Executor):
    def __init__(
            self,
            name: str,
            function: Optional[Callable[[], bool]] = None,
            async_function: Optional[Callable[[], Awaitable[bool]]] = None, 
    ) -> None:
        self.name = name
        self.is_async_function = async_function is not None
        self.function = async_function if self.is_async_function else function
        self.status = TriggerInstanceStatus.PENDING
        self.job = None

    def is_busy(self) -> bool:
        if self.job is not None:
            return not self.job.done()
        return False
    
    async def cancel(self) -> bool:
        if self.is_busy():
            self.job.cancel()
            await self.job
        self.status = TriggerInstanceStatus.CANCELLED
        self.job = None
        return True

    async def get_result(self) -> bool:
        try:
            result = await self.job
            logger.debug(f"Trigger {self.name} : Trigger result is {result}")
            self.status = TriggerInstanceStatus.DONE
            return result
        except Exception as e:
            logger.warning(f"Trigger {self.name} : Trigger failed with error {e}")
            self.status = TriggerInstanceStatus.ERROR
            raise e

    async def run(self) -> bool:
        # Validate trigger before running
        if self.function is None:
            raise ValueError("Trigger function is not set")
        if self.is_busy():
            raise ValueError("Trigger is busy")
        
        # Execute trigger
        if self.is_async_function:
            self.job = asyncio.create_task(self.function())
        else:
            self.job = asyncio.create_task(self.async_function())
        self.status = TriggerInstanceStatus.RUNNING
        logger.debug(f"Trigger {self.name} : Trigger executing asynchoronously")
        return True
