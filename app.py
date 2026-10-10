from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
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

# TODO: move to some config file, e.g. app_settings.py
showed_articles_limit = 25

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

@app.get("/articles")
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

@app.get("/articles/{id}")
def read_article_content(id: int, request: Request):
    with SessionLocal() as session:
        article_content = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .where(Article.id == id)
        ).scalars().one_or_none()
        
        if not article_content:
            raise HTTPException(
                status_code=404, 
                detail=f"Article with id {id} not found"
                )
        
        return templates.TemplateResponse(
            request,
            "article_content.html",
            context={"article": article_content}
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

@app.get("/feeds/{feed_id}/articles")
def read_feed_articles(feed_id: int, request: Request):
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

        # trying to auto-refresh current feed
        # when getting the list of its articles
        try:
            save_feed_to_db(feed.url, session)
        except Exception as exc:
            print(f"Error occurred while refreshing feed {feed.title}: {exc}")

        articles = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .where(Article.feed_id == feed_id)
            .order_by(Article.time_published.desc())
            .limit(showed_articles_limit)
        ).scalars().all()

        return templates.TemplateResponse(
            request,
            "articles.html",
            context={"articles": articles, "feed_title": feed.title, "feed_id": feed.id}
        )

@app.get("/favorites")
def read_favorites(request: Request):
    with SessionLocal() as session:
        favorite_articles = session.execute(
            select(Article)
            .options(joinedload(Article.feed))
            .where(Article.is_favorite == True)
            .order_by(Article.time_published.desc())
            .limit(showed_articles_limit)
        ).scalars().all()

        return templates.TemplateResponse(
            request,
            "favorites.html",
            context={"articles": favorite_articles}
        )

@app.post("/feeds")
def create_feed(feed: FeedCreate):
    new_feed = Feed(**feed.model_dump())
    with SessionLocal() as session:
        session.add(new_feed)
        session.commit()
        session.refresh(new_feed)

        save_feed_to_db(new_feed.url, session)

        return new_feed

@app.post("/feeds/refresh")
def refresh_feeds():
    with SessionLocal() as session:
        feeds = session.execute(select(Feed)).scalars().all()

        for feed in feeds:
            try:
                save_feed_to_db(feed.url, session)
            except Exception as exc:
                print(f"Error occurred while refreshing {feed.url}: {exc}")

        return RedirectResponse(url="/feeds", status_code=303)

@app.post("/feeds/{feed_id}/refresh")
def refresh_feed_articles(feed_id: int):
    with SessionLocal() as session:
        feed = session.get(Feed, feed_id)

        if feed is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feed with id {feed_id} not found"
            )

        try:
            save_feed_to_db(feed.url, session)
        except Exception as exc:
            print(f"Error occured while refreshing feed {feed.title}: {exc}")

        return RedirectResponse(url=f"/feeds/{feed_id}/articles", status_code=303)

@app.post("/articles/{id}/favorite")
def toggle_favorite(id: int):
    with SessionLocal() as session:
        article = session.get(Article, id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail=f"Article with id {id} not found"
            )
        # changing "favorite" state to the opposite.
        article.is_favorite = not article.is_favorite
        session.commit()

        return RedirectResponse(url=f"/articles/{id}", status_code=303)
