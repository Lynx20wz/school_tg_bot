import logging

from environs import *
from sys import stdout, _getframe, exit
from loguru import logger

env = Env()

env.read_env()

try:
    BD_PATH = env.str('BD_PATH')
    API_BOT = env.str('API_BOT')
    ADMIN_IDS = env.list('ADMIN_IDS', subcast=int)
except EnvError as e:
    logger.exception(f'Переменные окружения не заданы: {e}')
    exit()

log_format = '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'

# class InterceptHandler(logging.Handler):
#     def emit(self, record):
#         try:
#             level = logger.level(record.levelname).name
#         except ValueError:
#             level = record.levelno
#
#         frame, depth = _getframe(6), 6
#         while frame and frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1
#
#         logger.opt(depth=depth, exception=record.exc_info, colors=True).log(level, record.getMessage())

# logging.basicConfig(handlers=[InterceptHandler()], level=20, force=True)
logger.remove()
logger.add(
        sink=stdout,
        format=log_format,
        backtrace=True,
        diagnose=True,
        level='DEBUG',
        colorize=True
)
logger.add(
        format=log_format,
        sink='..//temp//log.log',
        level='INFO',
        mode='w',
)

__all__ = ['BD_PATH', 'API_BOT', 'ADMIN_IDS', 'logger']
