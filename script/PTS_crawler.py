import json, time, random, os, traceback, re, socket, sys
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from logger import create_logger


CHROMEDRIVER_PATH = "/home/zchen/crawler/chromedriver"

AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]
REFERERS = [
    "https://en.rti.org.tw",
    "https://google.com",
    "https://YouTube.com",
    "https://Facebook.com",
    "https://twitter.com",
    "https://instagram.com",
    "https://baidu.com",
    "https://wikipedia.org",
    "https://yandex.ru",
    "https://yahoo.com"
]
PROXIES = ['34.82.235.224:3128']

PAGE_ADDRESS_PREFIX = "https://news.pts.org.tw/news/english?page="
ADDRESS_PREFIX = "https://news.pts.org.tw/article"


def request(address, waiting_time=3):
    headers = {
        'user-agent': random.choice(AGENTS),
        'Referer': random.choice(REFERERS)
    }
    r = requests.get(
        address,
        headers=headers,
        # proxies={'https': proxy}
    )
    soup = BeautifulSoup(r.text, 'html.parser')

    return soup, r.status_code

def crawl_ids(page_id):
    soup, status_code = request(
        f"{PAGE_ADDRESS_PREFIX}{page_id}"
        )

    # extract the IDs
    links = [div.find("a").get("href") for div in soup.find_all('div', class_="col-7 col-md-12")]
    pref_len = len("/article/")
    ids = [int(link[pref_len:]) for link in links]

    return ids, status_code
    
def crawl_ids_wrapper(page_id):

    while True:
        try:
            ids, status = crawl_ids(page_id)
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
    
    return ids

def crawl_PTS(id):
    art = {"id": id}
    soup, status_code = request(
        f"{ADDRESS_PREFIX}/{id}"
        )
    
    # extract the info
    info = soup.find('script', type="application/ld+json")
    if info is None:
        print("info is None")
        return None, status_code
    art["metadata"] = info.text

    # extract the headline
    headline = soup.find('h1', class_="article-title")
    if headline is None:
        print("headline is None")
        return None, status_code
    art["headline"] = headline.text

    # extract the text
    paras = soup.find('div', class_="post-article")
    if paras is None:
        print("paras is None")
        return None, status_code
    art["article_part"] = str(paras)
    
    return art, status_code
    
def crawl_PTS_wrapper(id, repeat_limit=3):
    fail_cnt = 0
    while True:
        try:
            art, status = crawl_PTS(id)
            if art is None:
                if status == 200:
                    fail_cnt += 1
                    if fail_cnt < repeat_limit:
                        logger.info("Retry")
                        continue
                    else:
                        fail_cnt = 0
                        logger.info("Give up this fking article.")
                elif status not in [200, 302, 404]:
                    return -1
                
            break
        except Exception as e:
            logger.info(f"id: {id}")
            if "status" in locals():
                logger.info(f"status: {status}")
            traceback.print_exc()

            if type(e) not in [requests.exceptions.ConnectionError]:
                return -1
            
            logger.info("Retry")

    time.sleep(random.uniform(3, 6))
    
    return art

def load(file):
    with open(file, 'r', encoding="utf-8") as f:
        return f.read()
        
def save(file, string):
    with open(file, 'a', encoding="utf-8") as f:
        f.write(string)
        
def load_jsonl(file):
    with open(file, 'r', encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f]

def save_jsonl(file, obj_list):
    jstrings = [json.dumps(obj, ensure_ascii=False) for obj in obj_list]
    save(
        file,
        '\n'.join(jstrings) + '\n'
        )
    
def crawl_PTS_loop(ids):
    arts = []
    for id in ids:
        art = crawl_PTS_wrapper(id)
        if art == -1:   # Error!
            return None
        if art is not None:
            arts.append(art)
    return arts

def save_and_quit(file, articles, func_name):
    save_jsonl(file, articles)
    logger.info(f"Got some errors in `{func_name}()` QQ...")
    sys.exit()

def crawl_PTS_page(start, end, out_path, log_interval = 10):
    """ Crawl the pages from old to new (descend order). """

    articles = []
    file = Path(out_path) / f"articles_{end}-{start}.jsonl"
    cnt = 0
    if os.path.exists(file):    #判斷是否從上次中斷位置開始
        articles = load_jsonl(file)
        if articles != []:
            last = articles[-1]["page_id"]
            start = last - 1
            cnt = len(articles)
            articles = []
            logger.info(f"Start from page {start} ...")

    pbar = tqdm(list(enumerate(
        range(start, end, -1),
        start=1
        )))
    for i, page_id in pbar:
        pbar.set_description(f'Crawling page {page_id}')

        ids = crawl_ids_wrapper(page_id)
        if ids is None:   # Error!
            save_and_quit(file, articles, "crawl_ids")

        arts = crawl_PTS_loop(ids)
        if arts is None:   # Error!
            save_and_quit(file, articles, "crawl_PTS_loop")
        
        # Add `page_id` to each article.
        for art in arts:
            art["page_id"] = page_id

        cnt += len(arts)
        articles.extend(arts)

        if i % log_interval == 0:
            save_jsonl(file, articles)
            articles = []
            logger.info("")
            logger.info(f"Crawled {cnt} articles.")

    save_jsonl(file, articles)
    logger.info("")
    logger.info(f"Finish! Crawled {cnt} articles.")


# create a logger
logger = create_logger()

crawl_PTS_page(
    start=100, end=0,
    out_path="data/PTS/raw/"
    )  # From old to new.