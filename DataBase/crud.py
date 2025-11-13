from datetime import datetime, timedelta
from pickletools import int4
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from bot.config import logger
from DataBase.database import Base, engine, sm
from DataBase.models import *


class DataBaseCrud:
    """Interface to the database."""

    def __init__(self, engine=engine, session_maker=sm):
        self.engine = engine
        self.session_maker = session_maker

    async def __call__(self, userid: Optional[int] = None) -> None | UserModel | list[UserModel]:
        return await self.get_user(userid)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Users
    async def add_user(self, user: UserModel):
        """Adds a user to the database if the user isn't there."""
        async with self.session_maker() as session:
            if not (await session.execute(select(UserModel).filter_by(userid=user.userid))).first():
                session.add(user)
                await session.commit()
                logger.debug(f'User {user.username} has been added to the database!')

    async def get_user(self, userid: Optional[int] = None) -> None | UserModel | list[UserModel]:
        """Returns a user from the database if username, else returns all users.

        Args:
            userid: ID of the user who you want to get

        Returns:
            user by userid as UserModel if userid,
            else all users in the database as list[UserModel].
        """
        async with self.session_maker() as session:
            if userid:
                return await session.scalar(select(UserModel).filter_by(userid=userid))
            else:
                return list((await session.execute(select(UserModel))).scalars().all())

    async def update_user(self, user: UserModel, changes: Optional[tuple[str, ...]] = None):
        """Updates a user in the database.

        Args:
            user: User for update
            changes: Name of fields to be updated
        """
        async with self.session_maker() as session:
            if not changes:
                changes_dict = {
                    attr: getattr(user, attr)
                    for attr in user.__dict__
                    if attr in UserModel.__table__.columns
                }
            else:
                changes_dict = {attr: getattr(user, attr) for attr in changes}
            await session.execute(
                update(UserModel).filter_by(userid=user.userid).values(**changes_dict)
            )
            await session.commit()

    async def delete_user(self, userid: int):
        """Deletes a user from the database. Also deletes a user's homework if no one else refers to it."""
        async with self.session_maker() as session:
            try:
                query = select(UserModel).filter_by(userid=userid)
                user = (await session.execute(query)).scalar_one()
                homework = user.homework
                await session.delete(user)
                if not homework.users:
                    await session.delete(homework)
                await session.commit()
            except NoResultFound:
                logger.warning(f'User with ID {userid} does not exist in the database!')
                await session.rollback()

    # Homework
    async def add_homework(self, userid: int, homework: HomeworkWeekModel):
        async with self.session_maker() as session:
            try:
                user = await session.get(UserModel, userid)
                if not user:
                    raise NoResultFound

                logger.debug(f'{homework.begin}, {homework.end}, {homework.timestamp}')
                user.homework = homework
                await session.commit()
            except NoResultFound:
                logger.warning(f'User with ID {userid} does not exist in the database!')
                await session.rollback()

    async def get_homework(self, userid: int) -> HomeworkWeekModel | None:
        async with self.session_maker() as session:
            try:
                query = select(UserModel).filter_by(userid=userid)
                user = (await session.execute(query)).one()
                if (datetime.now() - user.homework.timestamp) < timedelta(hours=1):
                    return user.homework
                else:
                    await session.delete(user.homework)
                    return None
            except NoResultFound:
                logger.warning(f"User with ID {userid} doesn't have homework!")
                await session.rollback()
                return None
