#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
関数群、ユーティリティ
"""
# standard library
import sys  # 終了時のエラー有無
import re  # 正規表現モジュール
import pathlib  # 相対パス絶対パス変換
import zipfile  # zipファイル
import os  # ファイルパス分解
import shutil  # 高水準のファイル操作
import glob  # ファイル一覧取得
import inspect
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

# 3rd party packages
import requests  # HTTP通信
import urllib3
from urllib3.util.retry import Retry
import bs4  # Beautiful Soup
import pyperclip  # クリップボード

# Selenium
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.microsoft import IEDriverManager
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from webdriver_manager.opera import OperaDriverManager

# local source
from python.Web_scraping.const import *


def HTML2imglist_SeleniumFireFox(base_url, imglist_filepath, title, file_urllist):
    """
    (Selenium_FireFox版)指定したURLからタイトルと画像URLリストを読み込みクリップボードとファイルに書き込む
    img_css_selectで指定したタグのimg_attrで指定した属性を画像URL扱いする。img_css_selectは、CSSセレクタで指定する。

    :param base_url: str 対象のURL
    :param imglist_filepath: str URLリストを保存するファイルパス
    :param title: str タイトルリストを返す
    :param file_urllist: list 画像URLリストを返す
    :return: bool True 成功 / False 失敗(引数チェックエラーで中断)
    """
    # 引数チェック
    if 0 == len(base_url):
        print(inspect.stack()[1].function + '引数base_urlが空です。')
        return False
    if not isinstance(file_urllist, list):
        print(inspect.stack()[1].function + '引数file_urllistがlistではないです。')
        return False

    # ブラウザの起動
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    # driver = webdriver.Ie(IEDriverManager().install())
    # driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    # driver = webdriver.Opera(executable_path=OperaDriverManager().install())

    # Webページにアクセスする
    driver.get(base_url)
    # 指定した要素が表示されるまで、明示的に30秒待機する
    try:
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'image-container'))
            # EC.presence_of_element_located((By.CSS_SELECTOR, img_css_select))
        )
    finally:
        driver.implicitly_wait(1)
        # ソースコードを取得
        page_source = driver.page_source
        soup = bs4.BeautifulSoup(page_source, 'html.parser')
        title_tag = soup.title
        title.append(title_tag.string)
        print(title_tag.string)
        with open(imglist_filepath, 'w', encoding='utf-8') as imglist_file:
            buff = str(title[0]) + '\n'  # クリップボード用変数にタイトル追加
            for img in soup.select(img_css_select):
                absolute_path = str(img[img_attr])
                parse = urlparse(absolute_path)
                if 0 == len(parse.scheme):  # 絶対パスかチェックする
                    absolute_path = urljoin(base_url, absolute_path)
                file_urllist.append(absolute_path)
                print(absolute_path)
                buff += absolute_path + '\n'  # クリップボード用変数にurl追加
            imglist_file.write(buff)  # ファイルへの保存
            pyperclip.copy(buff)  # クリップボードへのコピー
        driver.quit()  # ドライバを終了し、関連するすべてのウィンドウを閉じます。
#        driver.close()  # ブラウザを終了する(全てのウィンドウを閉じる）
    return True
