#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Selenium Chromeドライバのヘルパー
Chrome.batを実行して、Chromeを起動しておくと、その続きから操作できる。
スクレイピングしたいurlをクリップボードにコピーして、実行する。
    起動しているChromeに接続する、起動していなければ起動して接続する、ChromeでURLを開きスクレイピングする __init__
    Chromeに接続する __connection
    Chromeを起動する __create
    Chromeを閉じる destroy
    ChromeでURLを開く __open_url
    Chromeで開いているページをスクレイピングする __gen_scraping
    Chromeで開いているページのsourceを取得する get_source
    タイトルを取得する get_title
    最終画像アドレスを取得する get_last_image_url
    履歴を一つ戻る back
    履歴を一つ進む forward

参考ブログ
https://note.nkmk.me/python/
https://maku77.github.io/python/
https://nikkie-ftnext.hatenablog.com/entry/value-object-python-dataclass
参考リファレンス
https://selenium-python.readthedocs.io/
https://www.seleniumqref.com/api/webdriver_gyaku.html
https://www.selenium.dev/ja/documentation/webdriver/getting_started/

"""
import os
import time
# import timeout_decorator
# from timeout_timer import timeout
import subprocess
import copy
import sys
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー
import datetime

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass

from const import *


@dataclass(frozen=True)
class ChromeDriverHelperValue:
    """Chromeドライバ値オブジェクト
    """
    url: str
    selectors: list
    title: str
    last_image_url: str

    def __init__(self, url, selectors, title, last_image_url):
        """完全コンストラクタパターン
        :param url: str 処理対象サイトURL
        :param selectors: list スクレイピングする際のセレクタリスト
        :param title: str 取得したサイトタイトル
        :param last_image_url: str 取得した最終画像のURL
        """
        if url is not None:
            if not self.is_url_only(url):
                raise ValueError(f"不正:引数urlがURLではない[{url}]")
            object.__setattr__(self, "url", url)
        if selectors is not None:
            object.__setattr__(self, "selectors", selectors)
        if title is not None:
            object.__setattr__(self, "title", title)
        if last_image_url is not None:
            if not self.is_url_only(last_image_url):
                raise ValueError(f"不正:引数last_image_urlがurlではない[{last_image_url}]")
            object.__setattr__(self, "last_image_url", last_image_url)

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class ChromeDriverHelper:
    """指定のサイトを読み込み、スクレイピングする
    """
    # value_object: ChromeDriverHelperValue = None
    __driver = None
    __source = None
    root_path = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(root_path, r'driver\chromedriver.exe')
    chrome_path = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
    __options = ChromeOptions()
    __port = "9222"
    __chrome_opt = ('debuggerAddress', f'127.0.0.1:{__port}')
    profile_path = r'C:\Users\igapon\temp'
    __cmd = f'{chrome_path}' \
            f' -remote-debugging-port={__port}' \
            f' --user-data-dir="{profile_path}"'

    def __init__(self, value_object, selectors=None):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlとselectorsより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param selectors: list スクレイピングする際のセレクタリスト
        """
        self.__start()
        if value_object is not None:
            if isinstance(value_object, ChromeDriverHelperValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, str):
                    url = value_object
                    if selectors is not None:
                        self.__open_url(url)
                        title, title_sub, last_image_url = self.__gen_scraping(selectors)
                        if not title:
                            if not title_sub:
                                # タイトルが得られない時は、タイトルを日時文字列にする
                                now = datetime.datetime.now()
                                title = f'{now:%Y%m%d_%H%M%S}'
                            else:
                                title = title_sub
                        self.back()
                        # NOTE: zipに入れてないので消えてまう
                        self.save_source(os.path.join(OUTPUT_FOLDER_PATH, f'{title}.html'))
                        self.forward()
                        self.value_object = ChromeDriverHelperValue(url,
                                                                    selectors,
                                                                    title,
                                                                    last_image_url,
                                                                    )

    def __add_options(self, *args):
        """オプション追加
        :param args: tuple(str, str) 追加するキーと値
        :return:
        """
        self.__options.add_experimental_option(*args)

    def __start(self):
        """Chromeへの接続を完了する。起動していなければ起動する。
        :return:
        """
        self.__add_options(*self.__chrome_opt)
        try:
            # タイムアウト長いので、なるべくChrome起動してから呼び出したい
            self.__connection()
        except Exception as e:
            print(e, "Chromeが起動していなかったので、起動して接続する。")
            self.__create()
            self.__connection()

    def __connection(self):
        """起動しているchromeに接続
        :return:
        """
        self.__driver = Chrome(executable_path=self.driver_path, options=self.__options)

    def __create(self):
        """chromeを起動する
        :return:
        """
        subprocess.Popen(self.__cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def destroy(self):
        """chromeが開いていれば閉じる
        :return: なし
        """
        if self.__driver is not None:
            self.__driver.close()

    def __open_url(self, url):
        """chromeにurlを開く
        :param url: str chromeで開くURL
        :return: なし
        """
        self.__driver.get(url)

    def __gen_scraping(self, selectors):
        """スクレイピング結果を返すジェネレータ
        chromeで開いているサイトに対してスクレイピングする
        chromeで開いているサイトから、selectorsを辿り、タイトルと、画像リストの最終画像アドレスを取得する
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        """
        for key, list_value in selectors.items():
            while list_value:
                tuple_value = list_value.pop(0)
                by, selector, action = tuple_value
                try:
                    elem = self.__driver.find_element(by=by, value=selector)
                    ret = action(elem)
                except NoSuchElementException:
                    # find_elementでelementが見つからなかったとき
                    ret = ""
                if ret and list_value:
                    ret_parse = urlparse(ret)
                    if 0 < len(ret_parse.scheme):
                        # listの末尾以外で、URLの時は、表示を更新する
                        self.__driver.get(ret)
                else:
                    yield ret

    def get_source(self):
        """chromeで現在表示しているページのソースコードを取得する
        :return: str ソースコード
        """
        self.__source = self.__driver.page_source
        return copy.deepcopy(self.__source)

    def save_source(self, path='./title.html'):
        """ソースコードをファイルに保存する
        :param path: str 保存するファイルパス(URLかタイトルを指定するとよさそう)
        :return:
        """
        html = self.get_source()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_title(self):
        """タイトル取得
        :return: str タイトル
        """
        return copy.deepcopy(self.value_object.title)

    def get_last_image_url(self):
        """最終画像アドレス取得
        :return: str 最終画像アドレス
        """
        return copy.deepcopy(self.value_object.last_image_url)

    def back(self):
        """ブラウザの戻るボタン押下と同じ動作
        :return:
        """
        self.__driver.back()

    def forward(self):
        """ブラウザの進むボタン押下と同じ動作
        :return:
        """
        self.__driver.forward()


if __name__ == '__main__':  # インポート時には動かない
    main_url = None
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        main_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            parse = urlparse(paste_str)
            if 0 < len(parse.scheme):
                main_url = paste_str
        # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()

    driver = ChromeDriverHelper(main_url, SELECTORS)
    main_title = driver.get_title()
    main_image_url = driver.get_last_image_url()
    print(main_image_url + "," + main_title)
    pyperclip.copy(main_image_url + "," + main_title)
