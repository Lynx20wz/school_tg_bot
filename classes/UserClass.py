import asyncio
from functools import wraps
from typing import Optional, Union, Tuple, Callable
from typing import TypeVar, ParamSpec

from aiogram.types import Message

from bin import username_button
from bin.config import logger
from classes.BaseDate import db

T = TypeVar('T')
P = ParamSpec('P')


class UserClass:
    users = []

    def __init__(
        self,
        username: str,
        userid: int,
        debug: bool = False,
        setting_dw: bool = False,
        setting_notification: bool = True,
        token: str = None,
        student_id: int = None,
        homework_id: int = None,
    ):
        """
        Инициализирует объект user_class.

        :param username: Имя пользователя.
        :param userid: ID пользователя.
        :param debug: Флаг отладки.
        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        :param token: Токен авторизации пользователя.
        :param student_id: ID студента.
        :param homework_id: ID домашнего задания.
        """

        self.username = username
        self.userid = userid
        self.debug = debug
        self.setting_dw = setting_dw
        self.setting_notification = setting_notification
        self.data = (username, userid, setting_dw, setting_notification, debug)
        self.token = token
        self.student_id = student_id
        self.homework_id = homework_id

        asyncio.create_task(db.add_user((username, userid, debug, setting_dw, setting_notification)))

        async def update_existing_user():
            existing_user = await self.get_user_from_massive(username, 2)
            if not existing_user:
                self.users.append(self)

        asyncio.create_task(update_existing_user())

    @classmethod
    async def get_user_from_massive(cls, username: str, mode: int = 1) -> Optional[Union[Tuple[str, int, bool, bool, bool], 'UserClass', int]]:
        """
        Получает пользователя из списка пользователей.

        :param username: Имя пользователя.
        :param mode: Режим возвращаемых данных.
        :return: Возвращает данные пользователя из массива users в зависимости от режима.
         Если пользователь не найден в массиве, то None.
        """
        for i, user in enumerate(cls.users):
            if user.username == username:
                match mode:
                    case 1:
                        return await user.data
                    case 2:
                        return user
                    case 3:
                        return i
        return None

    @staticmethod
    def get_user():
        """
        Возвращает пользователя из кэша.
        :return: Возвращает функцию-обёртку для получения пользователя.
        """

        def wrapper(func: Callable[P, T]):
            @wraps(func)
            async def wrapped(message: Union[Message, UserClass], *args, **kwargs):
                if isinstance(message, UserClass):
                    user = message
                else:
                    existing_user = await UserClass.get_user_from_massive(message.from_user.username, 2)
                    if existing_user:
                        user = existing_user
                    else:
                        user_db = await db(message.from_user.username)
                        logger.debug(f"{user_db} - {func.__name__}")
                        if user_db is not None:
                            try:
                                user = UserClass(
                                        message.from_user.username,
                                        message.from_user.id,
                                        user_db.get('debug', False),
                                        user_db.get('setting_dw', True),
                                        user_db.get('setting_notification', True),
                                        user_db.get('token'),
                                        user_db.get('homework'),
                                )
                            except AttributeError:
                                await message.answer(
                                        'У вас отсутствует имя пользователя! Пожалуйста добавьте его в настройках аккаунта.',
                                        reply_markup=username_button()
                                )
                                return
                        else:
                            user = UserClass(message.from_user.username, message.from_user.id)

                return await func(message=message, user=user, *args, **kwargs)

            return wrapped

        return wrapper

    async def save_settings(
        self, *, setting_dw: bool = None, setting_notification: bool = None, debug: bool = None, save_db: bool = False
    ):
        """
        Сохраняет настройки пользователя.

        :param setting_dw: Флаг настройки уведомлений.
        :param setting_notification: Флаг уведомлений.
        :param debug: Флаг отладки.
        :param save_db: Если True, то настройки будут обновленный не только в массиве пользователей,
        а также и в БД.
        """
        if setting_dw is None:
            setting_dw = self.setting_dw
        if setting_notification is None:
            setting_notification = self.setting_notification
        if debug is None:
            debug = self.debug

        self.setting_dw = setting_dw
        self.setting_notification = setting_notification
        self.debug = debug

        user_index = await self.get_user_from_massive(self.username, 3)
        if user_index is not None:
            UserClass.users[user_index].setting_dw = setting_dw
            UserClass.users[user_index].setting_notification = setting_notification
            UserClass.users[user_index].debug = debug

        if save_db:
            asyncio.create_task(db.update_user(self))
            logger.info(f'Новые настройки пользователя {self.username} сохранены!')
