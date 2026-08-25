from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.classes import User


class UserMiddleware(BaseMiddleware):
    """Middleware for getting user."""

    async def __call__(self, handler, event: Message, data: dict[str, Any]):
        data['user'] = await User.get_user(message=event)
        return await handler(event, data)
