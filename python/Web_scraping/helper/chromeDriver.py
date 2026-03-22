#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selenium Chromeドライバのヘルパー

- selenium chromeでスクレイピングを実施する
- 参考記事
    - https://note.nkmk.me/python/
    - https://maku77.github.io/python/
    - https://nikkie-ftnext.hatenablog.com/entry/value-object-python-dataclass
    - https://blog.wotakky.net/2018/08/12/post-4829/
    - https://www.zacoding.com/post/selenium-custom-wait/
    - https://stackoverflow-com.translate.goog/questions/63421086/modulenotfounderror-no-module-named-webdriver-manager-error-even-after-instal?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=sc
- 参考リファレンス
    - https://selenium-python.readthedocs.io/
    - https://www.seleniumqref.com/api/webdriver_gyaku.html
    - https://www.selenium.dev/ja/documentation/webdriver/getting_started/
    - https://kurozumi.github.io/selenium-python/index.html
"""
import os
import copy
import socket
import subprocess
import time
import inspect
import typing as t
from typing import Any

import psutil
from urllib.parse import urlparse

from dataclasses import dataclass
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import helper.uri
import helper.webFile
import helper.webFileList


@dataclass(frozen=True)
class ChromeDriverValue:
    """Chromeドライバ値オブジェクト"""
    url: str = None
    selectors: dict = None
    items: dict = None

    def __init__(self, url: str, selectors, items):
        """完全コンストラクタパターン

        Args:
            url: str 処理対象サイトURL
            selectors: dict スクレイピングする際のセレクタリスト
            items: dict スクレイピングして取得した値の辞書
        """
        if not url:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:urlが不正[{url}]")
        if not selectors:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:selectorsが不正[{selectors}]")
        if not items:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:itemsが不正[{items}]")
        if not isinstance(url, str):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:urlがstrではない")
        if not isinstance(selectors, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:selectorsがdictではない")
        if not isinstance(items, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:itemsがdictではない")
        if not self.is_url_only(url):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:urlがURLではない[{url}]")
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "selectors", selectors)
        object.__setattr__(self, "items", items)

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class ChromeDriver:
    """chromeドライバを操作する

    Example:
        >>> helper = ChromeDriver(url="https://www.google.com", selectors={"title": [(By.TAG_NAME, "title", lambda elem: elem.text)]})
        >>> print(helper.get_items())
        {'title': ['Google']}
        >>> helper.destroy()
    """
    value_object: ChromeDriverValue = None
    download_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      '../download').replace(os.sep, '/')

    _driver = None
    __wait = None
    __source = None
    __start_window_handle = None
    root_path = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(root_path, r'driver\chromedriver.exe')
    # chrome_path = r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"'
    chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
    __options = ChromeOptions()
    __port = "9222"
    __chrome_add_argument = ['--blink-settings=imagesEnabled=false',  # 画像非表示
                             # '--incognito',  # シークレットモードで起動する
                             # '--headless',  # バックグラウンドで起動する
                             ]
    __chrome_add_experimental_option = [('debuggerAddress', f'127.0.0.1:{__port}'),
                                        # NOTE: prefsはdebuggerAddressと同時に指定できない？
                                        # ('prefs', {'download.default_directory': download_path}),
                                        ]
    profile_path = r'C:\Users\igapon\temp'
    __cmd = f'{chrome_path}' \
            f' --remote-debugging-port={__port}' \
            f' --user-data-dir="{profile_path}"'

    def __init__(self,
                 value_object: t.Union[ChromeDriverValue, str] = None,
                 selectors: dict = None,
                 download_path: str = download_path):
        """コンストラクタ

        値オブジェクトからの復元、または、urlとselectorsより、値オブジェクトを作成する

        Args:
            value_object (ChromeDriverValue | str | None): 対象となるサイトURL、または、値オブジェクト。デフォルトは None
            selectors (dict, optional): スクレイピングする際のセレクタリスト。デフォルトは None
            download_path (str, optional): ダウンロードフォルダのパス。デフォルトは download_path

        Raises:
            ValueError: value_object が ChromeDriverValue または str ではない場合、または selectors が不正な場合
        """
        self._window_handle_list = []
        self.__start()
        if download_path:
            self.download_path = download_path
        if value_object:
            if isinstance(value_object, ChromeDriverValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
            elif isinstance(value_object, str):
                url = value_object
                if selectors:
                    selectors = copy.deepcopy(selectors)
                    self.open_current_tab(url)
                    self.scraping(selectors)
                else:
                    raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                     f"引数エラー:selectorsが不正[{selectors}]")
            else:
                raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                 f"引数エラー:value_objectが不正[{value_object}]")

    @staticmethod
    def is_chrome_running_in_debug_mode() -> bool:
        """Chrome がデバッグモードで実行されているか確認する

        Returns:
            True: Chrome が起動し、9222 ポートに応答する場合. False: それ以外
        """
        chrome_running = False
        for proc in psutil.process_iter():
            try:
                if 'chrome.exe' in proc.name():
                    chrome_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not chrome_running:
            print("chrome見つからず。")
            return False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('127.0.0.1', int(ChromeDriver.__port)))
                return True
            except ConnectionRefusedError:
                print("chrome見つかるが、9222に応答せず。")
                return False

    @staticmethod
    def fixed_path(file_path: str) -> str:
        """フォルダ名の禁止文字を全角文字に置き換える

        Args:
            file_path: 置き換えたいフォルダパス

        Returns:
            置き換え後のフォルダパス
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
    def fixed_file_name(file_name: str) -> str:
        """ファイル名の禁止文字を全角文字に置き換える

        Args:
            file_name: 置き換えたいファイル名

        Returns:
            置き換え後のファイル名
        """
        file_name = file_name.replace(os.sep, '￥')
        file_name = file_name.replace('/', '／')
        return ChromeDriver.fixed_path(file_name)

    def scraping(self, selectors: dict[str, list[tuple[By, str, t.Callable[[WebElement], str]]]]) -> dict[str, list[str]]:
        """現在表示の URL に対してスクレイピングを実行する

        Args:
            selectors: スクレイピングする際のセレクタリスト
                      key: スクレイピング結果のキー
                      value: [(By, セレクタ, WebElementに対するアクション)...] のリスト

        Returns:
            スクレイピング結果の辞書
        """
        items = {}
        for key, selector_list in selectors.items():
            if key == "title":
                items[key] = [self._driver.title]
            else:
                items[key] = self.__get_scraping_selector_list(selector_list)
        self.value_object = ChromeDriverValue(self._driver.current_url, selectors, items)
        return items

    def scroll_element(self, element: WebElement) -> None:
        """指定された要素までスクロールする

        Args:
            element: スクロール先の要素
        """
        actions = ActionChains(self._driver)
        actions.move_to_element(element)
        actions.perform()

    def get_value_object(self) -> ChromeDriverValue:
        """値オブジェクトを取得する

        Returns:
            値オブジェクト

        Raises:
            ValueError: value_object が存在しない場合
        """
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:value_object")

    def get_url(self) -> str:
        """URL を取得する

        Returns:
            URL

        Raises:
            ValueError: URL が存在しない場合
        """
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().url)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:url")

    def get_selectors(self) -> dict[str, list[tuple[By, str, t.Callable[[WebElement], str]]]]:
        """セレクタを取得する

        Returns:
             セレクタ

        Raises:
            ValueError: セレクタが存在しない場合
        """
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().selectors)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:selectors")

    def get_items(self) -> dict[str, list[str]]:
        """スクレイピング結果を取得する

        Returns:
            スクレイピング結果

        Raises:
            ValueError: スクレイピング結果が存在しない場合
        """
        if self.get_value_object():
            return copy.deepcopy(self.get_value_object().items)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:items")

    def __add_options(self, *args: tuple[str, Any]) -> None:
        """Chrome オプションを追加する

        Args:
            *args: 追加するオプションのタプル
        """
        self.__options.add_experimental_option(*args)

    def __add_argument(self, args: str) -> None:
        """Chrome 引数を追加する

        Args:
            args: 追加する引数
        """
        self.__options.add_argument(args)

    def __start(self) -> None:
        """Chromeへの接続を完了する。起動していなければ起動する。既に開いているtabは、とりあえず気にしない"""
        # TODO: __add_argumentが効いてない、使い方を調べる
        #        for arg in self.__chrome_add_argument:
        #            self.__add_argument(arg)
        for args in self.__chrome_add_experimental_option:
            print(*args)
            self.__add_options(*args)
        if not self.is_chrome_running_in_debug_mode():
            print("Chromeに繋がらなかったので、起動して接続する。")
            self.__create()
        try:
            # NOTE: タイムアウト長いので、なるべくChrome起動してから呼び出したい
            self.__connection()
        except Exception as e:
            print(e, "Chromeに繋がらなかったので、起動して接続する。")
            self.__create()
            self.__connection()
        self.__start_window_handle = self._driver.current_window_handle

    def __connection(self) -> None:
        """起動しているchromeに接続"""
        chrome_service = Service(executable_path=ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=chrome_service, options=self.__options)
        # self._driver = Chrome(executable_path=ChromeDriverManager().install(), options=self.__options)

    def __create(self) -> None:
        """chromeを起動する"""
        subprocess.Popen(self.__cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def destroy(self) -> None:
        """chromeが開いていれば閉じる"""
        if self._driver is not None:
            for __window_handle in self._window_handle_list:
                self.close(__window_handle)
            if self.__start_window_handle : # None でない場合のみclose()を呼ぶ
                self._driver.switch_to.window(self.__start_window_handle)
                self._driver.close()
                self.__start_window_handle = None
            self._driver.quit()
            self._driver = None

    def __gen_scraping_selectors(self, selectors: dict) -> t.Generator[list[str], None, None]:
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返すジェネレータ

        Args:
            selectors (dict): {key, list[tuple(by, selector, action)]}] スクレイピングの規則

        Yields:
            list[str]: スクレイピング結果をlistに入れて返す

        Raises:
            ValueError: URLが不正な場合
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
                            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                             f"引数エラー:urlが不正[{url}]")
                else:
                    for _ in self._window_handle_list:
                        self.close()
                    yield ret_list

    def __get_scraping_selector_list(self, selector_list: list) -> list:
        """(画面依存)chromeで開いているサイトに対して、スクレイピング結果を返す

        Args:
            selector_list: list[tuple(by, selector, action)]: スクレイピングの規則

        Returns:
            list[str]: スクレイピング結果をlistに入れて返す

        Raises:
          ValueError: URLが不正な場合
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
                        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                         f"引数エラー:urlが不正[{url}]")
            else:
                for _ in self._window_handle_list:
                    self.close()
                return ret_list

    def __get_scraping_selector(self, by: By, selector: str, action: t.Callable[[WebElement], str]) -> t.List[str]:
        """(画面遷移有)現在の画面について、スクレイピングして、結果を返す

        Args:
            by: セレクタの種類 (e.g., By.ID, By.XPATH)
            selector: セレクタ文字列
            action: WebElementに対して実行する関数 (e.g., lambda elem: elem.text)

        Returns:
            スクレイピング結果のリスト

        Raises:
            NoSuchElementException: 指定されたセレクタを持つ要素が見つからない場合
            その他の例外: actionの実行中に例外が発生した場合
        """
        try:
            ret_list = []
            __temp_window_handle_list = copy.deepcopy(self._window_handle_list)
            if __temp_window_handle_list:
                count = len(__temp_window_handle_list)
            else:
                count = 1
            for _ in range(count):
                elements = self._driver.find_elements(by=by, value=selector)
                for elem in elements:
                    try:
                        self.scroll_element(elem)
                        text = action(elem)
                        ret_list.append(text)
                    except Exception as inner_e:
                        print(f"Element process error: {inner_e}")
                if count != 1:
                    self.close()
            return ret_list
        except NoSuchElementException as e:
            # find_elementsでelementが見つからなかったとき
            print(f"NoSuchElementException: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

    def get_source(self) -> str:
        """(画面依存)現在の画面(chromeで現在表示しているタブ)のソースコードを取得する

        Returns:
            str: ソースコード
        """
        self.__source = self._driver.page_source
        return copy.deepcopy(self.__source)

    def save_source(self, path: str = './title.html') -> None:
        """(画面依存)現在の画面のソースコードをファイルに保存する

        Args:
            path (str, optional): 保存するファイルパス(URLかタイトルを指定するとよさそう)。 デフォルトは './title.html'
        """
        html = self.get_source()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def back(self) -> None:
        """(画面遷移有)ブラウザの戻るボタン押下と同じ動作"""
        self._driver.back()

    def forward(self) -> None:
        """(画面遷移有)ブラウザの進むボタン押下と同じ動作"""
        self._driver.forward()

    def next_tab(self) -> None:
        """(画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ後のタブを表示する"""
        self.__shift_tab(1)

    def previous_tab(self) -> None:
        """(画面遷移有)openで作ったタブ(__window_handle_list)の内、一つ前のタブを表示する"""
        self.__shift_tab(-1)

    def __shift_tab(self, step: int) -> None:
        """(画面遷移有)openで作ったタブ(__window_handle_list)の内、指定されたステップ数だけタブを切り替える

        Args:
          step (int): 切り替えるタブのステップ数。正の値は次へ、負の値は前へ
        """
        if not self._window_handle_list:
            self._driver.switch_to.window(self.__start_window_handle)
            return
        # switch_to.window の呼び出し履歴から、現在のウィンドウハンドルを特定する
        if self._driver.switch_to.window.call_args_list:
            current_handle = self._driver.switch_to.window.call_args_list[-1].args[0]
        else:  # まだ一度も switch_to.window が呼ばれていない場合は、最初のハンドルを設定する
          current_handle = self._window_handle_list[0]
        index = self._window_handle_list.index(current_handle)
        next_index = (index + step) % len(self._window_handle_list)
        next_handle = self._window_handle_list[next_index]
        self._driver.switch_to.window(next_handle)

    def download_image(self, url: str, download_image_path: str = None) -> None:
        """(画面遷移有)urlの画像を保存する(open_new_tab → save_image → closeする)

        Args:
            url (str): 画像のurl
            download_image_path (str, optional): ダウンロード先のパス。指定しない場合は、インスタンスの download_image_path を使用する
        """
        uri = helper.uri.Uri(url)
        if uri.is_data_uri(url):
            uri.save_data_uri(download_image_path)
        else:
            __handle = self.open_new_tab(url)
            self.save_image(uri.get_filename(), uri.get_ext())
            self.close(__handle)

    def open_current_tab(self, url: str) -> None:
        """(画面依存)現在表示されているタブでurlを開く

        Args:
            url (str): chromeで開くURL
        """
        self._driver.get(url)
        # ページが読み込まれるまで待機
        self.__wait = WebDriverWait(self._driver, 30)
        self.__wait.until(EC.presence_of_all_elements_located)

    def open_new_tab(self, url: str) -> str:
        """(画面遷移有)新しいタブでurlを開く

        Args:
            url (str): 開くURL

        Returns:
            str: 開いたタブのハンドル

        Raises:
            Exception: 新しいタブを開けなかった場合
        """
        self._driver.switch_to.new_window()
        self.open_current_tab(url)
        self._window_handle_list.append(self._driver.current_window_handle)
        return self._window_handle_list[-1]

    def open_new_tabs(self, url_list: list) -> list:
        """(画面遷移有)新しいタブでurlリストを開く

        Args:
            url_list (list[str]): 開くURLのリスト

        Returns:
            list[str]: 開いたタブのハンドルリスト
        """
        window_handle_list = []
        for url in url_list:
            window_handle_list.append(self.open_new_tab(url))
        return window_handle_list

    def close(self, window_handle=None):
        """openで開いた画面の内、指定の画面か、現在の画面を閉じる

        Args:
            window_handle: 閉じる画面のハンドル

        Raises:
            ValueError: 指定のwindow_handleがリストに存在しない場合
        """
        try:
            if not window_handle:
                window_handle = self._driver.current_window_handle
            if window_handle == self.__start_window_handle:
                raise ValueError("開始時のタブは閉じられません。")
            if window_handle not in self._window_handle_list:
                raise ValueError(f"指定されたウィンドウハンドル '{window_handle}' が存在しません。")
            index = self._window_handle_list.index(window_handle)
            self._driver.close()
            del self._window_handle_list[index]
            if len(self._window_handle_list) == 0:
                self._driver.switch_to.window(self.__start_window_handle)
            else:
                if index:
                    index -= 1
                self._driver.switch_to.window(self._window_handle_list[index])
        except ValueError as e:
            print(f"ValueError: {e}")
            raise

    def save_image(self, download_file_name, download_ext='.jpg', wait_time=10):
        """表示されている画像を保存する

        chromeのデフォルトダウンロードフォルダに保存された後に、指定のフォルダに移動する
        ダウンロード実行用スクリプトを生成＆実行する

        Args:
            download_file_name: ダウンロードするファイル名
            download_ext: ダウンロードするファイルの拡張子。デフォルトは '.jpg'
            wait_time: ファイルのダウンロード完了を待つ時間（秒）。デフォルトは 3 秒

        Raises:
            TimeoutError: wait_time秒以内にダウンロードが完了しなかった場合
        """
        __image_url = self._driver.current_url
        downloads_path = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "downloads")
        __web_file = helper.webFile.WebFile(__image_url, download_file_name, download_ext, downloads_path)
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
        self._driver.execute_script(script_str)
        file_path_to = os.path.join(self.download_path, __filename)
        file_path_from = __web_file.get_path()
        what = lambda: __web_file.move(file_path_to)
        how = lambda: os.path.isfile(file_path_from)
        self.wait_until(what, how, wait_time)

    @staticmethod
    def wait_until(what: t.Callable, how: t.Callable, wait_time: int = 3) -> t.Any:
        """指定の条件が満たされるまで待機する

        Args:
            what: 実行する関数
            how: 条件を判定する関数。Trueを返せば待機終了
            wait_time: 最大待機時間（秒）

        Returns:
            what関数の戻り値

        Raises:
            TimeoutError: wait_time秒以内に条件が満たされなかった場合
        """
        start = time.time()
        while (time.time() - start) < wait_time:
            if how():
                return what()
            time.sleep(0.1)
        raise TimeoutError(f"{wait_time}秒以内に条件が満たされませんでした。")
