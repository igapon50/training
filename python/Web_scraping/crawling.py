#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * 指定サイト(site_url)をセレクタ(selectors)でクローリングする
    * クローリング結果を、ページリスト(crawling_list.txt)に登録する
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
    selectors: dict = None
    crawling_file_path: str = './crawling_list.txt'
    crawling_urls: list = None

    def __init__(self, site_url, selectors, crawling_file_path=crawling_file_path, crawling_urls=None):
        """完全コンストラクタパターン"""
        if crawling_urls is None:
            crawling_urls = []
        if not site_url:
            raise ValueError(f"{self.__class__}引数エラー:site_url=None")
        if not selectors:
            raise ValueError(f"{self.__class__}引数エラー:selectors=None")
        if not crawling_file_path:
            raise ValueError(f"{self.__class__}引数エラー:crawling_file_path=None")
        if not isinstance(site_url, str):
            raise ValueError(f"{self.__class__}引数エラー:site_urlがstrではない")
        if not isinstance(selectors, dict):
            raise ValueError(f"{self.__class__}引数エラー:selectorsがdictではない")
        if not isinstance(crawling_file_path, str):
            raise ValueError(f"{self.__class__}引数エラー:crawling_file_pathがstrではない")
        object.__setattr__(self, "site_url", site_url)
        object.__setattr__(self, "selectors", selectors)
        object.__setattr__(self, "crawling_file_path", crawling_file_path)
        object.__setattr__(self, "crawling_urls", crawling_urls)


class Crawling:
    """クローリング"""
    value_object: CrawlingValue = None
    selectors: dict = None
    crawling_file_path: str = CrawlingValue.crawling_file_path

    def __init__(self, value_object=None, selectors=None, crawling_file_path=crawling_file_path):
        if value_object:
            if isinstance(value_object, CrawlingValue):
                self.value_object = value_object
            elif isinstance(value_object, str):
                if selectors:
                    self.value_object = CrawlingValue(value_object, selectors, crawling_file_path)
                else:
                    raise ValueError(f"{self.__class__}引数エラー:selectors=None")
            else:
                raise ValueError(f"{self.__class__}引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__}引数エラー:value_object=None")

    def get_value_object(self):
        """値オブジェクトを取得する"""
        return copy.deepcopy(self.value_object)

    def get_crawling_file_path(self):
        return copy.deepcopy(self.value_object.crawling_file_path)

    def get_site_urls_from_local(self):
        __site_urls = []
        with open(self.get_crawling_file_path(), 'r', encoding='utf-8') as __local_file:
            __site_urls = __local_file.readlines()
        return copy.deepcopy(__site_urls)

    def create_save_text(self):
        """保存用文字列の作成
        :return: str 保存用文字列の作成
        """
        __buff = json.dumps(self.value_object.site_url, ensure_ascii=False) + '\n'  # サイトURL追加
        # TODO: selectorsはjson.dumpsでシリアライズできないオブジェクトlambdaを含んでいる。pickleでもだめらしい。
        #  代替方法dillとか https://github.com/uqfoundation/dill
        #  marshalとか検討する
        # __buff += json.dumps(self.value_object.selectors, ensure_ascii=False) + '\n'  # セレクタ追加
        if self.value_object and self.value_object.crawling_file_path:
            __buff += json.dumps(self.value_object.crawling_file_path, ensure_ascii=False) + '\n'  # クローリング結果パス追加
        else:
            __buff += '\n'  # クローリング結果パス追加
        if self.value_object and self.value_object.crawling_urls:
            for __url in self.value_object.crawling_urls:
                __buff += __url + '\n'  # クローリング結果url
        return __buff

    def save_text(self):
        """データをファイルに、以下の独自フォーマットで保存する
            * サイトURL
            * セレクタ
            * saveファイルのフルパス
            * クローリング結果urls
        :return: bool 成功/失敗=True/False
        """
        if not self.value_object:
            return False
        with open(self.value_object.crawling_file_path, 'w', encoding='utf-8') as __work_file:
            __buff = self.create_save_text()
            __work_file.write(__buff)
        return True

    def load_text(self, __selectors):
        """独自フォーマットなファイルからデータを読み込む
        TODO: selectors
        :return: bool 成功/失敗=True/False
        """
        with open(self.value_object.crawling_file_path, 'r', encoding='utf-8') as __work_file:
            __buff = __work_file.readlines()
            __site_url = json.loads(__buff[0].rstrip('\n'))
            # del __buff[0]
            # __selectors = json.loads(__buff[0].rstrip('\n'))
            del __buff[0]
            __crawling_file_path = json.loads(__buff[0].rstrip('\n'))
            del __buff[0]
            __crawling_urls: list = []
            for __line in __buff:
                __crawling_urls.append(__line.rstrip('\n'))
            self.value_object = CrawlingValue(__site_url, __selectors, __crawling_file_path, __crawling_urls)
            return True

    def crawling(self):
        site_url = ''
        selectors = {
            'page_urls': [
                (By.XPATH,
                 '//body/div[2]/div[2]/div/a',
                 lambda el: el.get_attribute("href")
                 ),
            ]
        }
        chrome_driver = ChromeDriverHelper(self.value_object.site_url, self.value_object.selectors)


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
