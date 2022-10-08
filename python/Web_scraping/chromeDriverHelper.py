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
# import timeout_decorator
# from timeout_timer import timeout
import subprocess
import copy
import sys
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー
import datetime
import time

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


def fixed_file_name(file_name):
    __file_name = copy.deepcopy(file_name)
    __file_name = __file_name.replace(os.sep, '￥')
    __file_name = __file_name.replace('/', '／')
    return fixed_path(__file_name)


def fixed_path(file_path):
    __file_path = copy.deepcopy(file_path)
    __file_path = __file_path.replace(':', '：')
    __file_path = __file_path.replace('*', '＊')
    __file_path = __file_path.replace('?', '？')
    __file_path = __file_path.replace('"', '”')
    __file_path = __file_path.replace('<', '＜')
    __file_path = __file_path.replace('>', '＞')
    __file_path = __file_path.replace('|', '｜')
    return __file_path


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
    __start_window_handle = None
    __window_handle_list = []
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

    def __init__(self, value_object=None, selectors=None):
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
                        # title, title_sub, last_image_url = self.__gen_scraping_element(selectors)
                        # if not title:
                        #     if not title_sub:
                        #         # タイトルが得られない時は、タイトルを日時文字列にする
                        #         now = datetime.datetime.now()
                        #         title = f'{now:%Y%m%d_%H%M%S}'
                        #     else:
                        #         title = title_sub
                        # title = fixed_file_name(title)
                        # url_title = fixed_file_name(url)
                        # self.back()
                        # # NOTE: ここに保存すると、zipに入れてないので消えてまう
                        # # self.save_source(os.path.join(OUTPUT_FOLDER_PATH, f'{title}／{url}.html').replace(os.sep, '/'))
                        # self.save_source(f'{title}：{url_title}.html')
                        # self.forward()
                        # self.value_object = ChromeDriverHelperValue(url,
                        #                                             selectors,
                        #                                             title,
                        #                                             last_image_url,
                        #                                             )
                        title, title_sub, image_urls_list = self.__gen_scraping_selectors(selectors)
                        print(title, title_sub, image_urls_list)

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
        self.__start_window_handle = self.__driver.current_window_handle

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
            self.__driver.quit()

    def __open_url(self, url):
        """chromeにurlを開く
        :param url: str chromeで開くURL
        :return: なし
        """
        self.__driver.get(url)

    def __gen_scraping_element(self, selectors):
        """chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        selectorsで、タイトルmainと、タイトルsub、画像リストの最終画像アドレスを指定する
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        """
        for key, list_value in selectors.items():
            while list_value:
                tuple_value = list_value.pop(0)
                by, selector, action = tuple_value
                try:
                    element = self.__driver.find_element(by=by, value=selector)
                    ret = action(element)
                except NoSuchElementException:
                    # find_elementでelementが見つからなかったとき
                    ret = ""
                if ret and list_value:
                    ret_parse = urlparse(ret)
                    if ret_parse.scheme:
                        # listの末尾以外で、URLの時は、表示を更新する
                        self.__driver.get(ret)
                else:
                    yield ret

    def __gen_scraping_selectors(self, selectors):
        """chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        selectorsで、タイトルmainと、タイトルsub、画像のアドレスリストを指定する
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        """
        for key, selector_list in selectors.items():
            #         yield self.__gen_scraping_selector_list(selector_list)
            #
            # def __gen_scraping_selector_list(self, selector_list):
            #     """(画面遷移有)現在の画面(self._window_handle_list)から、多重スクレイピングして、結果を返す
            #     :param selector_list:
            #     :return:
            #     """
            while selector_list:
                by, selector, action = selector_list.pop(0)
                ret_list = self.__get_scraping_selector(by, selector, action)
                if ret_list and ret_list[0] and selector_list:
                    # ret_listに値があり、selector_listの末尾ではない時
                    for url in ret_list:
                        ret_parse = urlparse(url)
                        if ret_parse.scheme:
                            self.open(url)
                        else:
                            print(f"URLではない：{url}")
                            exit()
                else:
                    for _ in self.__window_handle_list:
                        self.close()
                    yield ret_list

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
                # 二段目以降のスクレイピング
                for _ in __temp_window_handle_list:
                    elements = self.__driver.find_elements(by=by, value=selector)
                    for elem in elements:
                        text = action(elem)
                        ret_list.append(text)
                    self.close()
            else:
                # 一段目のスクレイピング
                elements = self.__driver.find_elements(by=by, value=selector)
                for elem in elements:
                    text = action(elem)
                    ret_list.append(text)
                # TODO: closeの処理を、__temp_window_handle_listに限定して、呼び出せるようにしたい
                # TODO: 一段目と、二段目を共通処理にしたい
                # self.close()
        except NoSuchElementException:
            # find_elementsでelementが見つからなかったとき
            ret_list = [""]
        return ret_list

    def get_source(self):
        """現在の画面(chromeで現在表示しているタブ)のソースコードを取得する
        :return: str ソースコード
        """
        self.__source = self.__driver.page_source
        return copy.deepcopy(self.__source)

    def save_source(self, path='./title.html'):
        """現在の画面のソースコードをファイルに保存する
        :param path: str 保存するファイルパス(URLかタイトルを指定するとよさそう)
        :return:
        """
        html = self.get_source()
        new_path = fixed_path(path)
        with open(new_path, 'w', encoding='utf-8') as f:
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
        self.__shift_tab(1)

    def previous_tab(self):
        self.__shift_tab(-1)

    def __shift_tab(self, step):
        index = 0
        count = len(self.__window_handle_list)
        if self.__driver.current_window_handle in self.__window_handle_list:
            index = self.__window_handle_list.index(self.__driver.current_window_handle)
        self.__driver.switch_to.window(self.__window_handle_list[(index + step) % count])

    def open(self, url):
        """(画面遷移有)新しいタブでurlを開く
        :param url: str 開くURL
        :return: str 開いたタブのハンドル
        """
        self.__driver.switch_to.new_window()
        self.__open_url(url)
        self.__window_handle_list.append(self.__driver.current_window_handle)
        return self.__window_handle_list[-1]

    def open_list(self, url_list):
        """(画面遷移有)新しいタブでurlリストを開く
        :param url_list:  list[str] 開くURLのリスト
        :return: list[str] 開いたタブのハンドルリスト
        """
        window_handle_list = []
        for url in url_list:
            window_handle_list.append(self.open(url))
        return window_handle_list

    def close(self, window_handle=None):
        """(画面遷移有)指定の画面か、現在の画面を閉じる
        :param window_handle: str 閉じる画面のハンドル
        :return: None
        """
        try:
            if not window_handle:
                window_handle = self.__driver.current_window_handle
            else:
                self.__driver.switch_to.window(window_handle)
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


