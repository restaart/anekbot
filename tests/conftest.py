import asyncio
import os
import pickle
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock, Mock

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from app.config import Settings

PROJECT_ROOT = Path(__file__).parent.parent


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
    os.environ["TG_TOKEN"] = "123"
    os.environ["ADMIN_USERNAMES"] = '["user"]'
    os.environ["EMBEDDING_MODEL"] = "text-embedding-3-large"
    os.environ["OPENAI_TOKEN"] = "sk-asd"
    os.environ["DATABASE__DSN"] = "postgresql+asyncpg://test:test@localhost:5432/test"
    test_settings = Settings()
    get_test_settings = lambda: test_settings
    with patch("app.config.get_settings", new=get_test_settings):
        yield test_settings


@pytest.fixture(scope="session")
async def postgres_container(test_settings):
    with PostgresContainer("pgvector/pgvector:pg17", driver="asyncpg") as postgres:
        test_settings.database.DSN = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        yield postgres


@pytest.fixture(scope="session")
async def db_engine(postgres_container, test_settings: Settings):
    engine = create_async_engine(str(test_settings.database.DSN), echo=False)
    alembic_cfg = Config(PROJECT_ROOT / "alembic.ini")

    alembic_cfg.set_main_option("sqlalchemy.url", str(test_settings.database.DSN))
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
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
