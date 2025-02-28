from aiogram import Dispatcher

from filters.is_admin import IsAdmin
from .debug import debug_router
from .registration import auth_router
from .unknown import unknown_router
from bin import logger


class Handlers:
    routers = [debug_router, auth_router, unknown_router]

    def __init__(self, dp: Dispatcher):
        self.dp = dp

    def register_all(self):
        self.__register_handlers()
        self.__register_filters()
        # logger.debug('Handlers and filters registered!')

    def __register_handlers(self):
        if self.dp:
            for router in Handlers.routers:
                self.dp.include_router(router)
        else:
            raise AttributeError('The dispatcher was not specified!')

    @staticmethod
    def __register_filters():
        debug_router.message.filter(IsAdmin())
