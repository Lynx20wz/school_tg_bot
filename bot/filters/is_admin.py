from typing import override

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.config import config


class IsAdmin(BaseFilter):
    def __init__(self):
        self.admins: list[int] = config.admin_ids

    @override
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admins
