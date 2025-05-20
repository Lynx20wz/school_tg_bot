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
    'social_networks_button',
    'username_button',
    # Functions
    'get_weekday',
    'check_response',
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

log_format = (
    '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'
)

logger.remove()
logger.add(
    sink=stdout,
    format=log_format,
    backtrace=True,
    diagnose=True,
    level='DEBUG',
    colorize=True,
)
logger.add(format=log_format, sink='temp/log.log', level='INFO', mode='w')

# CONST
BD_PATH = 'temp/DataBase.db'
BD_BACKUP_PATH = 'temp/BackupDataBase.db'
DEBUG = True if '-debug' in argv else False

env = Env()
env.read_env()

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
        return [name_day for name_day in weekdays.values()]
    else:
        return weekdays.get(number)


def check_response(response) -> dict:
    """Function, which check for token and status code in response.

    Args:
        response (Response): Response from server which need to check
    Returns:
        Server response as a dictionary and raise exceptions
    Raises:
        NoToken: when user doesn't have token
        ExpiredToken: when token is expired
        ServerError: when request failed for other reasons
    """
    if response.status_code == 401:
        logger.warning(f'Срок действия токена истёк!: {response.status_code}\n{response.text}')
        raise ExpiredToken()
    elif response.status_code >= 400:
        logger.warning(f'Произошла ошибка: {response.status_code}\n{response.text}')
        raise ServerError()
    else:
        return response.json()
