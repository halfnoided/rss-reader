from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from database import Base

# TODO: move to some config file, e.g. app_settings.py
# However it's still not recommended to decrease its value much.
max_url_length = 512

class Feed(Base):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(max_url_length), unique=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)

    articles: Mapped[list[Article]] = relationship(
        "Article",
        back_populates="feed",
        cascade="all, delete-orphan"
        )

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feed_id: Mapped[int] = mapped_column(Integer, ForeignKey("feeds.id"))
    link: Mapped[str] = mapped_column(String(max_url_length), unique=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    time_published: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    feed: Mapped[Feed] = relationship("Feed", back_populates="articles")
