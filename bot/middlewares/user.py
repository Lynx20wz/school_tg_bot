from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.uow import UnitOfWork


class UserMiddleware(BaseMiddleware):
    """Middleware for getting user."""

    async def __call__(self, handler, event: Message, data: dict[str, Any]):
        uow: UnitOfWork = data['uow']
        data['user'] = await uow.users.get_or_create(event.from_user.id)
        return await handler(event, data)
