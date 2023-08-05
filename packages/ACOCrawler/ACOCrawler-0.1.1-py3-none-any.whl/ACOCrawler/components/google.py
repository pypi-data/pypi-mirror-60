import json
import time
from urllib import parse
import requests
from bs4 import BeautifulSoup

SLEEP_TIME = 2


class Google:
    def __init__(self):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'})

    def Search(self, keyword, type='text', maximum=100):
        """Google検索

        Args:
            keyword(str):
            type(str):
            maximum(int):

        Returns:
            list: 検索結果
        """
        print('Google', type.capitalize(), 'Search :', keyword)
        result, total = [], 0
        query = self.query_gen(keyword, type)
        while True:
            # 検索
            html = self.session.get(next(query)).text
            links = self.get_links(html, type)

            # 検索結果の追加
            if not len(links):
                print('-> No more links')
                break
            elif len(links) > maximum - total:
                result += links[:maximum - total]
                break
            else:
                result += links
                total += len(links)

        print('-> Finally got', str(len(result)), 'links')
        return result

    def query_gen(self, keyword, type):
        """検索クエリを作り出す

        ジェネレータ

        Args:
            keyword:
            type:

        Yields:
            str: 検索クエリ

        """
        page = 0
        while True:
            if type == 'text':
                params = parse.urlencode({
                    'q': keyword,
                    'num': '10',
                    'filter': '0',
                    'start': str(page * 10)})
            elif type == 'image':
                params = parse.urlencode({
                    'q': keyword,
                    'tbm': 'isch',
                    'filter': '0',
                    'ijn': str(page)})

            yield self.GOOGLE_SEARCH_URL + '?' + params
            time.sleep(SLEEP_TIME)
            page += 1

    def get_links(self, html, type):
        """リンクを求める

         あるHTMLに入っているリンクをすべて洗い出す

         Args:
             html:
             type:

         Returns:
             list: Googleの検索ページに含まれるURLを返す
         """
        soup = BeautifulSoup(html, 'lxml')
        if type == 'text':
            elements = soup.select('.rc > .r > a')
            links = [e['href'] for e in elements]
        elif type == 'image':
            elements = soup.select('.rg_meta.notranslate')
            jsons = [json.loads(e.get_text()) for e in elements]
            links = [js['ou'] for js in jsons]
        return links
