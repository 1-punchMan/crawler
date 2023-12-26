from crawler.link_crawler import crawl_links_from_pages


def extract_links(soup):
    post_list = soup.find(id="post_list")
    return [{"link": a.get("href")} for a in post_list.find_all('a', class_="post-item-title")]

crawl_links_from_pages(
    page_address_prefix="https://www.cnblogs.com/pick/",
    start=82, end=0,
    out_path="data/technology_articles/cnblogs",
    extract_func=extract_links
    )  # From old to new.