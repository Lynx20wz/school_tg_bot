__all__ = (
    # Self
    'BD_PATH',
    'BD_BACKUP_PATH',
    'API_BOT',
    'ADMIN_IDS',
    'logger',
    # KeyBoards
    'username_button',
    'main_button',
    'make_setting_button',
    'token_button',
    'make_debug_button',
    'social_networks_button',
    'username_button',
    # Exceptions
    'ExpiredToken',
    'NoToken',
    'ServerError',
    # Classes
    'UserClass',
    'BaseDate',
    'db'
)

from sys import stdout, exit

from environs import Env, EnvError
from loguru import logger
from until import *

env = Env()

env.read_env()

try:
    BD_PATH = env.str('BD_PATH')
    BD_BACKUP_PATH = env.str('BD_BACKUP_PATH')
    API_BOT = env.str('API_BOT')
    ADMIN_IDS = env.list('ADMIN_IDS', subcast=int)
except EnvError as e:
    logger.exception(f'Переменные окружения не заданы: {e}')
    exit()

log_format = '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'

logger.remove()
logger.add(
        sink=stdout,
        format=log_format,
        backtrace=True,
        diagnose=True,
        level='DEBUG',
        colorize=True,
)
logger.add(format=log_format, sink='temp//log.log', level='INFO', mode='w')

# To avoid cyclical imports
from classes import *
