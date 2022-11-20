#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * 指定サイト(site_url)をセレクタ(site_selectors)でクローリングする
    * クローリング結果を、ページリスト(crawling_file_pathのファイル)に登録する
    * ページリスト(get_site_urls_from_local)に登録されている、それぞれのページをスクレイピングする
    * スクレイピング結果を、ダウンロードリストに登録する
    * ダウンロードリストに登録されている、それぞれのファイルをダウンロードする
    * ダウンロードしたファイルを変名して圧縮する
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
                self.value_object = value_object
                self.load_text()
                self.save_text()
            elif isinstance(value_object, str):
                if site_selectors:
                    __site_url = value_object
                    __site_selectors = copy.deepcopy(site_selectors)
                    __crawling_file_path = crawling_file_path
                    __crawling_items = self.scraping(__site_url, __site_selectors)
                    self.value_object = CrawlingValue(__site_url,
                                                      __site_selectors,
                                                      __crawling_items,
                                                      __crawling_file_path)
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
        chrome_driver = ChromeDriverHelper(url, selectors)
        return chrome_driver.get_items()

    @staticmethod
    def dict_merge(dict1, dict2):
        """dict2をdict1にマージする。dictは値がlistであること。list内の重複は削除。list内の順序を維持"""
        for key, value in dict2.items():
            if key in dict1:
                dict1[key].extend(value)
                dict1[key] = list(dict.fromkeys(dict1[key]))
            else:
                dict1[key] = value
        return dict1

    def get_value_object(self):
        """値オブジェクトを取得する"""
        if self.value_object:
            return copy.deepcopy(self.value_object)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:value_object")

    def get_site_url(self):
        if self.get_value_object().site_url:
            return copy.deepcopy(self.get_value_object().site_url)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:site_url")

    def get_site_selectors(self):
        if self.get_value_object().site_selectors:
            return copy.deepcopy(self.get_value_object().site_selectors)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:site_selectors")

    def get_crawling_file_path(self):
        if self.get_value_object().crawling_file_path:
            return copy.deepcopy(self.get_value_object().crawling_file_path)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:crawling_file_path")

    def get_crawling_items(self):
        if self.get_value_object().crawling_items:
            return copy.deepcopy(self.get_value_object().crawling_items)
        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                         f"オブジェクトエラー:crawling_items")

    def get_site_urls_from_local(self):
        __site_urls = []
        with open(self.get_crawling_file_path(), 'r', encoding='utf-8') as __local_file:
            __site_urls = __local_file.readlines()
        return copy.deepcopy(__site_urls)

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
