from aiogram.types import Message

from database.models import User
from database.repositories.user import UserRepository


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def add(self, user: User):
        user_db = await self.repo.get(user.userid)
        if user_db is not None:
            return
        await self.repo.add(user)

    async def get(self, userid: int) -> User | None:
        return await self.repo.get(userid)

    async def get_or_create(self, userid: int) -> User:
        if user := await self.repo.get(userid):
            return user
        return await self.repo.add(User(userid))

    async def set_reg_data(self, userid: int, token: str, student_id: int):
        user = await self.repo.get(userid)
        if user is not None:
            await self.repo.update(userid, token=token, student_id=student_id)
        else:
            await self.repo.add(User(userid, token=token, student_id=student_id))

    async def update_settings(
        self,
        user: User,
        debug: bool | None = None,
        dw: bool | None = None,
        notifications: bool | None = None,
        hide_link: bool | None = None,
    ):
        if user is not None:
            await self.repo.update_settings(
                user,
                debug=debug,
                setting_dw=dw,
                setting_notifications=notifications,
                setting_hide_link=hide_link,
            )
