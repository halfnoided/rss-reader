from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
from models import Article, Feed
from schemas import (
    FeedCreate,
    FeedOut,
    ArticleOut,
    )
from rssparser import rss_parser, save_feed_to_db

showed_articles_limit = 10

app = FastAPI()

@app.get("/")
def read_root():
    return {"message":"Hello"}

@app.get(
    "/articles",
    response_model=list[ArticleOut]
    )
def read_articles():
    with SessionLocal() as session:
        articles = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .order_by(Article.time_published.desc())
            .limit(showed_articles_limit)
        ).scalars().all()

        return articles

@app.get(
    "/feeds",
    response_model=list[FeedOut]
    )
def read_feeds():
    with SessionLocal() as session:
        feeds = session.execute(
            select(Feed)
            .order_by(Feed.id)
        ).scalars().all()

        return feeds

@app.get(
    "/feeds/{feed_id}/articles",
    response_model=list[ArticleOut]
)
def read_feed_articles(feed_id: int):
    with SessionLocal() as session:
        feed = session.execute(
            select(Feed)
            .where(Feed.id == feed_id)
        ).scalars().one_or_none()

        if feed is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feed with id {feed_id} not found"
            )
        
        articles = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .where(Article.feed_id == feed_id)
            .order_by(Article.time_published.desc())
            .limit(showed_articles_limit)
        ).scalars().all()

        return articles
        
@app.post(
    "/feeds",
    response_model=FeedOut)
def create_feed(feed: FeedCreate):
    new_feed = Feed(**feed.model_dump())
    with SessionLocal() as session:
        session.add(new_feed)
        session.commit()
        session.refresh(new_feed)

        save_feed_to_db(
            rss_parser(new_feed.url),
            session
            )
        return new_feed