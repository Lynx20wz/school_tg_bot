from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.logger import logger


class TokenMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict[str, Any]):
        logger.debug('проверка токена')
        if data['user'].token is None:
            await event.answer(
                'У вас отсутствует токен! Пожалуйста введите команду /token, чтобы получить его!'
            )
            return None
        return await handler(event, data)
