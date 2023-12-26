import time
from tqdm import tqdm

from crawler.link_crawler import crawl_links_by_scrolling

ADDRESS_PREFIX = "https://juejin.cn"


def scroll(browser):
    js = '''
        entry_list = document.getElementsByClassName("entry-list list")[0];

        wait = () => new Promise(resolve => {
            window.scrollTo(0, document.body.scrollHeight);
            resolve()
            });

        return (async () => {
            await wait();
            return entry_list.childElementCount
            })();
    '''
    target_len = 1500
    last_n_links = 0

    pbar = tqdm(total=target_len)
    while True:
        n_links = browser.execute_script(js)
        pbar.update(n_links - last_n_links)
        if n_links >= target_len:
            break
        last_n_links = n_links
        time.sleep(0.5)

def extract_juejin_links(soup):
    title_tag_list = soup.find_all(class_="title-row")
    links = [title_tag.find("a").get("href") for title_tag in title_tag_list]
    return [ADDRESS_PREFIX + link for link in links]

crawl_links_by_scrolling(
    address="https://juejin.cn/recommended?sort=newest",
    out_path="data/technology_articles/juejin",
    extract_func=extract_juejin_links,
    perform_some_actions=scroll
    )