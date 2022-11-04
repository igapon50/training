#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * downloadlist.txtから、URLを読み込んでスクレイピング＆ダウンロードする。
    * downloadlist.txtファイルに処理対象サイトURLを、一行に一URL記載しておく。
"""
import subprocess
from chromeDriverHelper import *
from webFileListHelper import *
from downloading import *


@dataclass(frozen=True)
class CrawlingValue:
    """値オブジェクト"""
    crawling_file_path: str = './crawling_list.txt'

    def __init__(self, site_url, selectors, crawling_file_path=crawling_file_path):
        """完全コンストラクタパターン"""
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


class Crawling:
    """クローリング"""
    crawling_file_path: str = CrawlingValue.crawling_file_path
    value_object: CrawlingValue = None

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
                raise ValueError(f"{self.__class__}引数エラー:selectorsがstrではない")
        else:
            raise ValueError(f"{self.__class__}引数エラー:value_object=None")

    def get_crawling_file_path(self):
        return copy.deepcopy(self.value_object.crawling_file_path)

    def get_site_urls_from_local(self):
        __site_urls = []
        with open(self.get_crawling_file_path(), 'r', encoding='utf-8') as __local_file:
            __site_urls = __local_file.readlines()
        return copy.deepcopy(__site_urls)

    def test(self):
        site_url = ''
        selectors = {
            'page_urls': [
                (By.XPATH,
                 '//body/div[2]/div[2]/div/a',
                 lambda el: el.get_attribute("href")
                 ),
            ]
        }


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
