#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スクレイピングユーティリティ
    * 処理対象サイトURLと、CSSセレクタと、処理対象属性を指定して、スクレイピングする
    * スクレイピング結果を以下のファイルに保存したり、読み込んだりできる
        * pickle: ライブラリpickleを参照のこと
        * 独自フォーマット: ダウンロードする画像ファイルのURLが展開されているので、ダウンローダーにコピペしやすい
"""

# standard library
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

# 3rd party packages
import urllib3
import pickle
import sys
import copy
import bs4  # Beautiful Soup
import pyperclip  # クリップボード
from dataclasses import dataclass
from urllib3.util.retry import Retry
from requests_html import HTMLSession
import json

# local source
from const import *

# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class ScrapingValue:
    """
    スクレイピング値オブジェクト
    """
    urls: list
    css_selectors: list
    attrs: list
    title_css: str
    title: str
    image_list: list

    def __init__(self, urls, css_selectors, attrs, title_css, title, image_list):
        """
        完全コンストラクタパターン

        :param urls: list 処理対象サイトURLリスト
        :param css_selectors: list スクレイピングする際のCSSセレクタリスト
        :param attrs: list スクレイピングする際の属性リスト
        :param title_css: str 対象サイトタイトルのCSSセレクタ
        :param title: str 対象サイトタイトル
        :param image_list: list スクレイピングして得た属性のリスト
        """
        if urls is not None:
            object.__setattr__(self, "urls", urls)
        if css_selectors is not None:
            object.__setattr__(self, "css_selectors", css_selectors)
        if attrs is not None:
            object.__setattr__(self, "attrs", attrs)
        if title_css is not None:
            object.__setattr__(self, "title_css", title_css)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(image_list):
            object.__setattr__(self, "image_list", image_list)


class Scraping:
    """
    スクレイピングのユーティリティ
        * 指定のサイトを読み込む
        * 指定のCSSセレクタ(css_image_select)と属性でスクレイピングする
        * スクレイピング結果でCrawlingValueを生成する
        * CrawlingValueをファイルに保存したり読み込んだりできる
    """
    value_object: ScrapingValue = None
    urls: list = None
    css_selectors: list = None
    attrs: list = None
    script = """
        () => {
            return {
                width: document.documentElement.clientWidth,
                height: document.documentElement.clientHeight,
                deviceScaleFactor: window.devicePixelRatio,
            }
        }
    """

    def __init__(self, target_value=None, css_selectors=None, attrs=None, title_css=None):
        """
        コンストラクタ

        :param target_value: list 対象となるサイトURLリスト、または、ScrapingValue 値オブジェクト
        :param css_selectors: list スクレイピングする際のCSSセレクタリスト
        :param attrs: list スクレイピングする際の属性リスト
        :param title_css: str タイトルのCSSセレクタ
        """
        if target_value is not None:
            if isinstance(target_value, ScrapingValue):
                value_object = target_value
                self.value_object = value_object
                if value_object.urls is not None:
                    self.urls = value_object.urls
                if value_object.css_selectors is not None:
                    self.css_selectors = value_object.css_selectors
                if value_object.attrs is not None:
                    self.attrs = value_object.attrs
                if value_object.title_css is not None:
                    self.attrs = value_object.title_css
            else:
                if isinstance(target_value, list):
                    self.urls = target_value
                    if css_selectors is not None:
                        self.css_selectors = css_selectors
                        if attrs is not None:
                            self.attrs = attrs
                            if title_css is not None:
                                self.title_css = title_css
                                # self.request()
                                self.request_html()

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: crawling_value 値オブジェクト
        """
        return copy.deepcopy(self.value_object)

    def get_image_list(self):
        """
        画像URLリストを取得する

        :return: crawling_value.image_list 画像URLリスト
        """
        return copy.deepcopy(self.value_object.image_list)

    def get_title(self):
        """
        対象サイトタイトルを取得する

        :return: crawling_value.title 対象サイトタイトル
        """
        return self.value_object.title

    def request(self):
        """
        ページをたどって画像のurlを集める。値オブジェクトを生成する。

        :return: bool 成功/失敗=True/False
        """
        image_list: list = []
        title: str = ""
        retries = Retry(connect=5, read=2, redirect=5)
        http = urllib3.PoolManager(retries=retries)
        for url in self.urls:
            res = http.request('GET', url, timeout=10, headers=HEADERS_DIC)
            soup = bs4.BeautifulSoup(res.data, 'html.parser')
            # title = str(soup.title.string)
            title = str(soup.select(self.title_css))
            for css_selector, attr in zip(self.css_selectors, self.attrs):
                for img in soup.select(css_selector):
                    absolute_path = str(img[attr])
                    parse_path = urlparse(absolute_path)
                    if 0 == len(parse_path.scheme):  # 絶対パスかチェックする
                        absolute_path = urljoin(url, absolute_path)
                    image_list.append(absolute_path)
        self.value_object = ScrapingValue(self.urls,
                                          self.css_selectors,
                                          self.attrs,
                                          self.title_css,
                                          title,
                                          image_list,
                                          )
        return True

    def request_html(self):
        """
        ページを再帰的にたどって画像のurlを集める。値オブジェクトを生成する。

        :return: bool 成功/失敗=True/False
        """
        session = HTMLSession()
        response = session.get(self.urls[0])
        # ブラウザエンジンでHTMLを生成させる
        response.html.render(script=self.script, reload=False, timeout=0, sleep=10)
        # スクレイピング
        # title = response.html.find("html > head > title", first=True).text
        title = response.html.find(self.title_css, first=True).text
        target_url = self.urls
        for css_selector, attr in zip(self.css_selectors, self.attrs):
            target_url = self.get_url_list(target_url, css_selector, attr)
        image_list = target_url
        self.value_object = ScrapingValue(self.urls,
                                          self.css_selectors,
                                          self.attrs,
                                          self.title_css,
                                          title,
                                          image_list,
                                          )
        return True

    def get_url_list(self,
                     urls,
                     css_selector,
                     attr,
                     ):
        session = HTMLSession()
        url_list: list = []
        for url in urls:
            response = session.get(url)
            # ブラウザエンジンでHTMLを生成させる
            response.html.render(script=self.script, reload=False, timeout=0, sleep=10)
            target_rows = response.html.find(css_selector)
            count = len(target_rows)
            print(count)
            if target_rows:
                for row in target_rows:
                    if not attr == "":
                        absolute_path = row.attrs[attr]
                    else:
                        absolute_path = row.text
                    parse_path = urlparse(absolute_path)
                    if 0 == len(parse_path.scheme):  # 絶対パスかチェックする
                        absolute_path = urljoin(url, absolute_path)
                    url_list.append(absolute_path)
                    print(str(count) + " " + absolute_path)
                    count -= 1
        return url_list

    def create_save_text(self):
        """
        保存用文字列の作成

        :return: str 保存用文字列の作成
        """
        buff = json.dumps(self.value_object.urls, ensure_ascii=False) + '\n'  # サイトURL追加
        buff += json.dumps(self.value_object.css_selectors, ensure_ascii=False) + '\n'  # cssセレクタ追加
        buff += json.dumps(self.value_object.attrs, ensure_ascii=False) + '\n'  # 属性追加
        buff += self.value_object.title_css + '\n'  # タイトルCSSセレクタ追加
        buff += self.value_object.title + '\n'  # タイトル追加
        for absolute_path in self.value_object.image_list:
            buff += absolute_path + '\n'  # 画像URL追加
        return buff

    def clip_copy(self):
        """
        クローリング結果をクリップボードにコピーする

        :return: bool 成功/失敗=True/False
        """
        if self.value_object is None:
            return False
        buff = self.create_save_text()
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True

    def save_text(self, save_path):
        """
        データをファイルに、以下の独自フォーマットで保存する
            * 処理対象サイトURL
            * CSSセレクタ
            * 属性
            * タイトル
            * 複数の画像URL

        :param save_path: str セーブする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if self.value_object is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.create_save_text()
            work_file.write(buff)  # ファイルへの保存
            return True

    def load_text(self, load_path):
        """
        独自フォーマットなファイルからデータを読み込む

        :param load_path: str ロードする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            self.urls = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.css_selectors = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.attrs = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.title_css = buff[0].rstrip('\n')
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            image_list: list = []
            for line in buff:
                image_list.append(line.rstrip('\n'))
            self.value_object = ScrapingValue(self.urls,
                                              self.css_selectors,
                                              self.attrs,
                                              title,
                                              image_list,
                                              )
            return True

    def save_pickle(self, save_path):
        """
        シリアライズしてpickleファイルに保存する

        :param save_path: str セーブするpickleファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if save_path is None:
            return False
        with open(save_path, 'wb') as work_file:
            pickle.dump(self.value_object, work_file)
            return True

    def load_pickle(self, load_path):
        """
        pickleファイルを読み込み、デシリアライズする

        :param load_path: str ロードするpickleファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if load_path is None:
            return False
        with open(load_path, 'rb') as work_file:
            self.value_object = pickle.load(work_file)
            return True


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    imglist_filepath = RESULT_FILE_PATH
    target_url = DEFAULT_TARGET_URL
    folder_path = OUTPUT_FOLDER_PATH
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        target_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            parse = urlparse(paste_str)
            if 0 < len(parse.scheme):
                target_url = paste_str
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit(1)
    print(target_url)

    # テスト　女の子の顔のアイコン | かわいいフリー素材集 いらすとや
    urls = ['https://www.irasutoya.com/2013/10/blog-post_3974.html',
            ]
    css_selectors = ['div.entry > p:nth-child(1) > a > img',
                     ]
    attrs = ['src',
             ]
    title_css = 'html > head > title'
    scraping = Scraping(urls,
                        css_selectors,
                        attrs,
                        title_css,
                        )
    scraping.save_text(RESULT_FILE_PATH)
    # 値オブジェクトを生成
    value_objects = scraping.get_value_objects()
    # 保存や読込を繰り返す
    scraping.save_pickle(RESULT_FILE_PATH + '1.pkl')
    scraping.load_pickle(RESULT_FILE_PATH + '1.pkl')
    scraping.save_text(RESULT_FILE_PATH + '1.txt')
    # 値オブジェクトでインスタンス作成
    scraping2 = Scraping(value_objects)
    # 保存や読込を繰り返す
    scraping2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    scraping2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    scraping2.save_text(RESULT_FILE_PATH + '2.txt')
    scraping2.load_text(RESULT_FILE_PATH + '2.txt')
    scraping2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    scraping2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    scraping2.save_text(RESULT_FILE_PATH + '3.txt')
