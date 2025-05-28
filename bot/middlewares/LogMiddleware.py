from aiogram import BaseMiddleware
from aiogram.types import Message
from bot.bin import logger


class LogMiddleware(BaseMiddleware):
    async def __call__(self, handler: callable, event: Message, data: dict):
        logger.debug(f'{data.get("user").username} - {data["handler"].callback.__name__}')
        return await handler(event, data)