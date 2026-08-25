import asyncio
from typing import Any

from aiogram.types import Message

from bot.logger import logger
from database import DataBaseCrud, UserModel

from .parser import Parser
from .serialization_mixin import SerializationMixin

db = DataBaseCrud()


class User(SerializationMixin):
    model: type = UserModel

    def __init__(
        self,
        userid: int,
        username: str,
        debug: bool | None = False,
        setting_dw: bool | None = False,
        setting_notification: bool | None = True,
        setting_hide_link: bool | None = True,
        token: str | None = None,
        student_id: int | None = None,
        homework_id: int | None = None,
        **kwargs: dict[str, Any],
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
        self.userid: int = userid
        self.username: str = username
        self.debug: bool | None = debug
        self.setting_dw: bool | None = setting_dw
        self.setting_notification: bool | None = setting_notification
        self.setting_hide_link: bool | None = setting_hide_link
        self.data: tuple[int, str, bool | None, bool | None, bool | None, bool | None] = (
            userid,
            username,
            setting_dw,
            setting_notification,
            setting_hide_link,
            debug,
        )

        self.parser: Parser = Parser(token, student_id)
        self._token: str | None = token
        self._student_id: int | None = student_id
        self.homework_id: int | None = homework_id

        asyncio.create_task(db.add_user(self.to_model()))

    @staticmethod
    async def get_user(message: Message | User):
        if isinstance(message, User):
            return message
        else:
            user_db = await db(message.from_user.id)
            if user_db is not None:
                return User.from_model(user_db)
            else:
                return User(message.from_user.id, message.from_user.username)

    async def save_settings(
        self,
        *,
        setting_dw: bool | None = None,
        setting_notification: bool | None = None,
        setting_hide_link: bool | None = None,
        debug: bool | None = None,
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
    def token(self) -> str | None:
        return self._token

    @token.setter
    def token(self, value: str):
        self._token = value
        self.parser.token = value

    @property
    def student_id(self) -> int | None:
        return self._student_id

    @student_id.setter
    def student_id(self, value: int):
        self._student_id = value
        self.parser.student_id = value
