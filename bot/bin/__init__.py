__all__ = (
    # Const
    'config',
    'logger',
    # KeyBoards
    'username_button',
    'main_button',
    'make_setting_button',
    'token_button',
    'make_debug_button',
    'username_button',
    # Functions
    'get_weekday',
    # Exceptions
    'ExpiredTokenError',
    'NoTokenError',
    'ServerError',
)


from loguru import logger

from bot.config import config
from bot.until import *  # Exceptions and KeyBoards


def get_weekday(number: int | None = None) -> str | list[str]:
    weekdays = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }
    if number is None:
        return list(weekdays.values())
    elif number in range(1, 8):
        return weekdays[number]
    else:
        raise ValueError('Wrong number of the day of the week!')
