from datetime import datetime

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Boolean, Index, JSON, select
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Joke(Base):
    __tablename__ = "jokes"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    text: Mapped[str] = mapped_column(String)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    has_my_like: Mapped[bool] = mapped_column(Boolean, default=False)
    date: Mapped[datetime] = mapped_column(DateTime)
    embedding: Mapped[list[float]] = mapped_column(Vector(2000))

    __table_args__ = (
        Index(
            "jokes_embedding_idx",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_l2_ops"},
        ),
    )

    def __repr__(self) -> str:
        return f"Joke(id={self.id}, text={self.text[:15]}...)"


class ChatSettings(BaseModel):
    enabled: bool = False
    joke_min_likes: int = 0
    joke_max_length: int = 800


class ChatSettingsDB(Base):
    __tablename__ = "chat_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    settings: Mapped[dict] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"ChatSettings(chat_id={self.chat_id})"


if __name__ == "__main__":
    from app.database import get_session

    async def main():
        async with get_session() as session:
            query = select(ChatSettingsDB).where(ChatSettingsDB.chat_id == '1000')
            result = await session.execute(query)
            settings = result.scalar_one_or_none()
            print(settings)

    import asyncio

    asyncio.run(main())
