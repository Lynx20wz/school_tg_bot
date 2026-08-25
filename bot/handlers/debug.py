import json

from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.types import FSInputFile, Message

from bot.classes import User
from bot.keyboard import debug_kb, main_kb
from bot.logger import logger
from database import DataBaseCrud

db = DataBaseCrud()
debug_router = Router()


@debug_router.message(or_f(F.text.lower() == 'debug', Command('debug')))
async def developer(message: Message, user: User):
    user.debug = True
    await user.save_settings(debug=user.debug)
    logger.warning(f'{user.username} получил роль разработчика!')
    await message.answer(f'Удачной разработки, {user.username}! 😉', reply_markup=main_kb(user))


@debug_router.message(or_f(F.text == 'Команды дебага', Command('commands')))
async def command_debug(message: Message):
    await message.answer(
        f"""Добро пожаловать разработчик, тут все нужные для тебя команды!

**Доступные команды**:
**/sql** __<command>__ | __<args>__ - сделать SQL запрос
**/user** (/u) __<username>__ - получить информацию о пользователе
**/users** - получить информацию о всех пользователях
**/logfile** - получить логи бота""",
        reply_markup=debug_kb,
        parse_mode='Markdown',
    )


@debug_router.message(F.text == 'Запрос пользователя')
async def get_user(message: Message):
    user_data = await db(message.from_user.id)
    await message.answer(json.dumps(user_data, indent=4, ensure_ascii=False))


@debug_router.message(or_f(F.text == 'В главное меню', Command('exit')))
async def exit_debug_commands(message: Message, user: User):
    await message.answer(
        'Главное меню',
        reply_markup=main_kb(user),
        disable_notification=user.setting_notification,
    )


@debug_router.message(F.text, Command('u', 'user', 'users'))
async def sql_request(message: Message, command):
    command_args = command.args
    command = command.command

    if command == 'users':
        user_data = await db()
        await message.answer(json.dumps(user_data, indent=4, ensure_ascii=False))
    elif command_args is not None:
        user_data = await db(command_args)
        if user_data is None:
            await message.answer(f'Пользователь "{command_args}" не обнаружен!')
        else:
            await message.answer(json.dumps(user_data, indent=4, ensure_ascii=False))
    else:
        await get_user(message)


@debug_router.message(F.text, Command('logfile'))
async def logfile(message: Message):
    log_file = FSInputFile('temp/log.log')
    await message.answer_document(document=log_file)


@debug_router.message(or_f(F.text == 'Выкл. дебаг', Command('off')))
async def remove_debug(message: Message, user: User):
    user.debug = False
    await user.save_settings(debug=user.debug)
    await message.answer(f'Выключаю дебаг...', reply_markup=main_kb(user))
