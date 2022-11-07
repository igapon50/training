#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Selenium Chromeドライバのヘルパー
Chrome.batを実行して、Chromeを起動しておくと、その続きから操作できる。
スクレイピングしたいurlをクリップボードにコピーして、実行するとスクレイピング結果がクリップボードに入る
    destroy Chromeを閉じる
    get_source Chromeで表示しているタブのsourceを取得する
    save_source Chromeで表示しているタブのsourceをファイルに保存する
    get_title タイトルを取得する
    get_last_image_url 最終画像アドレスを取得する
    back (画面遷移有)ブラウザの戻るボタン押下と同じ動作
    forward (画面遷移有)ブラウザの進むボタン押下と同じ動作
    next_tab (画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ後のタブを表示する
    previous_tab (画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ前のタブを表示する
    open (画面遷移有)新しいタブでurlを開く
    open_tabs (画面遷移有)新しいタブでurlリストを開く
    close (画面遷移有)指定の画面か、現在の画面を閉じる
    download_image (画面依存)表示されている画像を保存する(Chromeデフォルトダウンロードフォルダに保存)

参考ブログ
https://note.nkmk.me/python/
https://maku77.github.io/python/
https://nikkie-ftnext.hatenablog.com/entry/value-object-python-dataclass
https://blog.wotakky.net/2018/08/12/post-4829/
参考リファレンス
https://selenium-python.readthedocs.io/
https://www.seleniumqref.com/api/webdriver_gyaku.html
https://www.selenium.dev/ja/documentation/webdriver/getting_started/
https://kurozumi.github.io/selenium-python/index.html

"""
import subprocess
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

from webFileListHelper import *


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
                raise ValueError(f"{self.__class__}引数エラー:urlがURLではない[{url}]")
            object.__setattr__(self, "url", url)
        if selectors is not None:
            object.__setattr__(self, "selectors", selectors)
        if title is not None:
            object.__setattr__(self, "title", title)
        if last_image_url is not None:
            if not self.is_url_only(last_image_url):
                raise ValueError(f"{self.__class__}引数エラー:last_image_urlがurlではない[{last_image_url}]")
            object.__setattr__(self, "last_image_url", last_image_url)

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class ChromeDriverHelper:
    """指定のサイトを読み込み、スクレイピングする
    """
    value_object: ChromeDriverHelperValue = None
    __driver = None
    __source = None
    __start_window_handle = None
    __window_handle_list = []
    root_path = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(root_path, r'driver\chromedriver.exe')
    chrome_path = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
    __options = ChromeOptions()
    __port = "9222"
    __default_directory = WebFileListHelper.folder_path
    __chrome_add_argument = ['--blink-settings=imagesEnabled=false',  # 画像非表示
                             # '--incognito',  # シークレットモードで起動する
                             # '--headless',  # バックグラウンドで起動する
                             ]
    __chrome_add_experimental_option = [('debuggerAddress', f'127.0.0.1:{__port}'),
                                        # TODO: prefsはdebuggerAddressと同時に指定できない？
                                        # ('prefs', {'download.default_directory': __default_directory}),
                                        ]
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
        if value_object:
            if isinstance(value_object, ChromeDriverHelperValue):
                self.value_object = value_object
            elif isinstance(value_object, str):
                url = value_object
                if selectors:
                    self.__open_url(url)
                    # image_urls_list = None
                    # title, title_sub, last_image_url = self.__gen_scraping_element(selectors)
                    # print(title, title_sub, last_image_url)
                    last_image_url = None
                    title, title_sub, image_urls_list = self.__gen_scraping_selectors(selectors)
                    print(title, title_sub, image_urls_list)
                    if title and isinstance(title, list):
                        title = title[0]
                    if title_sub and isinstance(title_sub, list):
                        title_sub = title_sub[0]
                    if image_urls_list and image_urls_list[0]:
                        last_image_url = image_urls_list[0]
                    if not title:
                        if not title_sub:
                            # タイトルが得られない時は、タイトルを日時文字列にする
                            now = datetime.datetime.now()
                            title = f'{now:%Y%m%d_%H%M%S}'
                        else:
                            title = title_sub
                    title = self.fixed_file_name(title)
                    url_title = self.fixed_file_name(url)
                    # self.back()
                    # NOTE: ここに保存すると、zipに入れてないので消えてまう
                    # self.save_source(os.path.join(OUTPUT_FOLDER_PATH, f'{title}／{url}.html').replace(os.sep, '/'))
                    self.save_source(f'{title}：{url_title}.html')
                    # self.forward()
                    if last_image_url:
                        self.value_object = ChromeDriverHelperValue(url,
                                                                    selectors,
                                                                    title,
                                                                    last_image_url,
                                                                    )
                    else:
                        raise ValueError(f"{self.__class__}引数エラー:image_urls_listが不正[{image_urls_list}]")

    @staticmethod
    def fixed_path(file_path):
        """フォルダ名の禁止文字を全角文字に置き換える
        :param file_path: str 置き換えたいフォルダパス
        :return: str 置き換え後のフォルダパス
        """
        __file_path = copy.deepcopy(file_path)
        __file_path = __file_path.replace(':', '：')
        __file_path = __file_path.replace('*', '＊')
        __file_path = __file_path.replace('?', '？')
        __file_path = __file_path.replace('"', '”')
        __file_path = __file_path.replace('<', '＜')
        __file_path = __file_path.replace('>', '＞')
        __file_path = __file_path.replace('|', '｜')
        return __file_path

    def fixed_file_name(self, file_name):
        """ファイル名の禁止文字を全角文字に置き換える
        :param file_name: str 置き換えたいファイル名
        :return: str 置き換え後のファイル名
        """
        __file_name = copy.deepcopy(file_name)
        __file_name = __file_name.replace(os.sep, '￥')
        __file_name = __file_name.replace('/', '／')
        return self.fixed_path(__file_name)

    def __add_options(self, *args):
        """オプション追加
        :param args: tuple(str, str) 追加するキーと値
        :return:
        """
        self.__options.add_experimental_option(*args)

    def __add_argument(self, args):
        self.__options.add_argument(args)

    def __start(self):
        """Chromeへの接続を完了する。起動していなければ起動する。
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
            for __window_handle in self.__window_handle_list:
                self.close()
            if self.__start_window_handle:
                self.__driver.switch_to.window(self.__start_window_handle)
                self.__driver.close()
                self.__start_window_handle = None
            self.__driver.quit()
            self.__driver = None

    def __open_url(self, url):
        """(画面依存)chromeにurlを開く
        :param url: str chromeで開くURL
        :return: なし
        """
        self.__driver.get(url)

    def __gen_scraping_element(self, selectors):
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        selectorsで、タイトルmainと、タイトルsub、画像リストの最終画像アドレスを指定する
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
        :return: str スクレイピング結果を返す
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
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ
        selectorsで、タイトルmainと、タイトルsub、画像のアドレスリストor最終画像青ドレスを指定する
        :param selectors: list dict list tuple(by, selector, action) スクレイピングの規則
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
                count = len(__temp_window_handle_list)
            else:
                count = 1
            for _ in range(count):
                elements = self.__driver.find_elements(by=by, value=selector)
                for elem in elements:
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
        new_path = self.fixed_path(path)
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_title(self):
        """タイトル取得
        :return: str タイトル
        """
        if self.value_object:
            return copy.deepcopy(self.value_object.title)
        return None

    def get_last_image_url(self):
        """最終画像アドレス取得
        :return: str 最終画像アドレス
        """
        if self.value_object:
            return copy.deepcopy(self.value_object.last_image_url)
        return None

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

    def open(self, url):
        """(画面遷移有)新しいタブでurlを開く
        :param url: str 開くURL
        :return: str 開いたタブのハンドル
        """
        self.__driver.switch_to.new_window()
        self.__open_url(url)
        self.__window_handle_list.append(self.__driver.current_window_handle)
        return self.__window_handle_list[-1]

    def open_tabs(self, url_list):
        """(画面遷移有)新しいタブでurlリストを開く
        :param url_list:  list[str] 開くURLのリスト
        :return: list[str] 開いたタブのハンドルリスト
        """
        window_handle_list = []
        for url in url_list:
            window_handle_list.append(self.open(url))
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

    def download_image(self):
        """(画面依存)表示されている画像を保存する
        chromeのデフォルトダウンロードフォルダに保存される
        ダウンロード実行用スクリプトを生成＆実行する
        :return:
        """
        __image_url = self.__driver.current_url
        __web_file = WebFileHelper(__image_url)
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

