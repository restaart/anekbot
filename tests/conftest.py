import asyncio
import pickle
from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from app.config import Settings
from tests.utils import run_async_migrations, PROJECT_ROOT


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def mock_embeddings():
    emb_file_path = PROJECT_ROOT / "tests" / "test_data" / "precomputed_embeddings.pkl"
    with open(str(emb_file_path), "rb") as f:
        emb = pickle.load(f)

    async def fake_get_embedding(input, *args, **kwargs):
        try:
            return Mock(data=[Mock(embedding=emb[input])])
        except KeyError:
            raise Exception(
                f"No precomputed embeddings for {input}. Modify 'generate_test_data.py' and regenerate."
            )

    with patch(
        "openai.resources.embeddings.AsyncEmbeddings.create",
        AsyncMock(side_effect=fake_get_embedding),
    ) as m:
        yield m


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    test_settings = Settings(
        TG_TOKEN="123",
        ADMIN_USERNAMES=["user"],
        OPENAI_TOKEN="123",
        DATABASE_URL="postgresql+asyncpg://test:test@localhost:5432/test",
    )
    with patch("app.config.settings", new=test_settings):
        yield test_settings


@pytest.fixture(scope="session")
async def postgres_container(test_settings):
    with PostgresContainer("pgvector/pgvector:pg17", driver="asyncpg") as postgres:
        test_settings.DATABASE_DSN = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        yield postgres


@pytest.fixture(scope="session")
async def db_engine(postgres_container, test_settings):
    engine = create_async_engine(str(test_settings.DATABASE_DSN), echo=False)
    await run_async_migrations()
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
