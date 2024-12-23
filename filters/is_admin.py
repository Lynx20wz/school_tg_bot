from aiogram.filters import BaseFilter

from bin.config import ADMIN_IDS


class IsAdmin(BaseFilter):
    def __init__(self):
        self.admins = ADMIN_IDS

    async def __call__(self, message) -> bool:
        return message.from_user.id in self.admins
