import asyncio
import threading
from types import CoroutineType


class CancellableTaskThread(threading.Thread):
    __task: asyncio.Task

    def __init__(self, coro: CoroutineType):
        super().__init__(target=lambda: asyncio.run(self.__run_task(coro)), daemon=True)

    async def __run_task(self, coro: CoroutineType):
        self.__task = asyncio.create_task(coro)

    def cancel(self):
        self.__task.cancel()
