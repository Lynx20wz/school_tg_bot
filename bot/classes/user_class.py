import asyncio
from typing import Optional, Union

from aiogram.types import Message

from bot.bin import logger
from DataBase.crud import DataBaseCrud
from DataBase.models import UserModel

from .parser import Parser
from .serialization_mixin import SerializationMixin

db = DataBaseCrud()


class UserClass(SerializationMixin):
    model = UserModel

    def __init__(
        self,
        userid: int,
        username: str,
        debug: Optional[bool] = False,
        setting_dw: Optional[bool] = False,
        setting_notification: Optional[bool] = True,
        setting_hide_link: Optional[bool] = True,
        token: Optional[str] = None,
        student_id: Optional[int] = None,
        homework_id: Optional[int] = None,
        **kwargs,
    ):
        """Initializes the user_class object.

        Args:
            userid (int): The ID of the user.
            username (str): The username of the user.
            debug (bool, optional): A flag indicating whether to enable debug mode. Defaults to False.
            setting_dw (bool, optional): A flag indicating whether to enable delivery notifications. Defaults to False.
            setting_notification (bool, optional): A flag indicating whether to enable notifications. Defaults to True.
            setting_hide_link (bool, optional): A flag indicating whether to hide links. Defaults to True.
            token (str, optional): The authentication token for the user. Defaults to None.
            student_id (int, optional): The ID of the student. Defaults to None.
            homework_id (int, optional): The ID of the homework. Defaults to None.
            kwargs: Additional keyword arguments.
        """
        super().__init__()
        self.userid = userid
        self.username = username
        self.debug = debug
        self.setting_dw = setting_dw
        self.setting_notification = setting_notification
        self.setting_hide_link = setting_hide_link
        self.data = (
            userid,
            username,
            setting_dw,
            setting_notification,
            setting_hide_link,
            debug,
        )

        self.parser = Parser(token, student_id)
        self._token = token
        self.student_id = student_id
        self.homework_id = homework_id

        asyncio.create_task(db.add_user(self.to_model()))

    @staticmethod
    async def get_user(message: Union[Message, 'UserClass']):
        if isinstance(message, UserClass):
            return message
        else:
            user_db = await db(message.from_user.id)
            if user_db is not None:
                return UserClass.from_model(user_db)
            else:
                return UserClass(message.from_user.id, message.from_user.username)

    async def save_settings(
        self,
        *,
        setting_dw: Optional[bool] = None,
        setting_notification: Optional[bool] = None,
        setting_hide_link: Optional[bool] = None,
        debug: Optional[bool] = None,
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

        await db.update_user(self)  # type: ignore
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
