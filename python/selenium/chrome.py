#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
サイトURLより、タイトルを取得する
サイトURLより、サイト末尾のimageURLを取得する

参考ブログ
https://yaspage.com/python-memo-selenium/
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

    def __init__(self, value_object=None, selectors=None):
        """コンストラクタ
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
                        title, image_url = self.driver_open(url, selectors)
                        self.value_object = SeleniumDriverValue(url,
                                                                selectors,
                                                                title,
                                                                image_url,
                                                                )

    def driver_open(self, url, selectors):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = Chrome(executable_path=driver_path, options=options)
        self.driver.get(url)
        # time.sleep(2)
        element = self.driver.find_element(by=By.XPATH, value=selectors['title'])
        title = element.text
        element = self.driver.find_element(by=By.XPATH, value=selectors['last_image_href'])
        image_url = element.get_attribute('href')
        self.driver.get(image_url)
        # time.sleep(2)
        element = self.driver.find_element(by=By.XPATH, value=selectors['image_url'])
        image_url = element.get_attribute('src')
        return title, image_url

    def __del__(self):
        if self.driver is not None:
            self.driver.close()

    def get_title(self):
        return copy.deepcopy(self.value_object.title)

    def get_image_url(self):
        return copy.deepcopy(self.value_object.image_url)


if __name__ == '__main__':  # インポート時には動かない
    # exec_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    driver_path = r'C:\Git\igapon50\traning\python\selenium\driver\chromedriver.exe'
    cmd = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"' \
          r' -remote-debugging-port=9222' \
          r' --user-data-dir="C:\Users\igapon\temp"'
    main_url = None
    main_selectors = {
        # //*[@id="info"]/h2
        'title': '//div/div/div/h2',
        # //*[@id="thumbnail-container"]/div/div[32]/a
        'last_image_href': '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
        'image_url': '//*[@id="image-container"]/a/img',
    }

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

    driver = SeleniumDriver(main_url, main_selectors)
    main_title = driver.get_title()
    print(main_title)
    main_image_url = driver.get_image_url()
    print(main_image_url)
