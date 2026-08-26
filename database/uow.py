from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database import sm
from database.repositories import HomeworkRepository, UserRepository
from database.services import HomeworkService, UserService


class UnitOfWork:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession] = sm):
        self.session_maker = session_maker
        self.session: AsyncSession | None = None

        self.users: UserService | None = None
        self.homework: HomeworkService | None = None

    async def __aenter__(self) -> 'UnitOfWork':
        self.session = self.session_maker()

        user_repo = UserRepository(self.session)
        hk_repo = HomeworkRepository(self.session)

        self.users = UserService(user_repo)
        self.homework = HomeworkService(hk_repo)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()
