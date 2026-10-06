from sqlalchemy import select

from database import Base, engine, SessionLocal
from models import Feed
from services.feed_resolver import rss_parser, save_feed_to_db

default_feeds = [
    {
        "url": "https://habr.com/ru/rss/hubs/python",
        "title": "Python на Хабре"
    },

    {
        "url": "https://www.reddit.com/r/programming/.rss",
        "title": "Programming on Reddit"
    },
]

def seed_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        first_feed_from_db = session.execute(
            select(Feed)
        ).scalars().first()
        
        if first_feed_from_db is not None:
            print("There are already feeds. Skipping...")
            return

        print("There are no feeds. Getting default ones:")
        for feed in default_feeds:
            print(f"Adding: {feed["title"]}")

            new_feed = Feed(**feed)
            session.add(new_feed)
            session.commit()
            session.refresh(new_feed)
            
            save_feed_to_db(new_feed.url, session)

        print("Initialization complete.")
        return 

if __name__ == "__main__":
    seed_db()
