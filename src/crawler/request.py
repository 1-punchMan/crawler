import time, random
import requests
import trafilatura

from trafilatura.utils import decode_response
from crawler.utils import get_selenium_browser

from .utils import AGENTS, REFERERS


def request_by_requests(address):
    headers = {
        'user-agent': random.choice(AGENTS),
        'Referer': random.choice(REFERERS)
    }
    r = requests.get(
        address,
        headers=headers,
        # proxies={'https': proxy}
    )
    return r.text, r.status_code

def request_by_selenium(address, waiting_time=3, perform_some_actions=None):
    BROWSER.get(address)

    # 等待页面 (JavaScript) 加载完成
    time.sleep(waiting_time)

    if perform_some_actions is not None:
        perform_some_actions(BROWSER)

    # 获取页面内容
    content = BROWSER.page_source
    status_code = BROWSER.requests[0].response.status_code

    return content, status_code

def request_by_trafilatura(address):
    response = trafilatura.fetch_url(address, decode=False)
    downloaded = decode_response(response)
    text = trafilatura.extract(downloaded, include_formatting=True)
    return text, response.status


REQUEST_METHODS = {
    "requests": request_by_requests,
    "selenium": request_by_selenium,
    "trafilatura": request_by_trafilatura,
}

def get_request_method(request_method):
    
    if request_method == "selenium":
        global BROWSER
        BROWSER = get_selenium_browser()

    return REQUEST_METHODS[request_method]