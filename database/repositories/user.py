from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.logger import logger
from database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: User) -> User:
        """Adds a user to the database."""
        self._session.add(user)
        logger.info(f'User {user.userid} has been added to the database!')
        await self._session.flush()
        return user

    async def get(self, userid: int) -> None | User:
        """Returns a user from the database by userid."""
        return await self._session.scalar(select(User).where(User.userid == userid))

    async def get_all(self) -> list[User]:
        """Returns all users in the database."""
        return list((await self._session.execute(select(User))).scalars().all())

    async def update(self, userid: int, **changes) -> None:
        """Updates a user in the database.

        Args:
            userid: User ID for update
            **changes: Field names and their new values to update
        """
        if not changes:
            return

        await self._session.execute(update(User).where(User.userid == userid).values(**changes))
        await self._session.flush()

    async def update_settings(
        self,
        user: User,
        debug: bool | None = None,
        setting_dw: bool | None = None,
        setting_notifications: bool | None = None,
        setting_hide_link: bool | None = None,
    ):
        settings = user._settings

        if debug is not None:
            settings = (settings | 0b01000) if debug else (settings & ~0b01000)

        if setting_dw is not None:
            settings = (settings | 0b00001) if setting_dw else (settings & ~0b00001)

        if setting_notifications is not None:
            settings = (settings | 0b00010) if setting_notifications else (settings & ~0b00010)

        if setting_hide_link is not None:
            settings = (settings | 0b00100) if setting_hide_link else (settings & ~0b00100)

        user._settings = settings

    async def delete(self, userid: int):
        """Deletes a user from the database. Also deletes a user's homework if no one else refers to it."""
        try:
            query = select(User).where(User.userid == userid)
            user: User = (await self._session.execute(query)).scalar_one()
            homework = user.homework
            await self._session.delete(user)
            if not homework.users:
                await self._session.delete(homework)
        except NoResultFound:
            logger.warning(f'User with ID {userid} does not exist in the database!')
            # await self._session.rollback()
