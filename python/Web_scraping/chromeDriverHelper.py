#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Selenium Chromeドライバのヘルパー
Chrome.batを実行して、Chromeを起動しておくと、その続きから操作できる。
コンストラクタで引数を指定するとスクレイピングまで実施されてget_value_objectが有効になる
    fixed_path (staticmethod)フォルダ名の禁止文字を全角文字に置き換える
    fixed_file_name ファイル名の禁止文字を全角文字に置き換える
    get_value_object 値オブジェクトを取得する
    get_url URLを取得する
    get_selectors セレクタを取得する
    get_items スクレイピング結果を取得する
    scraping 現在表示のURLにスクレイピングする
    destroy Chromeを閉じる
    get_source Chromeで表示しているタブのsourceを取得する
    save_source Chromeで表示しているタブのsourceをファイルに保存する
    back (画面遷移有)ブラウザの戻るボタン押下と同じ動作
    forward (画面遷移有)ブラウザの進むボタン押下と同じ動作
    next_tab (画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ後のタブを表示する
    previous_tab (画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ前のタブを表示する
    download_image (画面遷移有)urlの画像を保存する(open_new_tab → save_image → closeする)
    open_current_tab (画面依存)現在表示されているタブでurlを開く
    open_new_tab (画面遷移有)新しいタブでurlを開く
    open_new_tabs (画面遷移有)新しいタブでurlリストを開く
    close (画面遷移有)指定の画面か、現在の画面を閉じる
    save_image (画面依存)表示されている画像を保存する(Chromeデフォルトダウンロードフォルダに保存)

参考ブログ
https://note.nkmk.me/python/
https://maku77.github.io/python/
https://nikkie-ftnext.hatenablog.com/entry/value-object-python-dataclass
https://blog.wotakky.net/2018/08/12/post-4829/
https://www.zacoding.com/post/selenium-custom-wait/
参考リファレンス
https://selenium-python.readthedocs.io/
https://www.seleniumqref.com/api/webdriver_gyaku.html
https://www.selenium.dev/ja/documentation/webdriver/getting_started/
https://kurozumi.github.io/selenium-python/index.html

"""
import os
import copy
import sys

import subprocess
import datetime
import time
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdrivermanager import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass

from const import *
from webFileHelper import *
from webFileListHelper import *


@dataclass(frozen=True)
class ChromeDriverHelperValue:
    """Chromeドライバ値オブジェクト"""
    url: str = None
    selectors: dict = None
    items: dict = None

    def __init__(self, url, selectors, items):
        """完全コンストラクタパターン
        :param url: str 処理対象サイトURL
        :param selectors: dict スクレイピングする際のセレクタリスト
        :param items: dict スクレイピングして取得した値の辞書
        """
        if not url:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:urlが不正[{url}]")
        if not selectors:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:selectorsが不正[{selectors}]")
        if not items:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:itemsが不正[{items}]")
        if not isinstance(url, str):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:urlがstrではない")
        if not isinstance(selectors, dict):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:selectorsがdictではない")
        if not isinstance(items, dict):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:itemsがdictではない")
        if not self.is_url_only(url):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:urlがURLではない[{url}]")
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "selectors", selectors)
        object.__setattr__(self, "items", items)

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class ChromeDriverHelper:
    """chromeドライバを操作する
    """
    value_object: ChromeDriverHelperValue = None
    download_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'download').replace(os.sep, '/')

    __driver = None
    __wait = None
    __source = None
    __start_window_handle = None
    __window_handle_list = []
    root_path = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(root_path, r'driver\chromedriver.exe')
    chrome_path = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
    __options = ChromeOptions()
    __port = "9222"
    __chrome_add_argument = ['--blink-settings=imagesEnabled=false',  # 画像非表示
                             # '--incognito',  # シークレットモードで起動する
                             # '--headless',  # バックグラウンドで起動する
                             ]
    __chrome_add_experimental_option = [('debuggerAddress', f'127.0.0.1:{__port}'),
                                        # TODO: prefsはdebuggerAddressと同時に指定できない？
                                        # ('prefs', {'download.default_directory': download_path}),
                                        ]
    profile_path = r'C:\Users\igapon\temp'
    __cmd = f'{chrome_path}' \
            f' -remote-debugging-port={__port}' \
            f' --user-data-dir="{profile_path}"'

    def __init__(self, value_object=None, selectors=None, download_path=download_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlとselectorsより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param selectors: dict スクレイピングする際のセレクタリスト
        :param download_path: str ダウンロードフォルダのパス
        """
        self.__start()
        if download_path:
            self.download_path = download_path
        if value_object:
            if isinstance(value_object, ChromeDriverHelperValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
            elif isinstance(value_object, str):
                url = value_object
                if selectors:
                    selectors = copy.deepcopy(selectors)
                    self.open_current_tab(url)
                    items = self.scraping(selectors)
                    self.value_object = ChromeDriverHelperValue(url, selectors, items)
                else:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:selectorsが不正[{selectors}]")
            else:
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:value_objectが不正[{value_object}]")

    @staticmethod
    def fixed_path(file_path):
        """フォルダ名の禁止文字を全角文字に置き換える
        :param file_path: str 置き換えたいフォルダパス
        :return: str 置き換え後のフォルダパス
        """
        file_path = file_path.replace(':', '：')
        file_path = file_path.replace('*', '＊')
        file_path = file_path.replace('?', '？')
        file_path = file_path.replace('"', '”')
        file_path = file_path.replace('<', '＜')
        file_path = file_path.replace('>', '＞')
        file_path = file_path.replace('|', '｜')
        return file_path

    @staticmethod
    def fixed_file_name(file_name):
        """ファイル名の禁止文字を全角文字に置き換える
        :param file_name: str 置き換えたいファイル名
        :return: str 置き換え後のファイル名
        """
        file_name = file_name.replace(os.sep, '￥')
        file_name = file_name.replace('/', '／')
        return ChromeDriverHelper.fixed_path(file_name)

    def scraping(self, selectors):
        """現在表示のURLにスクレイピングする"""
        selectors = copy.deepcopy(selectors)
        items = {}
        for key, selector_list in selectors.items():
            items[key] = self.__get_scraping_selector_list(selector_list)
        return items

    def scroll_element(self, element):
        """elementまでスクロールする"""
        actions = ActionChains(self.__driver)
        actions.move_to_element(element)
        actions.perform()

    def get_value_object(self):
        """値オブジェクトを取得する"""
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:value_object")

    def get_url(self):
        """URLを取得する"""
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().url)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:url")

    def get_selectors(self):
        """セレクタを取得する"""
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().selectors)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:selectors")

    def get_items(self):
        """スクレイピング結果を取得する"""
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().items)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:items")

    def __add_options(self, *args):
        """オプション追加
        :param args: tuple(str, str) 追加するキーと値
        :return:
        """
        self.__options.add_experimental_option(*args)

    def __add_argument(self, args):
        self.__options.add_argument(args)

    def __start(self):
        """Chromeへの接続を完了する。起動していなければ起動する。既に開いているtabは、とりあえず気にしない
        :return:
        """
        # TODO: __add_argumentが効いてない、使い方を調べる
        #        for arg in self.__chrome_add_argument:
        #            self.__add_argument(arg)
        for args in self.__chrome_add_experimental_option:
            print(*args)
            self.__add_options(*args)
        try:
            # NOTE: タイムアウト長いので、なるべくChrome起動してから呼び出したい
            self.__connection()
        except Exception as e:
            print(e, "Chromeが起動していなかったので、起動して接続する。")
            self.__create()
            self.__connection()
        self.__start_window_handle = self.__driver.current_window_handle

    def __connection(self):
        """起動しているchromeに接続
        :return:
        """
        self.__driver = Chrome(executable_path=ChromeDriverManager().install(), options=self.__options)

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
            for __window_handle in self.__window_handle_list:
                self.close()
            if self.__start_window_handle:
                self.__driver.switch_to.window(self.__start_window_handle)
                self.__driver.close()
                self.__start_window_handle = None
            self.__driver.quit()
            self.__driver = None

    def __gen_scraping_selectors(self, selectors):
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        :param selectors: dict{key, list[tuple(by, selector, action)]}] スクレイピングの規則
        :return: list[str] スクレイピング結果をlistに入れて返す
        """
        for key, selector_list in selectors.items():
            while selector_list:
                by, selector, action = selector_list.pop(0)
                ret_list = self.__get_scraping_selector(by, selector, action)
                if ret_list and ret_list[0] and selector_list:
                    # ret_listに値があり、selector_listの末尾ではない時
                    for url in ret_list:
                        ret_parse = urlparse(url)
                        if ret_parse.scheme:
                            self.open_new_tab(url)
                        else:
                            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                             f"引数エラー:urlが不正[{url}]")
                else:
                    for _ in self.__window_handle_list:
                        self.close()
                    yield ret_list

    def __get_scraping_selector_list(self, selector_list):
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        :param selector_list: list[tuple(by, selector, action)] スクレイピングの規則
        :return: list[str] スクレイピング結果をlistに入れて返す
        """
        selector_list = copy.deepcopy(selector_list)
        while selector_list:
            by, selector, action = selector_list.pop(0)
            ret_list = self.__get_scraping_selector(by, selector, action)
            if ret_list and ret_list[0] and selector_list:
                # ret_listに値があり、selector_listの末尾ではない時
                for url in ret_list:
                    ret_parse = urlparse(url)
                    if ret_parse.scheme:
                        self.open_new_tab(url)
                    else:
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:urlが不正[{url}]")
            else:
                for _ in self.__window_handle_list:
                    self.close()
                return ret_list

    def __get_scraping_selector(self, by, selector, action):
        """(画面遷移有)現在の画面(self._window_handle_listがあればそれ、無ければself.__start_window_handle)について、
        スクレイピングして、画面を閉じて、結果を返す
        :param by:
        :param selector:
        :param action:
        :return:
        """
        try:
            ret_list = []
            __temp_window_handle_list = copy.deepcopy(self.__window_handle_list)
            if __temp_window_handle_list:
                count = len(__temp_window_handle_list)
            else:
                count = 1
            for _ in range(count):
                elements = self.__driver.find_elements(by=by, value=selector)
                for elem in elements:
                    self.scroll_element(elem)
                    text = action(elem)
                    ret_list.append(text)
                self.close()
        except NoSuchElementException:
            # find_elementsでelementが見つからなかったとき
            ret_list = [""]
        return ret_list

    def get_source(self):
        """(画面依存)現在の画面(chromeで現在表示しているタブ)のソースコードを取得する
        :return: str ソースコード
        """
        self.__source = self.__driver.page_source
        return copy.deepcopy(self.__source)

    def save_source(self, path='./title.html'):
        """(画面依存)現在の画面のソースコードをファイルに保存する
        :param path: str 保存するファイルパス(URLかタイトルを指定するとよさそう)
        :return:
        """
        html = self.get_source()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def back(self):
        """(画面遷移有)ブラウザの戻るボタン押下と同じ動作
        :return:
        """
        self.__driver.back()

    def forward(self):
        """(画面遷移有)ブラウザの進むボタン押下と同じ動作
        :return:
        """
        self.__driver.forward()

    def next_tab(self):
        """(画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ後のタブを表示する
        :return:
        """
        self.__shift_tab(1)

    def previous_tab(self):
        """(画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ前のタブを表示する
        :return:
        """
        self.__shift_tab(-1)

    def __shift_tab(self, step):
        index = 0
        count = len(self.__window_handle_list)
        if self.__driver.current_window_handle in self.__window_handle_list:
            index = self.__window_handle_list.index(self.__driver.current_window_handle)
        self.__driver.switch_to.window(self.__window_handle_list[(index + step) % count])

    def download_image(self, url, download_path=None):
        """(画面遷移有)urlの画像を保存する(open_new_tab → save_image → closeする)
        :param url: 画像のurl
        :param download_path:
        :return:
        """
        uri = UriHelper(url)
        if uri.is_data_uri(url):
            uri.save_data_uri(download_path)
        else:
            __handle = self.open_new_tab(url)
            self.save_image(uri.get_filename(), uri.get_ext())
            self.close(__handle)

    def open_current_tab(self, url):
        """(画面依存)現在表示されているタブでurlを開く
        :param url: str chromeで開くURL
        :return: なし
        """
        self.__driver.get(url)
        # ページが読み込まれるまで待機
        self.__wait = WebDriverWait(self.__driver, 30)
        self.__wait.until(EC.presence_of_all_elements_located)

    def open_new_tab(self, url):
        """(画面遷移有)新しいタブでurlを開く
        :param url: str 開くURL
        :return: str 開いたタブのハンドル
        """
        self.__driver.switch_to.new_window()
        self.open_current_tab(url)
        self.__window_handle_list.append(self.__driver.current_window_handle)
        return self.__window_handle_list[-1]

    def open_new_tabs(self, url_list):
        """(画面遷移有)新しいタブでurlリストを開く
        :param url_list:  list[str] 開くURLのリスト
        :return: list[str] 開いたタブのハンドルリスト
        """
        window_handle_list = []
        for url in url_list:
            window_handle_list.append(self.open_new_tab(url))
        return window_handle_list

    def close(self, window_handle=None):
        """(画面遷移有)openで開いた画面の内、指定の画面か、現在の画面を閉じる
        :param window_handle: str 閉じる画面のハンドル
        :return: None
        """
        try:
            if not window_handle:
                window_handle = self.__driver.current_window_handle
            else:
                self.__driver.switch_to.window(window_handle)
            if window_handle == self.__start_window_handle:
                return
            if self.__driver.current_window_handle == self.__start_window_handle:
                return
            index = self.__window_handle_list.index(window_handle)
            self.__driver.close()
            del self.__window_handle_list[index]
            if len(self.__window_handle_list) == 0:
                self.__driver.switch_to.window(self.__start_window_handle)
            else:
                if index:
                    index -= 1
                self.__driver.switch_to.window(self.__window_handle_list[index])
        except ValueError:
            print("ValueError 指定のwindow_handleがありません。")
            exit()

    def save_image(self, download_file_name, download_ext='.jpg', wait_time=3):
        """(画面依存)表示されている画像を保存する
        chromeのデフォルトダウンロードフォルダに保存された後に、指定のフォルダに移動する
        ダウンロード実行用スクリプトを生成＆実行する
        :return:
        """
        __image_url = self.__driver.current_url
        downloads_path = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "downloads")
        __web_file = WebFileHelper(__image_url, download_file_name, download_ext, downloads_path)
        __filename = __web_file.get_filename() + __web_file.get_ext()
        script_str = """
        window.URL = window.URL || window.webkitURL;

        var xhr = new XMLHttpRequest(),
        a = document.createElement('a'), file;

        xhr.open('GET', '""" + __image_url + """', true);
        xhr.responseType = 'blob';
        xhr.onload = function () {
        file = new Blob([xhr.response], { type : 'application/octet-stream' });
        a.href = window.URL.createObjectURL(file);
        a.download = '""" + __filename + """';
        a.click();
        };
        xhr.send();
        """
        self.__driver.execute_script(script_str)
        file_path = os.path.join(self.download_path, __filename)
        # TODO: メソッド化する
        # what = (lambda web_file, path: web_file.move(path))(__web_file, file_path)
        # how = (lambda web_file: os.path.isfile(web_file.get_path()))(__web_file)
        # self.wait_until(what, how)
        start = time.time()
        while ((time.time() - start) < wait_time) and not (os.path.isfile(__web_file.get_path())):
            time.sleep(0.1)
        __web_file.move(file_path)

    # @staticmethod
    # def wait_until(what, how, wait_time=3):
    #     """what(何)を実行するために、how(どのように)なるまで最大でwait_time秒間待つ"""
    #     start = time.time()
    #     while ((time.time() - start) < wait_time) and not (how):
    #         time.sleep(0.1)
    #     return what
