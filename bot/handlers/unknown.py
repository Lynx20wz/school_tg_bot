from aiogram import F, Router
from aiogram.types import Message

from bot.logger import logger
from database import User

unknown_router = Router()


@unknown_router.message(F.text)
async def unknown_command(message: Message, user: User):
    logger.error(
        f'Non-existent command has been called ({message.from_user.username}):\n"{message.text}"'
    )
    await message.answer(
        'Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.',
        disable_notification=user.setting_notifications,
    )
