__all__ = (
    'main_kb',
    'settings_kb',
    'token_kb',
    'debug_kb',
    'username_kb',
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.classes import User


def main_kb(user: User) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder(
        [
            [
                KeyboardButton(text='Расписание 📅'),
                KeyboardButton(text='Оценки 📝'),
                KeyboardButton(text='Домашнее задание 📓'),
            ],
            [
                KeyboardButton(text='Настройки ⚙️'),
            ],
        ]
    )

    if user and user.debug:
        kb.add(KeyboardButton(text='Команды дебага'))
    return kb.as_markup()


def settings_kb(user: User) -> ReplyKeyboardMarkup:
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


token_kb = InlineKeyboardMarkup(
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


debug_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='Запрос пользователя')],
        [KeyboardButton(text='Выкл. дебаг')],
        [KeyboardButton(text='В главное меню')],
    ],
)


username_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Как это сделать?',
                url='https://silverweb.by/kak-sozdat-nik-v-telegramm.',
            )
        ]
    ]
)
