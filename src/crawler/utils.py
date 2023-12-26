import json, random

from seleniumwire import webdriver

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


def get_selenium_browser():
    ch_options = webdriver.ChromeOptions()

    # 不加载图片,加快访问速度
    ch_options.add_experimental_option("prefs", {"profile.mamaged_default_content_settings.images": 2})
    ch_options.add_argument('--headless') # 无头模式，可不启用界面显示运行
    ch_options.add_argument('--disable-gpu') # 禁用GPU加速

    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    ch_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # ch_options.add_experimental_option("debuggerAddress", "127.0.0.1:9999")
    # ch_options.add_argument('--proxy--server=127.0.0.1:8080')
    ch_options.add_argument('--disable-infobars')  # 禁用浏览器正在被自动化程序控制的提示
    ch_options.add_argument('--incognito')

    # ch_options.add_argument(f'--user-agent="{random.choice(AGENTS)}"') # 设置请求头的User-Agent
    ch_options.add_argument(f'--Referer="{random.choice(REFERERS)}"')

    browser = webdriver.Chrome(
        options=ch_options,
        # service=webdriver.ChromeService(executable_path=CHROMEDRIVER_PATH)
        )

    # Create a request interceptor
    def interceptor(request):
        # del request.headers['user-agent']  # Delete the header first
        del request.headers['Referer']
        
        # request.headers['user-agent'] = random.choice(AGENTS)
        request.headers['Referer'] = random.choice(REFERERS)

    # Set the interceptor on the driver
    browser.request_interceptor = interceptor

    return browser


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
        
def load_json(file):
    with open(file, 'r', encoding="utf-8") as f:
        return json.load(f)

def save_json(file, obj):
    with open(file, 'w', encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)