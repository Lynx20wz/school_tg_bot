import asyncio
from functools import wraps
from typing import Union, Callable, Optional

from aiogram.types import Message

from bot.bin import username_button, logger
from .BaseDate import BaseDate
from .Parser import Parser

db = BaseDate()

class UserClass:
    def __init__(
        self,
        username: str,
        userid: int,
        debug: Optional[bool] = False,
        setting_dw: Optional[bool] = False,
        setting_notification: Optional[bool] = True,
        setting_hide_link: Optional[bool] = True,
        token: Optional[str] = None,
        student_id: Optional[int] = None,
        homework_id: Optional[int] = None,
    ):
        """Initializes the user_class object.

        Args:
            username (str): The username of the user.
            userid (int): The ID of the user.
            debug (bool, optional): A flag indicating whether to enable debug mode. Defaults to False.
            setting_dw (bool, optional): A flag indicating whether to enable delivery notifications. Defaults to False.
            setting_notification (bool, optional): A flag indicating whether to enable notifications. Defaults to True.
            setting_hide_link (bool, optional): A flag indicating whether to hide links. Defaults to True.
            token (str, optional): The authentication token for the user. Defaults to None.
            student_id (int, optional): The ID of the student. Defaults to None.
            homework_id (int, optional): The ID of the homework. Defaults to None.
        """
        self.username = username
        self.userid = userid
        self.debug = debug
        self.setting_dw = setting_dw
        self.setting_notification = setting_notification
        self.setting_hide_link = setting_hide_link
        self.data = (
            username,
            userid,
            setting_dw,
            setting_notification,
            setting_hide_link,
            debug,
        )

        self.parser = Parser(token, student_id)
        self._token = token
        self.student_id = student_id
        self.homework_id = homework_id

        asyncio.create_task(
            db.add_user(
                (
                    username,
                    userid,
                    debug,
                    setting_dw,
                    setting_notification,
                    setting_hide_link,
                )
            )
        )

    @staticmethod
    def get_user():
        """The function returns the user from the database.

        Returns:
            Function-wrapper for getting user
        """

        def wrapper(func: Callable):
            @wraps(func)
            async def wrapped(message: Union[Message, UserClass], *args, **kwargs):
                if isinstance(message, UserClass):
                    user = message
                else:
                    user_db = await db(message.from_user.username)
                    if user_db is not None:
                        try:
                            user = UserClass(
                                message.from_user.username,
                                message.from_user.id,
                                user_db.get('debug', False),
                                user_db.get('setting_dw', False),
                                user_db.get('setting_notification', True),
                                user_db.get('setting_hide_link', True),
                                user_db.get('token'),
                                user_db.get('student_id'),
                                user_db.get('homework'),
                            )
                        except AttributeError:
                            await message.answer(
                                'У вас отсутствует имя пользователя! Пожалуйста добавьте его в настройках аккаунта.',
                                reply_markup=username_button(),
                            )
                            return None
                    else:
                        user = UserClass(message.from_user.username, message.from_user.id)

                return await func(message=message, user=user, *args, **kwargs)
            return wrapped
        return wrapper

    async def save_settings(
        self,
        *,
        setting_dw: bool = None,
        setting_notification: bool = None,
        setting_hide_link: bool = None,
        debug: bool = None,
    ):
        """The function saves user settings.

        Args:
            setting_dw (bool): The flag for the delivery notification
            setting_notification (bool): The flag for notifications
            setting_hide_link (bool): The flag for hiding links
            debug (bool): The flag for debugging
            but also in the database
        """
        self.setting_dw = setting_dw or self.setting_dw
        self.setting_notification = setting_notification or self.setting_notification
        self.setting_hide_link = setting_hide_link or self.setting_hide_link
        self.debug = debug or self.debug

        asyncio.create_task(db.update_user(self))
        logger.debug(f'The new settings for user {self.username} have been saved!')

    def check_token(self) -> bool:
        return self._token is not None and self.student_id is not None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value
        self.parser.token = value

    @property
    def student_id(self):
        return self._student_id

    @student_id.setter
    def student_id(self, value):
        self._student_id = value
        self.parser.student_id = value
