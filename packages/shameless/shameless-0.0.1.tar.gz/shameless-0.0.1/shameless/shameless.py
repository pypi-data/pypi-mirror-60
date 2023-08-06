import os
import webbrowser
from multiprocessing import Pool, cpu_count
from typing import List, Callable

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


def get(url: str, chrome: bool = False) -> BeautifulSoup:
    if chrome:
        chromedriver_path = "/usr/local/bin/chromedriver"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("lang=ko_KR")
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        driver.get(url)
        html = driver.page_source
        driver.close()
    else:
        html = requests.get(url).text
    return BeautifulSoup(html, 'html.parser')


def show(url: str, chrome: bool = False):
    path = os.path.abspath('temp.html')
    file = f'file://{path}'
    with open(path, 'w') as f:
        f.write(get(url, chrome).prettify())
    try:
        webbrowser.get('chrome').open(file)
    except:
        webbrowser.open(file)


def pool(func: Callable, tasks: List) -> List:
    with Pool(cpu_count()) as p:
        result = list(tqdm(p.imap(func, tasks), total=len(tasks)))
    return result
