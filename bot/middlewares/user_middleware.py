from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.classes import UserClass


class UserMiddleware(BaseMiddleware):
    """Middleware for getting user."""

    async def __call__(self, handler, event: Message, data: dict):
        data['user'] = await UserClass.get_user(message=event)
        return await handler(event, data)
