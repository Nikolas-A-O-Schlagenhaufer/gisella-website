from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import email_length, image_file_length, title_length, username_length
from app.db import Base


class User(Base):
    __tablename__: str = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    username: Mapped[str] = mapped_column(
        String(username_length), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(email_length), unique=True, nullable=False
    )
    image_file: Mapped[str | None] = mapped_column(
        String(image_file_length), nullable=True, default=None
    )
    posts: Mapped[list[Post]] = relationship(back_populates="author")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__: str = "post"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    title: Mapped[str] = mapped_column(String(title_length), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC)
    )

    author: Mapped[User] = relationship(back_populates="posts")
