from pathlib import Path

from rssparser import rss_parser, save_feed_to_db
from database import engine, Base, SessionLocal
from models import Feed, Article
from app import app

Base.metadata.create_all(bind=engine)

def main():
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    return 0

if __name__ == "__main__":
    main()