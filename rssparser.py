from feedparser import parse 

def rss_parser(source: str):
    parsed_result = parse(source)
    return parsed_result