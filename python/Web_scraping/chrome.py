#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
サイトURLより、タイトルを取得する
サイトURLより、サイト末尾のimageURLを取得する

参考ブログ
https://note.nkmk.me/python/
https://maku77.github.io/python/
参考リファレンス
https://www.seleniumqref.com/api/webdriver_gyaku.html
https://www.selenium.dev/ja/documentation/webdriver/getting_started/

"""
import time
import subprocess
import copy
import sys
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from dataclasses import dataclass

# exec_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
driver_path = r'C:\Git\igapon50\traning\python\Web_scraping\driver\chromedriver.exe'
cmd = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"' \
      r' -remote-debugging-port=9222' \
      r' --user-data-dir="C:\Users\igapon\temp"'


@dataclass(frozen=True)
class SeleniumDriverValue:
    """Chromeドライバ値オブジェクト
    """
    url: list
    selectors: list
    title: str
    image_url: str

    def __init__(self, url, selectors, title, image_url):
        """完全コンストラクタパターン
        :param url: str 処理対象サイトURL
        :param selectors: list スクレイピングする際のセレクタリスト
        :param title: str 取得したサイトタイトル
        :param image_url: str 取得した最終画像のURL
        """
        if url is not None:
            object.__setattr__(self, "url", url)
        if selectors is not None:
            object.__setattr__(self, "selectors", selectors)
        if title is not None:
            object.__setattr__(self, "title", title)
        if image_url is not None:
            object.__setattr__(self, "image_url", image_url)


class SeleniumDriver:
    """指定のサイトを読み込み、スクレイピングする
    """
    value_object: SeleniumDriverValue = None
    driver = None

    def __init__(self, value_object, selectors=None):
        """コンストラクタ
        値オブジェクトからの復元、もしくは、urlとselectorsより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param selectors: list スクレイピングする際のセレクタリスト
        """
        if value_object is not None:
            if isinstance(value_object, SeleniumDriverValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, str):
                    url = value_object
                    if selectors is not None:
                        title, image_url = self.gen_scraping(url, selectors)
                        self.value_object = SeleniumDriverValue(url,
                                                                selectors,
                                                                title,
                                                                image_url,
                                                                )

    def gen_scraping(self, url, selectors):
        """スクレイピング結果を返すジェネレータ
        chromeを起動して、urlからselectorsを辿り、画像リストの最終画像アドレスと、タイトルを取得する
        :param url: str スクレイピングの開始ページ
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        """
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = Chrome(executable_path=driver_path, options=options)
        time.sleep(3)
        self.driver.get(url)
        # todo 表示されるまで待つ
        for key, list_value in selectors.items():
            while list_value:
                tuple_value = list_value.pop(0)
                by, selector, action = tuple_value
                elem = self.driver.find_element(by=by, value=selector)
                ret = action(elem)
                if list_value:
                    ret_parse = urlparse(ret)
                    if 0 < len(ret_parse.scheme):
                        # listの末尾以外で、URLの時は、表示を更新する
                        self.driver.get(ret)
                else:
                    yield ret

    def __del__(self):
        """デストラクタ
        chromeが開いていれば閉じる
        :return: なし
        """
        if self.driver is not None:
            self.driver.close()

    def get_title(self):
        """タイトル取得
        :return: str タイトル
        """
        return copy.deepcopy(self.value_object.title)

    def get_image_url(self):
        """最終画像アドレス取得
        :return: str 最終画像アドレス
        """
        return copy.deepcopy(self.value_object.image_url)


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
        'title': [(By.XPATH,
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
    driver = SeleniumDriver(main_url, main_selectors)
    main_title = driver.get_title()
    print(main_title)
    main_image_url = driver.get_image_url()
    print(main_image_url)
