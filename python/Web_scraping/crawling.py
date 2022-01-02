#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリングユーティリティ
    * 処理対象サイトURLと、CSSセレクタと、処理対象属性を指定して、クローリングする
    * クローリング結果を以下のファイルに保存したり、読み込んだりできる
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

# local source
from const import *

sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class CrawlingValue:
    """
    クローリング値オブジェクト
    """
    target_url: str
    css_image_selector: str
    image_attr: str
    title: str
    image_list: list

    def __init__(self, target_url, css_image_selector, image_attr, title, image_list):
        """
        完全コンストラクタパターン

        :param target_url: str 処理対象サイトURL
        :param css_image_selector: str スクレイピングする際のCSSセレクタ
        :param image_attr: str スクレイピングする際の属性
        :param title: str 対象サイトタイトル
        :param image_list: list スクレイピングして得た属性のリスト
        """
        if target_url is not None:
            object.__setattr__(self, "target_url", target_url)
        if css_image_selector is not None:
            object.__setattr__(self, "css_image_selector", css_image_selector)
        if image_attr is not None:
            object.__setattr__(self, "image_attr", image_attr)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(image_list):
            object.__setattr__(self, "image_list", image_list)


class Crawling:
    """
    クローリングのユーティリティ
        * 指定のサイトを読み込む
        * 指定のCSSセレクタ(css_image_select)と属性でクローリングする
        * クローリング結果でCrawlingValueを生成する
        * CrawlingValueをファイルに保存したり読み込んだりできる
    """
    crawling_value: CrawlingValue = None
    target_url: str = None
    css_image_selector: str = None
    image_attr: str = None

    def __init__(self, target_value, css_image_selector=None, image_attr=None):
        """
        コンストラクタ

        :param target_value: str 対象となるサイトURL、または、CrawlingValue 値オブジェクト
        :param css_image_selector: str スクレイピングする際のCSSセレクタ
        :param image_attr: str スクレイピングする際の属性
        """
        if target_value is None:
            print('target_valueがNoneです')
            sys.exit(1)
        if isinstance(target_value, CrawlingValue):
            crawling_value = target_value
            self.crawling_value = crawling_value
            if crawling_value.target_url is not None:
                self.target_url = crawling_value.target_url
            if crawling_value.css_image_selector is not None:
                self.css_image_selector = crawling_value.css_image_selector
            if crawling_value.image_attr is not None:
                self.image_attr = crawling_value.image_attr
        else:
            if isinstance(target_value, str):
                self.target_url = target_value
                # targetUrlを指定したら、誰か解析してcssImageSelector作ってくれないかな。
                if css_image_selector is not None:
                    self.css_image_selector = css_image_selector
                    if image_attr is not None:
                        self.image_attr = image_attr
                        self.request()

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: crawling_value 値オブジェクト
        """
        return copy.deepcopy(self.crawling_value)

    def get_image_list(self):
        """
        画像URLリストを取得する

        :return: crawling_value.image_list 画像URLリスト
        """
        return copy.deepcopy(self.crawling_value.image_list)

    def get_title(self):
        """
        対象サイトタイトルを取得する

        :return: crawling_value.title 対象サイトタイトル
        """
        return self.crawling_value.title

    def request(self):
        """
        target_urlに接続して、image_attrでスクレイピングして、titleとimage_listを更新する

        :return: bool 成功/失敗=True/False
        """
        retries = Retry(connect=5, read=2, redirect=5)
        http = urllib3.PoolManager(retries=retries)
        res = http.request('GET', self.target_url, timeout=10, headers=HEADERS_DIC)
        soup = bs4.BeautifulSoup(res.data, 'html.parser')
        title = str(soup.title.string)
        image_list: list = []
        for img in soup.select(self.css_image_selector):
            absolute_path = str(img[self.image_attr])
            parse_path = urlparse(absolute_path)
            if 0 == len(parse_path.scheme):  # 絶対パスかチェックする
                absolute_path = urljoin(self.target_url, absolute_path)
            image_list.append(absolute_path)
        self.crawling_value = CrawlingValue(self.target_url,
                                            self.css_image_selector,
                                            self.image_attr,
                                            title,
                                            image_list,
                                            )
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
        if self.crawling_value is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.crawling_value.target_url + '\n'  # サイトURL追加
            buff += self.crawling_value.css_image_selector + '\n'  # cssセレクタ追加
            buff += self.crawling_value.image_attr + '\n'  # 属性追加
            buff += self.crawling_value.title + '\n'  # タイトル追加
            for absolute_path in self.crawling_value.image_list:
                buff += absolute_path + '\n'  # 画像URL追加
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
            self.target_url = buff[0].rstrip('\n')
            del buff[0]
            self.css_image_selector = buff[0].rstrip('\n')
            del buff[0]
            self.image_attr = buff[0].rstrip('\n')
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            image_list: list = []
            for line in buff:
                image_list.append(line.rstrip('\n'))
            self.crawling_value = CrawlingValue(self.target_url,
                                                self.css_image_selector,
                                                self.image_attr,
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
            pickle.dump(self.crawling_value, work_file)
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
            self.crawling_value = pickle.load(work_file)
            return True

    def clip_copy(self):
        """
        クローリング結果をクリップボードにコピーする

        :return: bool 成功/失敗=True/False
        """
        if self.crawling_value is None:
            return False
        buff = self.crawling_value.target_url + '\n'  # サイトURL追加
        buff += self.crawling_value.css_image_selector + '\n'  # cssセレクタ追加
        buff += self.crawling_value.image_attr + '\n'  # 属性追加
        buff += self.crawling_value.title + '\n'  # タイトル追加
        for absolute_path in self.crawling_value.image_list:
            buff += absolute_path + '\n'  # 画像URL追加
        pyperclip.copy(buff)  # クリップボードへのコピー
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

    crawling = Crawling(target_url, img_css_select, img_attr)  # 'img.vimg[src*="jpg"]'
    crawling.save_text(RESULT_FILE_PATH)
    value_objects = crawling.get_value_objects()
    crawling.save_pickle(RESULT_FILE_PATH + '1.pkl')
    crawling.load_pickle(RESULT_FILE_PATH + '1.pkl')
    crawling.save_text(RESULT_FILE_PATH + '1.txt')
    crawling2 = Crawling(value_objects)
    crawling2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    crawling2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    crawling2.save_text(RESULT_FILE_PATH + '2.txt')
    crawling2.load_text(RESULT_FILE_PATH + '2.txt')
    crawling2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    crawling2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    crawling2.save_text(RESULT_FILE_PATH + '3.txt')
