from pathlib import Path

from pydantic import PostgresDsn, BaseModel, PositiveInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

root_path = Path(__file__).parent.parent


class DatabaseSettings(BaseModel):
    DSN: PostgresDsn = Field(description="PostgreSQL connection string")
    pool_size: PositiveInt = Field(
        default=20, description="Number of connections to keep open"
    )
    pool_max_overflow: int = Field(
        default=10, description="Maximum overflow connections allowed"
    )
    pool_timeout: PositiveInt = Field(
        default=30, description="Connection timeout in seconds", gt=0
    )
    pool_recycle: PositiveInt = Field(
        default=1800, description="Connection recycle time in seconds", gt=300
    )


class Settings(BaseSettings):
    tg_token: str = Field(description="Telegram Bot API token")
    admin_usernames: list[str] = Field(
        description="List of Telegram usernames with admin access"
    )
    openai_token: str = Field(description="OpenAI API token")
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="Name of the OpenAI embedding model to use",
    )
    embedding_vector_size: int = Field(
        default=2000, description="Size of the embedding vectors produced by the model"
    )
    database: DatabaseSettings = Field(description="Database connection settings")

    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
    )


import os

os.environ.setdefault("ENV_FILE", str(root_path / ".env"))

settings = Settings(_env_file=os.environ["ENV_FILE"])
