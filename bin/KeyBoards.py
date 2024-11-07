from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_button(user):
    btns = [
        [
            KeyboardButton(text='Расписание 📅'),
            KeyboardButton(text='Домашнее задание 📓')
        ],
        [
            KeyboardButton(text='Соц. сети класса 💬'),
            KeyboardButton(text='Настройки ⚙️')
        ],
    ]
    if user and user.debug:
        btns.append([KeyboardButton(text='Команды дебага')])
    murkup = ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)
    return murkup


def make_setting_button(user):
    return ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[
                [
                    KeyboardButton(text='Выдача на неделю' if user.setting_dw else 'Выдача на день'),
                    KeyboardButton(text='Уведомления вкл.' if user.setting_notification else 'Уведомления выкл.')
                ],
                [KeyboardButton(text='Назад')],
            ]
    )
