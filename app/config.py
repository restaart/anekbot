from pathlib import Path

from pydantic import PostgresDsn, BaseModel, PositiveInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

root_path = Path(__file__).parent.parent


class DatabaseSettings(BaseModel):
    DSN: PostgresDsn
    pool_size: PositiveInt = Field(
        default=20,
        description="Number of connections to keep open"
    )
    pool_max_overflow: int = Field(
        default=10,
        description="Maximum overflow connections allowed"
    )
    pool_timeout: PositiveInt = Field(
        default=30,
        description="Connection timeout in seconds",
        gt=0
    )
    pool_recycle: PositiveInt = Field(
        default=1800,
        description="Connection recycle time in seconds",
        gt=300
    )

class Settings(BaseSettings):
    tg_token: str
    admin_usernames: list[str]
    openai_token: str
    embedding_model: str = "text-embedding-3-large"
    embedding_vector_size: int = 2000
    database: DatabaseSettings

    model_config = SettingsConfigDict(
        extra="ignore",
        env_nested_delimiter="__",
    )


settings = Settings(_env_file=str(root_path / ".env"))
