from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

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
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))

    def __repr__(self) -> str:
        return f"Post(id={self.id}, external_id={self.external_id})"
