from contextlib import asynccontextmanager
from functools import cache

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


@cache
def get_engine():
    settings = get_settings()
    return create_async_engine(
        str(settings.database.DSN),
        echo=False,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.pool_max_overflow,
        pool_timeout=settings.database.pool_timeout,
        pool_recycle=settings.database.pool_recycle,
    )


@cache
def get_session_maker():
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


@asynccontextmanager
async def get_session():
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass
