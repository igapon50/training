#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クローリング
    * 指定サイト(site_url)をセレクタ(site_selectors)でクローリングする(ChromeDriverを使用)
    * クローリング結果を、crawling_file_pathに保存する
    * crawling_file_pathのpage_urlsは、スクレイピングする対象urlリストである
    * crawling_file_pathのexclusion_urlsは、スクレイピングの除外urlリストである
    * zip保存まで終わると、page_urlsからexclusion_urlsにurlを移す
    * セレクタを、image_urlで定義すると、crawling_url_deploymentでスクレイピングして末尾画像URLの展開URLでダウンロードして、zipに保存する
    * セレクタを、image_urlsで定義すると、crawling_urlsでスクレイピングしてダウンロードして、zipに保存する
"""
import os
import sys
import copy
import inspect
import json
import datetime
import time
from dataclasses import dataclass
from typing import Union, Optional
import helper.chromeDriver
import helper.webFile
import helper.webFileList
import helper.line_message_api
import helper.slack_message_api
import helper.status


@dataclass(frozen=True)
class CrawlingValue:
    """Crawlingの値オブジェクトクラス

    Attributes:
        site_url (str): サイトURL
        site_selectors (Dict[str, str]): サイトセレクタ。キーはアイテム名、値はCSSセレクタ
        crawling_items (Dict[str, List[str]]): クローリングアイテム。キーはアイテムの種類（例：'page_urls'）、値はURLのリスト
        crawling_file_path (str): クローリングファイルパス

    Raises:
        ValueError: 各属性が不正な値（None、空文字列、不正な型）の場合
    """
    site_url: str = None
    site_selectors: dict = None
    crawling_items: dict = None
    crawling_file_path: str = None

    def __init__(self, site_url, site_selectors, crawling_items, crawling_file_path):
        """完全コンストラクタパターン"""
        if not site_url:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_url=None")
        if not site_selectors:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_selectors=None")
        if crawling_items is None:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_items=None")
        if not crawling_file_path:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_file_path=None")
        if not isinstance(site_url, str):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_urlがstrではない")
        if not isinstance(site_selectors, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:site_selectorsがdictではない")
        if not isinstance(crawling_items, dict):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_itemsがdictではない")
        if not isinstance(crawling_file_path, str):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:crawling_file_pathがstrではない")
        object.__setattr__(self, "site_url", site_url)
        object.__setattr__(self, "site_selectors", site_selectors)
        object.__setattr__(self, "crawling_items", crawling_items)
        object.__setattr__(self, "crawling_file_path", crawling_file_path)


class Crawling:
    """クローリングクラス

    指定されたサイトをクローリングし、結果をファイルに保存します
    """
    URLS_TARGET = "page_urls"
    URLS_EXCLUSION = "exclusion_urls"
    URLS_FAILURE = "failure_urls"
    value_object: CrawlingValue = None
    site_selectors: dict = None
    crawling_items: dict = {URLS_TARGET: [], URLS_EXCLUSION: [], URLS_FAILURE: []}
    crawling_file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           '../crawling_list.txt').replace(os.sep, '/')

    def __init__(self,
                 value_object=None,
                 site_selectors=None,
                 crawling_items=None,
                 crawling_file_path=crawling_file_path):
        if value_object:
            if isinstance(value_object, CrawlingValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
                self.load_text()
                self.save_text()
            elif isinstance(value_object, str):
                if site_selectors:
                    site_selectors = copy.deepcopy(site_selectors)
                    site_url = value_object
                    if crawling_items is None:
                        crawling_items = Crawling.crawling_items
                    self.value_object = CrawlingValue(site_url,
                                                      site_selectors,
                                                      crawling_items,
                                                      crawling_file_path)
                    self.load_text()
                    self.save_text()
                else:
                    raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                     f"引数エラー:site_selectors=None")
            elif isinstance(value_object, dict):
                site_selectors = copy.deepcopy(value_object)
                self.load_text(site_selectors, crawling_file_path)
                self.save_text()
            else:
                raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                                 f"引数エラー:value_objectが無効な型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:value_object=None")

    @staticmethod
    def scraping(url, selectors):
        """ChromeDriverを使ってスクレイピングする"""
        selectors = copy.deepcopy(selectors)
        # インスタンス化。これだけではページは開かれない（あるいは空のタブ）
        chrome_driver = helper.chromeDriver.ChromeDriver()

        try:
            # 0. まず対象のURLを開く
            chrome_driver.open_current_tab(url)

            # 1. ロボットチェックが出ていないか確認
            if 'bot_check' in selectors:
                for by, path, func in selectors['bot_check']:
                    # chrome_driver._driver を直接参照して要素を探す
                    elements = chrome_driver._driver.find_elements(by, path)
                    if len(elements) > 0:
                        # ロボットチェック検知。例外を投げて failure_urls に回す
                        raise ValueError(f"Bot detection (last_image_urlが不正): {url}")

            # 2. スクレイピングを実行（ここで内部の value_object が生成される）
            items = chrome_driver.scraping(selectors)

            # 3. Cloudflare 等の「タイトルがドメイン名だけ」のケースを失敗扱いにする
            title_jp = Crawling.take_out(items, 'title_jp')
            if title_jp == "nhentai.net":
                raise ValueError(f"Cloudflare blocking (last_image_urlが不正): {url}")
            return items
        except Exception as e:
            # エラーが発生した場合は例外を再送して上位の failure_urls 処理に任せる
            raise e

    @staticmethod
    def dict_merge(dict1, dict2):
        """dict2をdict1にマージする。dictは値がlistであること。list内の重複は削除。list内の順序を維持"""
        dict1 = copy.deepcopy(dict1)
        dict2 = copy.deepcopy(dict2)
        for key, value in dict2.items():
            if key in dict1:
                dict1[key].extend(value)
                dict1[key] = list(dict.fromkeys(dict1[key]))
            else:
                dict1[key] = value
        return dict1

    @staticmethod
    def take_out(items, item_name):
        """crawling_itemsから指定のitemを取り出す"""
        ret_value = None
        if item_name in items:
            ret_value = copy.deepcopy(items[item_name])
        if ret_value and isinstance(ret_value, list):
            if len(ret_value) == 1:
                # listの中身が一つしかない時
                ret_value = ret_value[0]
        return ret_value

    @staticmethod
    def validate_title(items: dict, title: str, title_sub: str):
        title = Crawling.take_out(items, title)
        title_sub = Crawling.take_out(items, title_sub)
        if not title:
            if not title_sub:
                # タイトルが得られない時は、タイトルを日時文字列にする
                now = datetime.datetime.now()
                title = f'{now:%Y%m%d_%H%M%S}'
            else:
                title = title_sub
        return helper.chromeDriver.ChromeDriver.fixed_file_name(title)

    @staticmethod
    def download_chrome_driver(web_file_list):
        """selenium chromeDriverを用いて、画像をデフォルトダウンロードフォルダにダウンロードして、指定のフォルダに移動する
        """
        chromedriver = helper.chromeDriver.ChromeDriver()
        for url, path in zip(web_file_list.get_url_list(), web_file_list.get_path_list()):
            chromedriver.download_image(url, path)

    def get_value_object(self):
        """値オブジェクトを取得する"""
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:value_object")

    def get_site_url(self):
        """値オブジェクトのプロパティsite_url取得"""
        if self.get_value_object().site_url:
            return copy.deepcopy(self.get_value_object().site_url)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:site_url")

    def get_site_selectors(self):
        """値オブジェクトのプロパティsite_selectors取得"""
        if self.get_value_object().site_selectors:
            return copy.deepcopy(self.get_value_object().site_selectors)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:site_selectors")

    def get_crawling_items(self):
        """値オブジェクトのプロパティcrawling_items取得"""
        if self.get_value_object().crawling_items:
            return copy.deepcopy(self.get_value_object().crawling_items)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:crawling_items")

    def get_crawling_file_path(self):
        """値オブジェクトのプロパティcrawling_file_path取得"""
        if self.get_value_object().crawling_file_path:
            return copy.deepcopy(self.get_value_object().crawling_file_path)
        raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                         f"オブジェクトエラー:crawling_file_path")

    def create_save_text(self):
        """保存用文字列の作成

        以下を保存する
            * サイトURL
            * セレクタ
            * saveファイルのフルパス
            * クローリング結果urls

        Returns:
            str: 保存用文字列の作成
        """
        __buff = json.dumps(self.get_site_url(), ensure_ascii=False) + '\n'  # サイトURL
        # TODO: selectorsはjson.dumpsでシリアライズできないオブジェクトたぶんlambdaを含んでいる。pickleでもだめらしい。
        #  代替方法dillとか https://github.com/uqfoundation/dill
        #  marshalとか検討する
        # __buff += json.dumps(self.value_object.site_selectors, ensure_ascii=False) + '\n'  # セレクタ
        if self.get_value_object().crawling_file_path:
            __buff += json.dumps(self.get_crawling_file_path(), ensure_ascii=False) + '\n'  # クローリング結果保存パス
        else:
            __buff += '\n'  # クローリング結果パス追加
        __buff += json.dumps(self.get_crawling_items(), ensure_ascii=False) + '\n'  # クローリング結果
        return __buff

    def save_text(self):
        """クローリング情報をファイルに、保存する

        Returns:
            bool: 成功/失敗=True/False
        """
        with open(self.get_crawling_file_path(), 'w', encoding='utf-8') as __work_file:
            __buff = self.create_save_text()
            __work_file.write(__buff)
        return True

    def load_text(self, selectors=None, crawling_file_path=crawling_file_path):
        """独自フォーマットなファイルからデータを読み込み、value_objectを作り直す

        Args:
            selectors (dict, optional): スクレイピングする際のセレクタリスト。デフォルトは None
            crawling_file_path (str, optional): ダウンロードフォルダのパス。デフォルトは crawling_file_path

        Returns:
            bool: 成功、True。ファイルがなかったり、ファイルが空だったら、False
        """
        if not os.path.exists(crawling_file_path):
            return False
        if os.stat(crawling_file_path).st_size == 0:
            return False
        try:
            with open(crawling_file_path, 'r', encoding='utf-8') as __work_file:
                __buff = __work_file.readlines()
                __site_url = json.loads(__buff[0].rstrip('\n'))
                # TODO: site_selectors
                # del __buff[0]
                # __selectors = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __crawling_file_path = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __crawling_items = json.loads(__buff[0].rstrip('\n'))
                del __buff[0]
                __selectors = selectors
                __crawling_items2 = None
                if self.value_object:
                    __site_url = self.get_site_url()
                    __selectors = self.get_site_selectors()
                    __crawling_items2 = self.get_crawling_items()
                if __crawling_items2:
                    __crawling_items = self.dict_merge(__crawling_items, __crawling_items2)
                __crawling_file_path = crawling_file_path
                self.value_object = CrawlingValue(__site_url, __selectors, __crawling_items, __crawling_file_path)
        except Exception as e:
            now = datetime.datetime.now().strftime('%Y%m%d%H%M')
            file_name, ext = os.path.splitext(crawling_file_path)
            backup_file_path = f"{file_name}_{now}{ext}"
            os.rename(crawling_file_path, backup_file_path)
            print(f"ファイルの読み込みに失敗しました。バックアップを作成しました: {backup_file_path}")
            print(f"エラー内容: {e}")
            return False
        return True

    def is_url_included_exclusion_list(self, url):
        """除外リストに含まれるURLならTrueを返す
        """
        crawling_items = self.get_crawling_items()
        if self.URLS_EXCLUSION in crawling_items:
            if url in crawling_items[self.URLS_EXCLUSION]:
                return True
        return False

    def move_url_from_page_urls_to_exclusion_urls(self, url):
        """ターゲットリスト(page_urls)から除外リスト(exclusion_urls)にURLを移動する
        """
        site_url = self.get_site_url()
        selectors = self.get_site_selectors()
        crawling_file_path = self.get_crawling_file_path()
        crawling_items = self.get_crawling_items()
        if self.URLS_EXCLUSION in crawling_items:
            if url not in crawling_items[self.URLS_EXCLUSION]:
                crawling_items[self.URLS_EXCLUSION].append(url)
        else:
            crawling_items[self.URLS_EXCLUSION] = [url]
        if self.URLS_TARGET in crawling_items:
            if url in crawling_items[self.URLS_TARGET]:
                crawling_items[self.URLS_TARGET].remove(url)
        self.value_object = CrawlingValue(site_url, selectors, crawling_items, crawling_file_path)
        self.save_text()

    def is_url_included_failure_list(self, url):
        """失敗リストに含まれるURLならTrueを返す
        """
        crawling_items = self.get_crawling_items()
        if self.URLS_FAILURE in crawling_items:
            if url in crawling_items[self.URLS_FAILURE]:
                return True
        return False

    def move_url_from_page_urls_to_failure_urls(self, url):
        """ターゲットリスト(page_urls)から失敗リスト(failure_urls)にURLを移動する
        """
        site_url = self.get_site_url()
        selectors = self.get_site_selectors()
        crawling_file_path = self.get_crawling_file_path()
        crawling_items = self.get_crawling_items()
        if self.URLS_FAILURE in crawling_items:
            if url not in crawling_items[self.URLS_FAILURE]:
                crawling_items[self.URLS_FAILURE].append(url)
        else:
            crawling_items[self.URLS_FAILURE] = [url]
        if self.URLS_TARGET in crawling_items:
            if url in crawling_items[self.URLS_TARGET]:
                crawling_items[self.URLS_TARGET].remove(url)
        self.value_object = CrawlingValue(site_url, selectors, crawling_items, crawling_file_path)
        self.save_text()

    def marge_crawling_items(self):
        """crawling_itemsのpage_urlsにexclusion_urlsがあったら削除する"""
        crawling_items = self.get_crawling_items()
        page_urls = []
        if self.URLS_TARGET in crawling_items:
            page_urls = crawling_items[self.URLS_TARGET]
        for page_url in page_urls:
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            if self.is_url_included_failure_list(page_url):
                self.move_url_from_page_urls_to_failure_urls(page_url)
                continue

    def crawling_url_deployment(self, page_selectors, image_selectors, notification_id=""):
        """各ページをスクレイピングして、末尾画像のナンバーから、URLを予測して、画像ファイルをダウンロード＆圧縮する
            # crawling_itemsに、page_urlsがあり、各page_urlをpage_selectorsでスクレイピングする
            # タイトルとURLでダウンロード除外または済みかをチェックして、
            # ダウンロードしない場合は、以降の処理をスキップする
            # 各page_urlをimage_selectorsでスクレイピングしてダウンロードする画像URLリストを作る。
            # 画像URLリストをirvineHelperでダウンロードして、zipファイルにする
        """
        crawling_items = self.get_crawling_items()
        page_urls = []
        if self.URLS_TARGET in crawling_items:
            page_urls = crawling_items[self.URLS_TARGET]
        total_pages = len(page_urls)
        max_retries = 3  # 最大リトライ回数
        retry_delay = 10 # リトライ間の待機時間（秒）
        for i, page_url in enumerate(page_urls):
            status = helper.status.Status()
            if status is not None and not status.is_running():
                print("stop status")
                break
            current_page = i + 1
            remaining_pages = total_pages - current_page
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            if self.is_url_included_failure_list(page_url):
                self.move_url_from_page_urls_to_failure_urls(page_url)
                continue
            for attempt in range(max_retries):
                try:
                    items = self.scraping(page_url, page_selectors)
                    languages = self.take_out(items, 'languages')
                    title = Crawling.validate_title(items, 'title_jp', 'title_en')
                    # ロボットチェック等でタイトルが取得できていない、あるいは言語が空の場合
                    if not languages:
                        raise ValueError(f"データ取得失敗（言語情報なし）: {page_url}")
                    url_title = helper.chromeDriver.ChromeDriver.fixed_file_name(page_url)
                    # フォルダがなかったらフォルダを作る
                    os.makedirs(helper.webFileList.WebFileList.work_path, exist_ok=True)
                    target_file_name = os.path.join(helper.webFileList.WebFileList.work_path, f'{title}：{url_title}.html')
                    print(f"タイトル: {title}, 言語: {languages}")
                    if languages and languages == 'japanese' and not os.path.exists(target_file_name):
                        # ダウンロードするときだけ通知する
                        # _line_message_api = LineMessageAPI(access_token="", channel_secret="")
                        # _line_message_api.send_message(
                        #     notification_id,
                        #     f'crawling :現在{current_page}ページ目 / 全{total_pages}ページ中 (残り{remaining_pages}ページ)')
                        _slack_message_api = helper.slack_message_api.SlackMessageAPI(access_token="")
                        _slack_message_api.send_message(
                            notification_id,
                            f'crawling :現在{current_page}ページ目 / 全{total_pages}ページ中 (残り{total_pages - current_page}ページ)')
                        image_items = self.scraping(page_url, image_selectors)
                        last_image_url = self.take_out(image_items, 'image_url')
                        if not last_image_url:
                            # リトライのために同じエラーを発生させる
                            raise ValueError(f"エラー:last_image_urlが不正[{last_image_url}]")
                        print(f"最終画像URLの取得成功: {last_image_url}")
                        web_file_list = helper.webFileList.WebFileList([last_image_url])
                        web_file_list.update_value_object_by_deployment_url_list()
                        web_file_list.download_irvine()
                        for count in enumerate(helper.webFile.WebFile.ext_list):
                            if web_file_list.is_exist():
                                break
                            web_file_list.rename_url_ext_shift()
                            web_file_list.download_irvine()
                        if not web_file_list.make_zip_file():
                            web_file_list.delete_local_files()
                            print("ZIPファイルの作成に失敗しました。")
                            self.move_url_from_page_urls_to_failure_urls(page_url)
                            # この continue は try-except の外側のループを継続する
                            # リトライせず次のURLへ進むため、breakで抜ける
                            break
                        web_file_list.rename_zip_file(title) or web_file_list.rename_zip_file(f'{title}：{url_title}')
                        web_file_list.delete_local_files()
                        helper.chromeDriver.ChromeDriver().save_source(target_file_name)
                        print("処理成功。除外リストに移動します。")
                        self.move_url_from_page_urls_to_exclusion_urls(page_url)
                    else:
                        print("ダウンロード対象外、または処理済みのためスキップします。")
                        self.move_url_from_page_urls_to_exclusion_urls(page_url)
                    # ここまで到達すれば成功なので、リトライのループを抜ける
                    break
                except ValueError as e:
                    # 指定したエラーメッセージの場合のみリトライ処理を行う
                    if "last_image_urlが不正" in str(e):
                        print(f"エラーが発生しました: {e}")
                        if attempt < max_retries - 1:
                            print(f"{retry_delay}秒後にリトライします... (試行 {attempt + 2}/{max_retries})")
                            time.sleep(retry_delay)
                        else:
                            print(f"最大リトライ回数({max_retries}回)に達しました。このURLの処理を失敗として記録します。")
                            self.move_url_from_page_urls_to_failure_urls(page_url)
                    else:
                        # 想定外のValueErrorの場合は、リトライせずにエラーを伝播させる
                        print(f"想定外のValueErrorです: {e}")
                        self.move_url_from_page_urls_to_failure_urls(page_url)
                        break # リトライせず次のURLへ
                except Exception as e:
                    print(f"予期せぬエラーが発生しました: {e}")
                    if attempt < max_retries - 1:
                        print(f"{retry_delay}秒後にリトライします... (試行 {attempt + 2}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        print(f"最大リトライ回数({max_retries}回)に達しました。このURLの処理を失敗として記録します。")
                        self.move_url_from_page_urls_to_failure_urls(page_url)

    def crawling_urls(self, page_selectors, image_selectors):
        """各ページをスクレイピングして、画像ファイルをダウンロード＆圧縮する
            # crawling_itemsに、page_urlsがあり、各page_urlをpage_selectorsでスクレイピングする
            # タイトルとURLでダウンロード除外または済みかをチェックして、
            # ダウンロードしない場合は、以降の処理をスキップする
            # 各page_urlをimage_selectorsでスクレイピングしてダウンロードする画像URLリストを作る。
            # 画像URLリストをirvineHelperでダウンロードして、zipファイルにする
        """
        crawling_items = self.get_crawling_items()
        page_urls = []
        if self.URLS_TARGET in crawling_items:
            page_urls = crawling_items[self.URLS_TARGET]
        for page_url in page_urls:
            status = helper.status.Status()
            if status is not None and not status.is_running():
                print("stop status")
                break
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                continue
            if self.is_url_included_failure_list(page_url):
                self.move_url_from_page_urls_to_failure_urls(page_url)
                continue
            items = self.scraping(page_url, page_selectors)
            title = Crawling.validate_title(items, 'title_jp', 'title_en')
            url_title = helper.chromeDriver.ChromeDriver.fixed_file_name(page_url)

            # フォルダがなかったらフォルダを作る
            os.makedirs(helper.webFileList.WebFileList.work_path, exist_ok=True)
            target_file_name = os.path.join(helper.webFileList.WebFileList.work_path, f'{title}：{url_title}.html')
            print(title)
            if not os.path.exists(target_file_name):
                image_items = self.scraping(page_url, image_selectors)
                image_urls = self.take_out(image_items, 'image_urls')
                print(image_urls)
                web_file_list = helper.webFileList.WebFileList(image_urls)
                web_file_list.download_irvine()
                for count in enumerate(helper.webFile.WebFile.ext_list):
                    if web_file_list.is_exist():
                        break
                    # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
                    web_file_list.rename_url_ext_shift()
                    web_file_list.download_irvine()
                if not web_file_list.make_zip_file():
                    sys.exit()
                if not web_file_list.rename_zip_file(title):
                    if not web_file_list.rename_zip_file(f'{title}：{url_title}'):
                        sys.exit()
                web_file_list.delete_local_files()
                # 成功したらチェック用ファイルを残す
                helper.chromeDriver.ChromeDriver().save_source(target_file_name)
            # page_urlsからexclusion_urlsにURLを移して保存する
            self.move_url_from_page_urls_to_exclusion_urls(page_url)
