from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from database import Base

max_url_length = 512

class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(max_url_length), unique=True)
    title = Column(String)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))
    link = Column(String(max_url_length), unique=True)
    title = Column(String)
    time_published = Column(DateTime)
