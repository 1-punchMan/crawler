import time, random, os, traceback, sys
import requests

from pathlib import Path
from tqdm import tqdm

from .logger import create_logger
from .request import request_by_trafilatura as request
from .utils import load_jsonl, save_jsonl

# create a logger
logger = create_logger()


def crawl_page(link) -> tuple[str, int]:
    return request(link)
    
def crawl_page_wrapper(link, repeat_limit=3):
    fail_cnt = 0
    while True:
        try:
            content, status = crawl_page(link)
            if not content:
                if status == 200:
                    fail_cnt += 1
                    if fail_cnt < repeat_limit:
                        logger.info("Retry")
                        continue
                    else:
                        fail_cnt = 0
                        logger.info("Give up this fking article.")
                elif status not in [200, 302, 404]:
                    return None
                
            break
        except Exception as e:
            logger.info(f"link: {link}")
            if "status" in locals():
                logger.info(f"status: {status}")
            traceback.print_exc()

            if type(e) not in [requests.exceptions.ConnectionError]:
                return None
            
            logger.info("Retry")
            time.sleep(random.uniform(3, 6))
    
    return content

def save_and_quit(file, articles, func_name):
    save_jsonl(file, articles)
    logger.info(f"Got some errors in `{func_name}()` QQ...")
    sys.exit()

def crawl_articles_from_links(links, out_path, log_interval = 100):
    """ Crawl the pages from old to new (descend order). """

    articles = []
    out_file = Path(out_path) / "articles.jsonl"
    cnt = 0
    start = 0
    if os.path.exists(out_file):    #判斷是否從上次中斷位置開始
        articles = load_jsonl(out_file)
        if articles != []:
            last = articles[-1]["id"]
            start = last + 1
            cnt = len(articles)
            articles = []
            logger.info(f"Start from page {start} ...")

    pbar = tqdm(list(enumerate(links[start:], start=1)))
    for i, link in pbar:
        content = crawl_page_wrapper(link)
        if content == None:   # Error!
            save_and_quit(out_file, articles, "crawl_page_wrapper")

        cnt += 1
        art = {
            "id": cnt,
            "link": link,
            "text": content,
        }
        articles.append(art)

        if i % log_interval == 0:
            logger.info(f"Saving...")

            save_jsonl(out_file, articles)
            articles = []

            logger.info(f"Crawled {cnt} articles.")
            
        time.sleep(random.uniform(3, 4))

    save_jsonl(out_file, articles)
    logger.info("")
    logger.info(f"Finish! Crawled {cnt} articles.")