SELECTORS_2 = {
    'title_jp': [(By.XPATH,
                  '//div/div/div/h2',  # //*[@id="info"]/h2
                  lambda el: el.text),
                 ],
    'title_en': [(By.XPATH,
                  '//div/div/div/h1',  # //*[@id="info"]/h1
                  lambda el: el.text),
                 ],
    # 'image_url': [(By.XPATH,
    #                '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
    #                lambda el: el.get_attribute("href")),
    #               (By.XPATH,
    #                '//*[@id="image-container"]/a/img',
    #                lambda el: el.get_attribute("src")),
    #               ],
    'image_urls': [(By.XPATH,
                    '//*[@id="thumbnail-container"]/div/div/a',
                    lambda el: el.get_attribute("href")),
                   (By.XPATH,
                    '//*[@id="image-container"]/a/img',
                    lambda el: el.get_attribute("src")),
                   ],
}

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

    # driver = ChromeDriverHelper(main_url, SELECTORS)
    # main_title = driver.get_title()
    # main_image_url = driver.get_last_image_url()
    # print(main_image_url + "," + main_title)
    # pyperclip.copy(main_image_url + "," + main_title)

    # テスト　若者 | かわいいフリー素材集 いらすとや
    image_url_list = [
        'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'
        '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'
        's180-c/fashion_dekora.png',
        'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/'
        'MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/'
        's180-c/otaku_girl_fashion.png',
        'https://1.bp.blogspot.com/-K8DEj7le73Y/XuhW_wO41mI/AAAAAAABZjQ/'
        'NMEk02WcUBEVBDsEJpCxTN6T0NmqG20qwCNcBGAsYHQ/'
        's180-c/kesyou_jirai_make.png',
    ]
    driver = ChromeDriverHelper()
    driver.open_list(image_url_list)
    for _ in image_url_list:
        driver.next_tab()
        time.sleep(1)
    for _ in image_url_list:
        driver.previous_tab()
        time.sleep(1)
    for _ in image_url_list:
        driver.close()
        time.sleep(1)

    # driver = ChromeDriverHelper("", SELECTORS_2)
