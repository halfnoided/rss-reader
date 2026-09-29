import socket
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from feedparser import parse
from datetime import datetime

from models import Feed, Article

# Default timeout, if there's no response from source
timeout_in_seconds = 10
socket.setdefaulttimeout(timeout_in_seconds)

def rss_parser(source: str):
    parsed_source = parse(
        source,
        request_headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:156.0) Gecko/20100101 Firefox/156.0"
            }
    )
    return parsed_source

def time_parser(entry) -> datetime | None:
    parsed= entry.get("published_parsed")
    
    if not parsed:
        return None

    try:
        return datetime(
            year=parsed.tm_year,
            month=parsed.tm_mon,
            day=parsed.tm_mday,
            hour=parsed.tm_hour,
            minute=parsed.tm_min,
            second=parsed.tm_sec
        )
    except (ValueError, TypeError):
        return None

def save_feed_to_db(parsed_source, session):
    feed_url = parsed_source.feed.get("link", "unknown_url")
    feed_title = parsed_source.feed.get("title", "Unknown title")
    
    feed = session.execute(
        select(Feed)
        .where(Feed.url == feed_url)
        ).scalars().one_or_none()

    if not feed:
        feed = Feed(
            url = feed_url,
            title = feed_title
        )
        session.add(feed)
        session.commit()
    
    for entry in parsed_source.entries:
        article = Article(
            feed_id = feed.id,
            link = entry.get("link"),
            title = entry.get("title"),
            time_published = time_parser(entry) 
        )
        try:
            session.add(article)
            session.commit()
        except IntegrityError:
            session.rollback()
