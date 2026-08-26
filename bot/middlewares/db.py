from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.uow import UnitOfWork


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict[str, Any]):
        async with UnitOfWork() as uow:
            data['uow'] = uow
            await handler(event, data)
