from feedparser import parse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models import Feed, Article 

def rss_parser(source: str):
    parsed_source = parse(source)
    return parsed_source

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
            title = entry.get("title")
        )
        try:
            session.add(article)
            session.commit()
        except IntegrityError:
            session.rollback()