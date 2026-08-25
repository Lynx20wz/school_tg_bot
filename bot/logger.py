__all__ = ('logger',)

from sys import stdout

from loguru import logger

from bot.config import config

log_format: str = (
    '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'
)


logger.remove()
logger.add(
    sink=stdout,
    format=log_format,
    level='DEBUG' if config.is_debug else 'INFO',
    colorize=True,
)
logger.add(format=log_format, sink='temp/log.log', level='INFO', mode='w')
