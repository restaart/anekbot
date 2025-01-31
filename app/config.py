from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

root_path = Path(__file__).parent.parent


class Settings(BaseSettings):
    TG_TOKEN: str
    BOT_NAME: str
    ADMIN_USERNAMES: list[str]
    OPENAI_TOKEN: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    DATABASE_URL: PostgresDsn

    model_config = {
        "env_file": str(root_path / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
