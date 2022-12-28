#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * ChromeDriverHelperを使って、指定サイト(site_url)をセレクタ(site_selectors)でクローリングする
    * 指定サイトのクローリング結果を、crawling_file_pathに保持する
    * crawling_file_pathのpage_urlsに対して、スクレイピングして末尾画像URLの展開URLでダウンロードして、zipに保存する
"""
import subprocess
import json
from chromeDriverHelper import *
from webFileListHelper import *
from downloading import *


@dataclass(frozen=True)
class CrawlingValue:
    """値オブジェクト"""
    site_url: str = None
    site_selectors: dict = None
    crawling_items: dict = None
    crawling_file_path: str = './crawling_list.txt'

    def __init__(self, site_url, site_selectors, crawling_items, crawling_file_path=crawling_file_path):
        """完全コンストラクタパターン"""
        if not site_url:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:site_url=None")
        if not site_selectors:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:site_selectors=None")
        if crawling_items is None:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:crawling_items=None")
        if not crawling_file_path:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:crawling_file_path=None")
        if not isinstance(site_url, str):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:site_urlがstrではない")
        if not isinstance(site_selectors, dict):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:site_selectorsがdictではない")
        if not isinstance(crawling_items, dict):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:crawling_itemsがdictではない")
        if not isinstance(crawling_file_path, str):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:crawling_file_pathがstrではない")
        object.__setattr__(self, "site_url", site_url)
        object.__setattr__(self, "site_selectors", site_selectors)
        object.__setattr__(self, "crawling_items", crawling_items)
        object.__setattr__(self, "crawling_file_path", crawling_file_path)


class Crawling:
    """クローリング"""
    value_object: CrawlingValue = None
    site_selectors: dict = None
    crawling_file_path: str = CrawlingValue.crawling_file_path

    def __init__(self, value_object=None, site_selectors=None, crawling_file_path=crawling_file_path):
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
                    crawling_items = self.scraping(site_url, site_selectors)
                    self.value_object = CrawlingValue(site_url,
                                                      site_selectors,
                                                      crawling_items,
                                                      crawling_file_path)
                    self.load_text()
                    self.save_text()
                else:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:site_selectors=None")
            else:
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:value_object=None")

    @staticmethod
    def scraping(url, selectors):
        """ChromeDriverHelperを使ってスクレイピングする"""
        selectors = copy.deepcopy(selectors)
        chrome_driver = ChromeDriverHelper(url, selectors)
        return chrome_driver.get_items()

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
        return ChromeDriverHelper.fixed_file_name(title)

    def get_value_object(self):
        """値オブジェクトを取得する"""
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:value_object")

    def get_site_url(self):
        """値オブジェクトのプロパティsite_url取得"""
        if self.get_value_object().site_url:
            return copy.deepcopy(self.get_value_object().site_url)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:site_url")

    def get_site_selectors(self):
        """値オブジェクトのプロパティsite_selectors取得"""
        if self.get_value_object().site_selectors:
            return copy.deepcopy(self.get_value_object().site_selectors)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:site_selectors")

    def get_crawling_items(self):
        """値オブジェクトのプロパティcrawling_items取得"""
        if self.get_value_object().crawling_items:
            return copy.deepcopy(self.get_value_object().crawling_items)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:crawling_items")

    def get_crawling_file_path(self):
        """値オブジェクトのプロパティcrawling_file_path取得"""
        if self.get_value_object().crawling_file_path:
            return copy.deepcopy(self.get_value_object().crawling_file_path)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:crawling_file_path")

    def create_save_text(self):
        """保存用文字列の作成
        :return: str 保存用文字列の作成
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
        """データをファイルに、以下の独自フォーマットで保存する
            * サイトURL
            * セレクタ
            * saveファイルのフルパス
            * クローリング結果urls
        :return: bool 成功/失敗=True/False
        """
        with open(self.get_crawling_file_path(), 'w', encoding='utf-8') as __work_file:
            __buff = self.create_save_text()
            __work_file.write(__buff)
        return True

    def load_text(self):
        """独自フォーマットなファイルからデータを読み込み、value_objectを更新する
        TODO: site_urlやselectorsが変わったらどうする？
        :return: bool 成功/失敗=True/False
        """
        __site_url2 = self.get_site_url()
        __selectors2 = self.get_site_selectors()
        __crawling_file_path2 = self.get_crawling_file_path()
        __crawling_items2 = self.get_crawling_items()
        if not os.path.exists(__crawling_file_path2):
            return False
        with open(__crawling_file_path2, 'r', encoding='utf-8') as __work_file:
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
            if __crawling_items2:
                # TODO: タイトルとか、前回と値が違うと、マージで増殖するかも
                __crawling_items = self.dict_merge(__crawling_items, __crawling_items2)
            self.value_object = CrawlingValue(__site_url2, __selectors2, __crawling_items, __crawling_file_path2)
            return True

    def is_url_included_exclusion_list(self, url):
        """除外リストに含まれるURLならTrueを返す
        :param url:
        :return:
        """
        crawling_items = self.get_crawling_items()
        if 'exclusion_urls' in crawling_items:
            if url in crawling_items['exclusion_urls']:
                return True
        return False

    def move_url_from_page_urls_to_exclusion_urls(self, url):
        """ターゲットリスト(page_urls)から除外リスト(exclusion_urls)にURLを移動する
        :param url:
        :return:
        """
        site_url = self.get_site_url()
        selectors = self.get_site_selectors()
        crawling_file_path = self.get_crawling_file_path()
        crawling_items = self.get_crawling_items()
        if 'exclusion_urls' in crawling_items:
            if url not in crawling_items['exclusion_urls']:
                crawling_items['exclusion_urls'].append(url)
        else:
            crawling_items['exclusion_urls'] = [url]
        if 'page_urls' in crawling_items:
            if url in crawling_items['page_urls']:
                crawling_items['page_urls'].remove(url)
        self.value_object = CrawlingValue(site_url, selectors, crawling_items, crawling_file_path)

    def crawling_url_deployment(self, page_selectors, image_selectors):
        """各ページをスクレイピングして、末尾画像のナンバーから、URLを予測して、画像ファイルをダウンロード＆圧縮する
            # crawling_itemsに、page_urlsがあり、各page_urlをpage_selectorsでスクレイピングする
            # タイトルとURLでダウンロード除外または済みかをチェックして、
            # ダウンロードしない場合は、以降の処理をスキップする
            # 各page_urlをimage_selectorsでスクレイピングしてダウンロードする画像URLリストを作る。
            # 画像URLリストをirvineHelperでダウンロードして、zipファイルにする
        :param page_selectors:
        :param image_selectors:
        :return:
        """
        crawling_items = self.get_crawling_items()
        page_urls = []
        if 'page_urls' in crawling_items:
            page_urls = crawling_items['page_urls']
        for page_url in page_urls:
            print(page_url)
            if self.is_url_included_exclusion_list(page_url):
                self.move_url_from_page_urls_to_exclusion_urls(page_url)
                self.save_text()
                continue
            items = self.scraping(page_url, page_selectors)
            languages = self.take_out(items, 'languages')
            title = Crawling.validate_title(items, 'title_jp', 'title_en')
            url_title = ChromeDriverHelper.fixed_file_name(page_url)

            # フォルダがなかったらフォルダを作る
            os.makedirs(WebFileListHelper.work_path, exist_ok=True)
            target_file_name = os.path.join(WebFileListHelper.work_path, f'{title}：{url_title}.html')
            print(title, languages)
            if languages and languages == 'japanese' and not os.path.exists(target_file_name):
                image_items = self.scraping(page_url, image_selectors)
                image_urls = self.take_out(image_items, 'image_urls')
                last_image_url = self.take_out(image_items, 'image_url')
                if not last_image_url:
                    raise ValueError(f"エラー:last_image_urlが不正[{last_image_url}]")
                print(last_image_url, image_urls)
                web_file_list = WebFileListHelper([last_image_url])
                # 末尾画像のナンバーから全ての画像URLを推測して展開する
                web_file_list.update_value_object_by_deployment_url_list()
                url_list = web_file_list.get_url_list()
                print(url_list)

                web_file_list.download_irvine()
                for count in enumerate(WebFileHelper.ext_list):
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
                ChromeDriverHelper().save_source(target_file_name)
            # page_urlsからexclusion_urlsにURLを移して保存する
            self.move_url_from_page_urls_to_exclusion_urls(page_url)
            self.save_text()


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    load_path = './downloadlist.txt'
    with open(load_path, 'r', encoding='utf-8') as work_file:
        buff = work_file.readlines()
        for line in buff:
            target_url = line.rstrip('\n')
            # subprocess.run(['python', 'imgdl.py', target_url])
            # 画像が連番の場合、selenium
            subprocess.run(['python', 'urlDeployment.py', target_url])
