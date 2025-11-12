from aiogram.filters import BaseFilter

from bot.config import config


class IsAdmin(BaseFilter):
    def __init__(self):
        self.admins = config.ADMIN_IDS

    async def __call__(self, message) -> bool:
        return message.from_user.id in self.admins
