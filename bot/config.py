__all__ = ('config', 'logger')

from sys import argv, stdout

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    DEBUG: bool = True if '-debug' in argv else False
    DB_PATH: str
    DB_BACKUP_PATH: str

    DEBUG_TOKEN: str
    RELEASE_TOKEN: str

    ADMIN_IDS: list[int]

    @property
    def DB_URL(self) -> str:  # noqa: N802
        return f'sqlite+aiosqlite:///{self.DB_PATH}'

    @property
    def TOKEN(self) -> str:  # noqa: N802
        return self.DEBUG_TOKEN if self.DEBUG else self.RELEASE_TOKEN


config = Config()  # pyright: ignore[reportCallIssue]


log_format: str = (
    '{time:H:mm:ss} | "{function}" | {line} ({module}) | <level>{level}</level> | {message}'
)

logger.remove()
logger.add(
    sink=stdout,
    format=log_format,
    backtrace=True,
    diagnose=True,
    level='DEBUG' if config.DEBUG else 'INFO',
    colorize=True,
)
logger.add(format=log_format, sink='temp/log.log', level='INFO', mode='w')
