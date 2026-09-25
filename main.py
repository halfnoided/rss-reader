from pathlib import Path
from rssparser import rss_parser, save_feed_to_db
from database import engine, Base, SessionLocal
from models import Feed, Article

Base.metadata.create_all(bind=engine)

# TODO:
# Provide path fetching from some other place,
# not just direct inline string,
# e.g. environment variable for path
# path = Path("/home/user/test_file.xml")
url = "https://habr.com/ru/rss/articles/"

def main():
    with SessionLocal() as session:
        save_feed_to_db(rss_parser(url), session)
    return 0

if __name__ == "__main__":
    main()