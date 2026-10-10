from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base

# TODO: move to some config file, e.g. app_settings.py
# However it's still not recommended to decrease its value much.
max_url_length = 512

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(max_url_length), unique=True)
    title = Column(String)

    articles = relationship(
        "Article",
        back_populates="feed",
        cascade="all, delete-orphan"
        )

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    link = Column(String(max_url_length), unique=True)
    title = Column(String)
    time_published = Column(DateTime)
    content = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False)

    feed = relationship("Feed", back_populates="articles")
