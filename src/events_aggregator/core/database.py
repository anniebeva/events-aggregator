from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from events_aggregator.core.config import settings


DATABASE_URL = (
    f'postgresql+asyncpg://{settings.postgres_username}:'
    f'{settings.postgres_password}@{settings.postgres_host}:'
    f'{settings.postgres_port}/{settings.postgres_database_name}'
)


engine = create_async_engine(DATABASE_URL)


async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with async_session_maker() as session:
        yield session
