import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters.command import Command
from aiogram.types import (
    BotCommand,
    BufferedInputFile,
    Message,
)

from bot.classes import User
from bot.config import config
from bot.filters import IsAdmin
from bot.handlers import *
from bot.keyboard import main_kb
from bot.logger import logger
from bot.middlewares import LogMiddleware, TokenMiddleware, UserMiddleware
from database import DataBaseCrud

bot = Bot(config.token)
dp = Dispatcher()


@dp.message(F.text, Command('start'))
async def start(message: Message, user: User):
    logger.info(f'The bot was launched by {message.from_user.username}')
    with open('bot/logging.png', 'rb') as file:
        await message.answer_photo(
            photo=BufferedInputFile(file.read(), filename='Логирование'),
            caption="""Привет. Этот бот создан для вашего удобства и комфорта! Здесь вы можете глянуть расписание, дз, и т.д. Найдёте ошибки сообщите: @Lynx20wz)
                \nP.S: Также должен сказать, что в целях отлова ошибок я веду логирование, то есть, я вижу какую функцию вы запустили и ваш никнейм в телеграм (на фото видно).""",
            reply_markup=main_kb(user),
        )


async def main():
    db = DataBaseCrud()
    dp.include_routers(
        debug_router,
        auth_router,
        data_get_router,
        settings_router,
        # don't put it under this router, it should be the last one.
        unknown_router,
    )

    dp.message.outer_middleware(UserMiddleware())
    debug_router.message.filter(IsAdmin())
    dp.message.middleware(LogMiddleware())

    data_get_router.message.middleware(TokenMiddleware())

    await bot.set_my_commands(
        [
            BotCommand(command='start', description='Начало работы'),
            BotCommand(command='marks', description='Оценки'),
            BotCommand(command='schedule', description='Расписание'),
            BotCommand(command='homework', description='Домашнее задание'),
            BotCommand(command='token', description='Обновить или задать токен'),
        ]
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await db.init()
    logger.info('Bot started!')
    await dp.start_polling(bot)
    logger.info('Bot shutdown!')


if __name__ == '__main__':
    asyncio.run(main())
