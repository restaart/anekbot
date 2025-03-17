import asyncio
import os
import pickle
from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import patch, AsyncMock, Mock

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.postgres import PostgresContainer

PROJECT_ROOT = Path(__file__).parent.parent
os.environ["ENV_FILE"] = str(PROJECT_ROOT / "tests" / ".env-test")

from app.config import settings
from app.bot_state import BOT_STATE
from app.database import get_session


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


@pytest.fixture(scope="session")
async def postgres_container():
    container = PostgresContainer("pgvector/pgvector:pg17", driver="asyncpg")
    container.with_bind_ports(5432, 50432)
    with container as postgres:
        settings.database.DSN = postgres.get_connection_url().replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        yield postgres


@pytest.fixture(scope="session")
async def database_container(postgres_container):
    alembic_cfg = Config(PROJECT_ROOT / "alembic.ini")

    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database.DSN))
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    yield postgres_container


# @pytest.fixture(scope="session")
# async def db_engine(database):
#     engine = create_async_engine(str(settings.database.DSN), echo=False)
#     alembic_cfg = Config(PROJECT_ROOT / "alembic.ini")
#
#     alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database.DSN))
#     alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
#
#     loop = asyncio.get_running_loop()
#     await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
#     try:
#         yield engine
#     finally:
#         await engine.dispose()
#
#
@pytest.fixture
async def db_session(database_container) -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def mock_state():
    BOT_STATE["me"] = Mock(username="bot")
