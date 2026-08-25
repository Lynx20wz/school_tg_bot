from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.logger import logger


class LogMiddleware(BaseMiddleware):
    """Middleware for getting user for logging user actions."""

    async def __call__(self, handler, event: Message, data: dict[str, Any]):
        logger.debug(f'{data["user"].username} - {data["handler"].callback.__name__}')
        return await handler(event, data)
