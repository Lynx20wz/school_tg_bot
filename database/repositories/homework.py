from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from database import User
from database.models import HomeworkWeekModel


class HomeworkRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, userid: int, homework: HomeworkWeekModel):
        try:
            user = await self._session.get(User, userid)
            if not user:
                raise NoResultFound

            logger.debug(f'{homework.begin}, {homework.end}, {homework.timestamp}')
            user.homework = homework
            await self._session.commit()
        except NoResultFound:
            logger.warning(f'User with ID {userid} does not exist in the database!')
            await self._session.rollback()

    async def get(self, userid: int) -> HomeworkWeekModel | None:
        try:
            query = select(User).filter_by(userid=userid)
            user: User = (await self._session.execute(query)).scalar_one()
            if (datetime.now() - datetime.fromisoformat(user.homework.timestamp)) < timedelta(
                hours=1
            ):
                return user.homework
            else:
                await self._session.delete(user.homework)
                return None
        except NoResultFound:
            logger.warning(f"User with ID {userid} doesn't have homework!")
            await self._session.rollback()
            return None
