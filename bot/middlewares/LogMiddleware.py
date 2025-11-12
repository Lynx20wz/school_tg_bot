from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.bin import logger


class LogMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, event: Message, data: dict):
        logger.debug(f'{data["user"].username} - {data["handler"].callback.__name__}')
        return await handler(event, data)
