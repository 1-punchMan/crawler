import time, random, os, traceback
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

from .logger import create_logger
from .request import get_request_method
from .utils import load_jsonl, save_jsonl

# create a logger
logger = create_logger()


def set_request_method(request_method):
    global REQUEST
    REQUEST = get_request_method(request_method)

def crawl_links(address, extract_func, **kwargs):
    html, status_code = REQUEST(address, **kwargs)
    soup = BeautifulSoup(html, 'html.parser')

    # extract the links
    links = extract_func(soup)
    
    return links, status_code
    
def crawl_links_wrapper(page_address_prefix, page_id, extract_func, **kwargs):

    while True:
        try:
            links, status = crawl_links(
                f"{page_address_prefix}{page_id}",
                extract_func,
                **kwargs
                )
            if status not in [200, 302, 404]:
                logger.info(f"page_id: {page_id}")
                logger.info("Request error!")
                logger.info(f"status: {status}")

                return None
            
            break
        except Exception as e:
            logger.info(f"page_id: {page_id}")
            if "status" in locals():
                logger.info(f"status: {status}")
            traceback.print_exc()

            if (
                str(e) != "'NoneType' object has no attribute 'find'" and
                type(e) not in [requests.exceptions.ConnectionError]
                ):
                return None
            
            logger.info("Retry")

    time.sleep(random.uniform(3, 6))
    
    return links

def save_links(file, links):
    save_jsonl(file, links)
    logger.info("")
    logger.info(f"Finish! Crawled {len(links)} links.")

def crawl_links_from_pages(page_address_prefix, start, end, out_path, extract_func):
    """ Crawl the pages from old to new (descend order). """

    set_request_method("requests")

    links = []
    file = Path(out_path) / f"links_p{end}-p{start}.jsonl"
    if os.path.exists(file):    #判斷是否從上次中斷位置開始
        crawled_links = load_jsonl(file)
        if crawled_links != []:
            last = crawled_links[-1]["page_id"]
            start = last - 1
            logger.info(f"Start from page {start} ...")

    pbar = tqdm(list(enumerate(
        range(start, end, -1),
        start=1
        )))
    for i, page_id in pbar:
        pbar.set_description(f'Crawling page {page_id}')

        lks = crawl_links_wrapper(page_address_prefix, page_id, extract_func)
        
        # Add `page_id` to each link.
        for link in lks:
            link["page_id"] = page_id
            
        links.extend(lks)

    save_links(file, links)

def crawl_links_by_scrolling(address, out_path, extract_func, **kwargs):
    """ Crawl the link list that is accessed by scrolling down. """

    set_request_method("selenium")

    file = Path(out_path) / f"links.jsonl"
    links, status = crawl_links(address, extract_func, **kwargs)
    links = [{"link": link} for link in links]

    save_links(file, links)
        