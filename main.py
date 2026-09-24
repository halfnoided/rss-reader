from pathlib import Path
from rssparser import rss_parser
from database import engine, Base
from models import Feed, Article

Base.metadata.create_all(bind=engine)

# TODO:
# Provide path fetching from some other place,
# not just direct inline string,
# e.g. environment variable for path
# path = Path("/home/user/test_file.xml")
url = "https://habr.com/ru/rss/articles/"

def main():
    # s1 = path
    s2 = url
    parsed_s2 = rss_parser(s2)
    # Accessing first 5 entries with their title
    for entry in parsed_s2.entries[:5]:
        print(entry.get("title", "No specific title")) 
        print(entry.get("link"))
        print(entry.get("published"))
        print("That's it!")
    return 0

if __name__ == "__main__":
    main()