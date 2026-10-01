import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = "sqlite+aiosqlite:///./ncert_engine.db"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Create all database tables.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Provide a database session to FastAPI endpoints.
    """

    async with AsyncSessionLocal() as session:
        yield session