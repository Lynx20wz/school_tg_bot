from aiogram import Router, F

from bot.bin import UserClass, logger

unknown_router = Router()


@unknown_router.message(F.text)
@UserClass.get_user()
async def unknown_command(message, user):
    logger.error(f'Non-existent command has been called ({message.from_user.username}):\n"{message.text}"')
    await message.answer(
        'Извините, нет такой команды. Пожалуйста, используйте доступные кнопки или команды.',
        disable_notification=user.setting_notification,
    )
