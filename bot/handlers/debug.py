import json

from aiogram import Router, F
from aiogram.filters import Command, or_f
from loguru import logger

from bot.bin import main_button, make_debug_button
from bot.classes import DataBase

db = DataBase()
debug_router = Router()


@debug_router.message(or_f(F.text.lower() == 'debug', Command('debug')))
async def developer(message, user):
    user.debug = True
    await user.save_settings(debug=user.debug)
    logger.warning(f'{user.username} получил роль разработчика!')
    await message.answer(f'Удачной разработки, {user.username}! 😉', reply_markup=main_button(user))


@debug_router.message(or_f(F.text == 'Команды дебага', Command('commands')))
async def command_debug(message):
    await message.answer(
        f"""Добро пожаловать разработчик, тут все нужные для тебя команды!
    
**Доступные команды**:
**/sql** __<command>__ | __<args>__ - сделать SQL запрос
**/user** (/u) __<username>__ - получить информацию о пользователе
**/users** - получить информацию о всех пользователях
**/logfile** - получить логи бота""",
        reply_markup=make_debug_button(),
        parse_mode='Markdown',
    )


@debug_router.message(F.text == 'Запрос пользователя')
async def get_user(message):
    user_data = await db(message.from_user.username)
    await message.answer(json.dumps(user_data, indent=4, ensure_ascii=False))


@debug_router.message(or_f(F.text == 'В главное меню', Command('exit')))
async def exit_debug_commands(message, user):
    await message.answer(
        'Главное меню',
        reply_markup=main_button(user),
        disable_notification=user.setting_notification,
    )


@debug_router.message(F.text, Command('sql'))
async def sql_debug(message, command):
    command_args = command.args
    if command_args is None:
        await message.answer('Вы не указали аргументы для команды!')
        return
    else:
        command, *args = command_args.split(' | ')
        logger.debug(f'{command=} - {args=}')
        res = await db.custom_command(command, args)
        await message.answer(f'Ответ:\n{str(res)}')


@debug_router.message(F.text, Command('u', 'user', 'users'))
async def sql_request(message, command):
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
async def logfile(message):
    with open('temp/log.log', 'r', encoding='utf-8') as logfile:
        await message.answer('\n'.join(logfile.readlines()))


@debug_router.message(or_f(F.text == 'Выкл. дебаг', Command('off')))
async def remove_debug(message, user):
    user.debug = False
    user.save_settings(debug=user.debug)
    await message.answer(f'Выключаю дебаг...', reply_markup=main_button(user))
