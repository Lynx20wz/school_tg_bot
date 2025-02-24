__all__ = ('BD_PATH', 'BD_BACKUP_PATH', 'API_BOT', 'ADMIN_IDS', 'logger')

from sys import stdout, exit

from environs import Env, EnvError
from loguru import logger

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
