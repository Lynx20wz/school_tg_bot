__all__ = ('debug_router', 'auth_router', 'unknown_router', 'data_get_router', 'settings_router')

from .debug import debug_router
from .registration import auth_router
from .unknown import unknown_router
from .data_get import data_get_router
from .settings import settings_router