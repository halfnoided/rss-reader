import socket
import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from feedparser import parse
from datetime import datetime
from bs4 import BeautifulSoup

from models import Feed, Article

# TODO: move to some config file, e.g. app_settings.py
# Default timeout, if there's no response from source
timeout_in_seconds = 10

socket.setdefaulttimeout(timeout_in_seconds)


# This function fetches rss+atom (.xml) from HTML if the wanted feed
# can pass 
def rss_parser(url: str):

    # Current `headers` functionality include only user-agent override
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:156.0) Gecko/20100101 Firefox/156.0"
    }

    try:
        html_source = httpx.get(url, headers=headers, follow_redirects=True)
        html_source.raise_for_status()

        content_type = html_source.headers["content-type"]
        if "html" in content_type:
            soup = BeautifulSoup(html_source.text, "html.parser")
            for link in soup.find_all("link", rel="alternate"):
                link_type = link.get("type", "")
                if "rss" in link_type or "atom" in link_type:
                    rss_url = link.get("href")
                    return parse(rss_url, request_headers=headers)
            return None
    
        elif "xml" in content_type:
            return parse(url, request_headers=headers)
        else:
            print(f"Unknown content type. Skipping...")
            return None
  
    except httpx.RequestError:
        print(f"An error occurred while requesting {url}.") 
        return None
    except httpx.HTTPStatusError:
        print(f"Server responded with status code {html_source.status_code}.")
        return None

# Parse time given by feedparser into more readable
# and more python-like time format
def parsed_time(entry) -> datetime | None:
    parsed = entry.get("published_parsed")
    
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

# Save feed by given feed URL within current local session
# into persistent database
def save_feed_to_db(feed_url, session):
    parsed_source = rss_parser(feed_url)
    if parsed_source is None:
        print(f"Failed to parse {feed_url}.")
        return
     
    feed_title = parsed_source.feed.get("title", "Empty title")

    feed = session.execute(
        select(Feed)
        .where(Feed.url == feed_url)
        ).scalars().one_or_none()

    if feed is None:
        feed = Feed(
            url = feed_url,
            title = feed_title
        )
        session.add(feed)
        session.commit()
    
    for entry in parsed_source.entries:
        article_content = ""
        if "content" in entry:
            article_content = entry.content[0].value
        if (article_content == "") and ("summary" in entry):
            article_content = entry.summary

        article = Article(
            feed_id = feed.id,
            link = entry.get("link"),
            title = entry.get("title"),
            time_published = parsed_time(entry),
            content = article_content
        )
        try:
            session.add(article)
            session.commit()
        except IntegrityError:
            session.rollback()
