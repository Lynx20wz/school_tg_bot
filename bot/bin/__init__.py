__all__ = (
    # Const
    'BD_PATH',
    'BD_BACKUP_PATH',
    'API_BOT',
    'ADMIN_IDS',
    'DEBUG',
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
    'ExpiredToken',
    'NoToken',
    'ServerError',
)

from sys import stdout, exit, argv
from typing import Union

from environs import Env, EnvError
from loguru import logger
from until import *  # Exceptions and buttons


# CONST
DEBUG = True if '-debug' in argv else False
BD_PATH = 'temp/DataBase.db'
BD_BACKUP_PATH = 'temp/BackupDataBase.db'

env = Env()
env.read_env()

log_format = (
    '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'
)

logger.remove()
logger.add(
    sink=stdout,
    format=log_format,
    backtrace=True,
    diagnose=True,
    level='DEBUG' if DEBUG else 'INFO',
    colorize=True,
)
logger.add(format=log_format, sink='temp/log.log', level='INFO', mode='w')

try:
    if DEBUG:
        API_BOT = env.str('DEBUG_BOT')
        logger.debug('Bot is in DEBUG mode')
    else:
        API_BOT = env.str('API_BOT')
    ADMIN_IDS = env.list('ADMIN_IDS', subcast=int)
except EnvError as e:
    logger.exception(f"Environment variables aren't set: {e}")
    exit()


def get_weekday(number: int = None) -> Union[str, list[str]]:
    weekdays = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }
    if not number:
        return list(weekdays.values())
    else:
        return weekdays.get(number)
