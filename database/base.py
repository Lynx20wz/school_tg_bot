__all__ = ('engine', 'sm', 'Base')

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from bot.config import config

engine = create_async_engine(
    url=config.db_url,
    echo=False,
    # pool_size=5,
    # max_overflow=10,
)

sm = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
