from crawler.article_crawler import crawl_articles_from_links
from crawler.utils import load_jsonl


links = load_jsonl("/home/zchen/crawler/data/technology_articles/juejin/links.jsonl")
links = [obj["link"] for obj in links]

crawl_articles_from_links(
    links,
    out_path="data/technology_articles/juejin"
    )