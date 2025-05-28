from aiogram import Router, F

from bot.classes.DataBase import DataBase
from bot.classes.UserClass import UserClass
from bot.bin import logger
from bot.until.KeyBoards import make_setting_button, main_button
from aiogram.types import Message

db = DataBase()
settings_router = Router()


@settings_router.message(F.text == 'Настройки ⚙️')
async def settings(message: Message, user: UserClass):
    markup = make_setting_button(user)
    await message.answer(
        text=r"""
Настройки:

*Выдача на день\неделю:*
    1) *"Выдача на день":* будет высылаться домашнее задание только на завтра.
В пятницу, субботу и воскресенье будет высылаться домашнее задание на понедельник.
    2) *"Выдача на неделю":* Будет высылаться домашнее задание на все оставшиеся дни недели.

*Уведомления:*
    1) *"Уведомления вкл.":* включает звук уведомлений для каждого сообщения.
    2) *"Уведомления выкл.":* отключает звук уведомления для каждого сообщения.

*Скрытие ссылок:*
    1) *"Скрыть ссылки":* ссылки будут замаскированны под "ЦДЗ".
    2) *"Показать ссылки":* ссылки будут выведены напрямую.
            """,
        reply_markup=markup,
        parse_mode='Markdown',
        disable_notification=user.setting_notification,
    )


@settings_router.message(F.text.in_(['Выдача на неделю', 'Выдача на день']))
async def change_delivery(message: Message, user: UserClass):
    if message.text == 'Выдача на неделю':
        user.setting_dw = False
    elif message.text == 'Выдача на день':
        user.setting_dw = True
    markup = make_setting_button(user)
    await user.save_settings(setting_dw=user.setting_dw)
    logger.debug(f'Changed issue settings ({message.from_user.username} - {user.setting_dw})')
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@settings_router.message(F.text.in_(['Уведомления вкл.', 'Уведомления выкл.']))
async def change_notification(message: Message, user: UserClass):
    if message.text == 'Уведомления вкл.':
        user.setting_notification = False
    elif message.text == 'Уведомления выкл.':
        user.setting_notification = True
    markup = make_setting_button(user)
    await user.save_settings(setting_notification=user.setting_notification)
    logger.debug(
        f'Changed notification settings ({message.from_user.username} - {user.setting_notification})'
    )
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@settings_router.message(F.text.in_(['Скрыть ссылки', 'Показать ссылки']))
async def change_link(message: Message, user: UserClass):
    if message.text == 'Скрыть ссылки':
        user.setting_hide_link = True
    elif message.text == 'Показать ссылки':
        user.setting_hide_link = False
    markup = make_setting_button(user)
    await user.save_settings(setting_hide_link=user.setting_hide_link)
    logger.debug(f'Changed link settings ({message.from_user.username} - {user.setting_hide_link})')
    await message.answer(
        'Настройки успешно изменены!',
        reply_markup=markup,
        disable_notification=user.setting_notification,
    )


@settings_router.message(F.text == 'Назад')
async def exit_settings(message: Message, user: UserClass):
    logger.debug(f'Out of the settings ({message.from_user.username})')
    await user.save_settings(
        setting_dw=user.setting_dw,
        setting_notification=user.setting_notification,
        setting_hide_link=user.setting_hide_link,
        debug=user.debug,
    )
    await message.answer(
        'Главное меню',
        reply_markup=main_button(user),
        disable_notification=user.setting_notification,
    )


@settings_router.message(F.text == 'Удалить аккаунт')
async def delete_user(message: Message, user: UserClass):
    """Complete deletion of a user.

    Args:
        message (Message): Received message
        user (UserClass): User object
    """
    logger.debug(f'The account has been deleted ({message.from_user.username})')
    await db.delete_user(user.username)
    await message.answer('Аккаунт успешно удален!')
