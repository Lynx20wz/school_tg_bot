__all__ = (
    # Const
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

# CONST
BD_PATH = 'temp/DataBase.db'
BD_BACKUP_PATH = 'temp/BackupDataBase.db'

env = Env()
env.read_env()

try:
    API_BOT = env.str('API_BOT')
    ADMIN_IDS = env.list('ADMIN_IDS', subcast=int)
except EnvError as e:
    logger.exception(f"Environment variables aren't set: {e}")
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
logger.add(format=log_format, sink='temp/log.log', level='INFO', mode='w')

# To avoid cyclical imports
from bot.classes import *
