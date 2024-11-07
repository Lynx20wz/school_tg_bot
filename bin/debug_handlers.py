from aiogram import Router, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from KeyBoards import main_button
from bin import UserClass, db

debug_router = Router()

from loguru import logger

def make_debug_button():
    return ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[
                [
                    KeyboardButton(text='В главное меню'),
                    KeyboardButton(text='Запрос пользователя')
                ],
                [KeyboardButton(text='Выкл. дебаг')]
            ]
    )


@debug_router.message(F.text.lower() == 'debug')
@UserClass.get_user()
async def developer(message, user):
    user.debug = True
    user.save_settings(db, debug=user.debug, save_db=True)
    logger.warning(f'{user.username} получил роль разработчика!')
    await message.answer(f'Удачной разработки, {user.username}! 😉', reply_markup=main_button(user))


@debug_router.message(F.text == 'Команды дебага')
async def command_debug(message):
    await message.answer(f'Добро пожаловать разработчик, тут все нужные для тебя команды!', reply_markup=make_debug_button())


@debug_router.message(F.text == 'Запрос пользователя')
async def get_user(message):
    await message.answer(f'{db(message.from_user.username)}')


@debug_router.message(F.text == 'В главное меню')
@UserClass.get_user()
async def exit_debug_commands(message, user):
    logger.debug(f'{user.setting_dw} - {user.setting_notification}')
    logger.info(f'Вышел из команд дебага ({message.from_user.username})')
    await message.answer('Главное меню', reply_markup=main_button(user), disable_notification=user.setting_notification)


@debug_router.message(F.text == 'Выкл. дебаг')
@UserClass.get_user()
async def remove_debug(message, user):
    user.debug = False
    user.save_settings(debug=user.debug, save_db=True, database=db)
    logger.debug(f'{user.username} отключил роль разработчика.')
    await message.answer(f'Выключаю дебаг...', reply_markup=main_button(user))
