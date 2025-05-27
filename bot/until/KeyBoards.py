__all__ = (
    'main_button',
    'make_setting_button',
    'token_button',
    'make_debug_button',
    'username_button',
)

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_button(user):
    buttons = [
        [
            KeyboardButton(text='Расписание 📅'),
            KeyboardButton(text='Оценки 📝'),
            KeyboardButton(text='Домашнее задание 📓'),
        ],
        [
            KeyboardButton(text='Настройки ⚙️'),
        ],
    ]
    if user and user.debug:
        buttons.append([KeyboardButton(text='Команды дебага')])
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return markup


def make_setting_button(user):
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Выдача на неделю' if user.setting_dw else 'Выдача на день'),
                KeyboardButton(
                    text='Уведомления вкл.' if user.setting_notification else 'Уведомления выкл.'
                ),
                KeyboardButton(
                    text='Показать ссылки' if user.setting_hide_link else 'Скрыть ссылки'
                ),
            ],
            [KeyboardButton(text='Назад')],
        ],
    )


def token_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Получить токен',
                    url='https://authedu.mosreg.ru/v2/token/refresh',
                ),
                InlineKeyboardButton(text='Если токена нет', url='https://authedu.mosreg.ru/50'),
            ]
        ]
    )


def make_debug_button():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='Запрос пользователя')],
            [KeyboardButton(text='Выкл. дебаг')],
            [KeyboardButton(text='В главное меню')],
        ],
    )


def username_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Как это сделать?',
                    url='https://silverweb.by/kak-sozdat-nik-v-telegramm.',
                )
            ]
        ]
    )
