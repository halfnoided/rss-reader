from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from pathlib import Path

from database import SessionLocal
from models import Article, Feed
from schemas import (
    FeedCreate,
    FeedOut,
    ArticleOut,
    )
from services.feed_resolver import rss_parser, save_feed_to_db

showed_articles_limit = 10

app = FastAPI()
templates = Jinja2Templates(
    directory=Path(__file__).parent / "templates"
    )

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={"message": "Hello"}
    )

@app.get(
    "/articles",
    response_model=list[ArticleOut]
    )
def read_articles(request: Request):
    with SessionLocal() as session:
        articles = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .order_by(Article.time_published.desc())
            .limit(showed_articles_limit)
        ).scalars().all()

        return templates.TemplateResponse(
            request,
            "articles.html",
            context={"articles": articles}
        )

@app.get("/feeds")
def read_feeds(request: Request):
    with SessionLocal() as session:
        feeds = session.execute(
            select(Feed)
            .order_by(Feed.id)
        ).scalars().all()

        return templates.TemplateResponse(
            request,
            "feeds.html",
            context={"feeds": feeds}
        )

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
            new_feed.url,
            session
            )
        return new_feed