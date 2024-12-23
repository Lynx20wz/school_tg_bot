__all__ = ('debug_router', 'auth_router', 'unknown_router')

from .debug import debug_router
from .registration import auth_router
from .unknown import unknown_router
