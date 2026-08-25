import sys
from os import getenv
from typing import Any, ClassVar

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file='.env')

    is_debug: bool = Field(default=False)
    db_path: str = Field(default=...)
    db_backup_path: str = Field(default=...)
    debug_token: str | None = Field(default=None)
    release_token: str = Field(default=...)
    admin_ids: list[int] = Field(default=...)

    @model_validator(mode='before')
    @classmethod
    def set_debug_mode(cls, data: dict[str, Any]) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        if '-d' in sys.argv or getenv('IS_DEV'):
            data['is_debug'] = True
        return data

    @model_validator(mode='after')
    def check_tokens(self) -> 'Config':
        if self.is_debug and not self.debug_token:
            raise ValueError('debug_token is required when is_debug=True')
        return self

    @computed_field
    @property
    def db_url(self) -> str:
        return f'sqlite+aiosqlite:///{self.db_path}'

    @computed_field
    @property
    def token(self) -> str:
        # Thanks to the validator above, debug_token is guaranteed to be str if is_debug=True
        return self.debug_token if self.is_debug else self.release_token  # pyright: ignore[reportReturnType]


config = Config()
