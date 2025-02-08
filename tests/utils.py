# alembic_runner.py
import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.config import settings  # adjust the import to your settings

PROJECT_ROOT = Path(__file__).parent.parent


async def run_async_migrations():
    """Run Alembic migrations by instantiating a fresh Config."""
    # Create an Alembic Config, pointing to your alembic.ini file.
    alembic_cfg = Config(PROJECT_ROOT / "alembic.ini")
    # Update the sqlalchemy.url to use the current settings
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_DSN))
    alembic_cfg.set_main_option(
        "script_location", str(PROJECT_ROOT / "migrations")
    )  # Path to your migrations folder

    # Run the upgrade command in a thread to avoid blocking the event loop.
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
