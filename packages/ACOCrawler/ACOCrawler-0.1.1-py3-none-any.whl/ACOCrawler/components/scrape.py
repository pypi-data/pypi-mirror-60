import os
import time
import urllib3
import re
import requests

from bs4 import BeautifulSoup, Comment
from reppy.cache import RobotsCache
from requests.exceptions import Timeout
from urllib3.exceptions import InsecureRequestWarning

from .url import Url
from .wakati import Wakati
from .score import Score

urllib3.disable_warnings(InsecureRequestWarning)

PAGE_CAPACITY = 200
TIME_OUT = 2
SLEEP_TIME = 1

URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

BODY_URL_REGEX = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+')
BODY_WWW_REGEX = re.compile(r'[/:%#\$&\?\(\)~\.=\+\-…]+')
SPACE_REGEX = re.compile(r'\s+')
NUMBER_REGEX = re.compile(r'\d+')
TAG_REGEX = re.compile(r'<[^>]*?>')
SPECIAL_REGEX = re.compile('[!"#$%&\'\\\\()*,-./⁄:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、≒◉？！｀╱＋￥％〻〳〴〵〼ヿ«»〽]')

BAD_EXTENSIONS = ['.pdf', '.jpg', '.png', '.css', '.js', '.mp4', '.jpeg', '.gif', '.bmp', '.mpg', '.avi', '.mp3',
                  '.wma', '.wav', '.exe', '.zip', '.bat', '.bak', '.doc', '.fon', '.fnt', '.ini', '.lzh', '.gz', '.tar',
                  '.tgz', '.wav', '.xls']


class Scrape:
    """スクレイピングクラス

    URLのページをスクレイピングする

    Raises:
        Exception: 拡張子・robots.txt・TLEに関して発生する

    """
    robot = RobotsCache(PAGE_CAPACITY, TIME_OUT)

    @classmethod
    def page_scrape(cls, url, keyword, **kwargs):
        """ページをスクレイピングする

        urlの文書をスクレイピングする

        Args:
            url(str): 文書URL
            keyword(str): キーワード
            **kwargs(dict): NLPの際使用する

        Returns:
            dict: スクレイピング結果
        """
        url = Url.erase_url_parameters(url)
        extension = os.path.splitext(url)[1].lower()

        if extension in BAD_EXTENSIONS:
            raise Exception

        if not cls.robot.allowed(url, 'python program'):
            print('robots.txt not allowed: ', url)
            raise Exception

        try:
            result = requests.get(url, verify=False, allow_redirects=True, timeout=TIME_OUT)
            time.sleep(SLEEP_TIME)
        except Timeout:
            print("TLE: ", url)
            raise Exception

        content = result.content
        soup = BeautifulSoup(content, 'lxml')

        title = cls.__get_title(soup)
        title = cls.__clean_body(title)
        anchors = cls.__get_anchors(url, soup)
        domain = Url.get_url_domain(url)
        body = cls.__get_body(soup)
        body = cls.__clean_body(body)
        wakati = Wakati.wakati_text(body)
        score = Score.calc_score_by_simple_counts(body, wakati, keyword, **kwargs)

        return {
            'url': url,
            'title': title,
            'anchors': anchors,
            'domain': domain,
            'body': body,
            'wakati': wakati,
            'score': score
        }

    @classmethod
    def __get_title(cls, soup):
        title = ""
        if hasattr(soup, 'title') and hasattr(soup.title, 'string'):
            title = soup.title.string
        return title

    @classmethod
    def __get_anchors(cls, url, soup):
        anchors = [a.get('href') for a in soup('a')
                   if a.get('href') is not None
                   and len(a.get('href'))
                   and a.get('href')[0:10] != 'javascript'
                   and re.match(URL_REGEX, a.get('href')) is not None]
        anchors = [Url.get_absolute_url(url, anchor) for anchor in anchors]
        anchors = [Url.erase_url_parameters(anchor) for anchor in anchors]
        anchors = [Url.erase_url_special_characters(anchor) for anchor in anchors]
        anchors = list(set(anchors))
        return anchors

    @classmethod
    def __get_body(cls, soup):
        for comment in soup(text=lambda x: isinstance(x, Comment)): comment.extract()
        [script.decompose() for script in soup('script')]
        [style.decompose() for style in soup('style')]
        body = ' '.join([text.strip() for text in soup.find_all(text=True)[1:]])
        return body

    @classmethod
    def __clean_body(cls, body):
        if body is None:
            body = ''
        body = body.lower()
        body = TAG_REGEX.sub('', body)
        body = NUMBER_REGEX.sub('', body)
        body = BODY_URL_REGEX.sub('', body)
        body = BODY_WWW_REGEX.sub('', body)
        body = SPECIAL_REGEX.sub(' ', body)
        body = SPACE_REGEX.sub(' ', body)
        return body
