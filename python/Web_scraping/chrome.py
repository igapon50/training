#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chrome.batを実行して、スクレイピングしたいurlをクリップボードにコピーして、実行する。
    起動しているChromeに接続する、起動していなければ起動して接続する
    Chromeに接続する
    Chromeを起動する
    ChromeでURLを開く
    Chromeで開いているサイトのsourceを取得する
    Chromeを閉じる

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
import timeout_decorator
from timeout_timer import timeout
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


@dataclass(frozen=True)
class ChromeDriverValue:
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


class ChromeDriver:
    """指定のサイトを読み込み、スクレイピングする
    """
    value_object: ChromeDriverValue = None
    driver = None
    root = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(root, r'driver\chromedriver.exe')
    profile_path = r'C:\Users\igapon\temp'
    cmd = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"' \
          r' -remote-debugging-port=9222' \
          f' --user-data-dir="{profile_path}"'

    def __init__(self, value_object, selectors=None):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlとselectorsより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param selectors: list スクレイピングする際のセレクタリスト
        """
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        try:
            self.connection(options)
        except StopIteration as e:
            print(e, "Chromeが起動していなかったので、起動する。タイムアウト")
            self.create(options)
        except Exception as e:
            print(e, "Chromeが起動していなかったので、起動する。その他")
            self.create(options)
        if value_object is not None:
            if isinstance(value_object, ChromeDriverValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, str):
                    url = value_object
                    if selectors is not None:
                        title_en, title, last_image_url = self.gen_scraping(url, selectors)
                        if not title:
                            title = title_en
                        self.value_object = ChromeDriverValue(url,
                                                              selectors,
                                                              title,
                                                              last_image_url,
                                                              )

    # 以下のタイムアウト上手く動かせなかった
    # @timeout_decorator.timeout(5, use_signals=False, timeout_exception=StopIteration)
    # @timeout_decorator.timeout(5, timeout_exception=StopIteration)
    # @timeout_decorator.timeout(5)
    # @timeout(5)
    def connection(self, options):
        # 起動しているchromeに接続
        self.driver = Chrome(executable_path=self.driver_path, options=options)

    def create(self, options):
        # chromeを起動して接続
        subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.driver = Chrome(executable_path=self.driver_path, options=options)

    def gen_scraping(self, url, selectors):
        """スクレイピング結果を返すジェネレータ
        chromeで開いているサイトから、selectorsを辿り、タイトルと、画像リストの最終画像アドレスを取得する
        :param url: str スクレイピングの開始ページ
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        """
        self.driver.get(url)
        for key, list_value in selectors.items():
            while list_value:
                tuple_value = list_value.pop(0)
                by, selector, action = tuple_value
                try:
                    elem = self.driver.find_element(by=by, value=selector)
                    ret = action(elem)
                except NoSuchElementException:
                    # find_elementでelementが見つからなかったとき
                    now = datetime.datetime.now()
                    ret = f'{now:%Y%m%d_%H%M%S}'
                if list_value:
                    ret_parse = urlparse(ret)
                    if 0 < len(ret_parse.scheme):
                        # listの末尾以外で、URLの時は、表示を更新する
                        self.driver.get(ret)
                else:
                    yield ret

    def close(self):
        """chromeが開いていれば閉じる
        :return: なし
        """
        if self.driver is not None:
            self.driver.close()

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

    main_selectors = {
        'title_en': [(By.XPATH,
                      '//div/div/div/h1',  # //*[@id="info"]/h1
                      lambda el: el.text),
                     ],
        'title_jp': [(By.XPATH,
                      '//div/div/div/h2',  # //*[@id="info"]/h2
                      lambda el: el.text),
                     ],
        'image_url': [(By.XPATH,
                       '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
                       lambda el: el.get_attribute("href")),
                      (By.XPATH,
                       '//*[@id="image-container"]/a/img',
                       lambda el: el.get_attribute("src")),
                      ],
    }
    driver = ChromeDriver(main_url, main_selectors)
    main_title = driver.get_title()
    main_image_url = driver.get_last_image_url()
    print(main_image_url + "," + main_title)
    pyperclip.copy(main_image_url + "," + main_title)
    # driver.close()
