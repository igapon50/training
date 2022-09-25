#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
引数URLのサイトにアクセスして、タイトルと最終画像URLをスクレイピングする。
最終画像URLの数字を展開した、URLリストをファイルに保存して、irvineに渡す。
    http:/hoge/10.jpg
    ↓
    http:/hoge/1.jpg ～ http:/hoge/10.jpg
irvineが起動してダウンロードが開始されるので、ダウンロードが終わったらirvineを手動で終了する。
irvineが終了したらダウンロードファイルをチェックする。
失敗している時は、拡張子を変えて、ファイルに保存して、irvineに渡す。
成功している時は、リネームしてzipして削除する。
"""
import urllib.parse
import subprocess
from downloading import *
import sys
from chromeDriverHelper import *
from irvineHelper import *

from dataclasses import dataclass


@dataclass(frozen=True)
class UrlDeploymentValue:
    """URL展開クラスの値オブジェクト
    """
    url: str
    selectors: list
    title: str
    image_urls: list

    def __init__(self, url, selectors, title, image_urls):
        """完全コンストラクタパターン
        :param url: str 処理対象サイトURL
        :param selectors: list スクレイピングする際のセレクタリスト
        :param title: str 取得したサイトタイトル
        :param image_urls: list 取得した画像のURLリスト
        """
        if url is not None:
            if not self.is_url_only(url):
                raise ValueError(f"不正:引数urlがURLではない[{url}]")
            object.__setattr__(self, "url", url)
        if selectors is not None:
            object.__setattr__(self, "selectors", selectors)
        if title is not None:
            object.__setattr__(self, "title", title)
        if image_urls is not None:
            for image_url in image_urls:
                if not self.is_url_only(image_url):
                    raise ValueError(f"不正:引数last_image_urlがurlではない[{image_url}]")
            object.__setattr__(self, "image_urls", image_urls)

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class UrlDeployment:
    """
    「str スクレイプ対象URL, list selectors」が引数で渡されるケース
    「str 末尾画像URL, str タイトル」が引数で渡されるケース
    「list 画像URLリスト, str タイトル」が引数で渡されるケース
    """
    value_object: UrlDeploymentValue = None
    url_list: list = []

    def __init__(self, value_object, selectors):
        if value_object is not None:
            if isinstance(value_object, UrlDeploymentValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, str):
                    # URLかチェックする
                    __parse = urlparse(value_object)
                    if not __parse.scheme:
                        print('引数が不正です。URLではない？')
                        sys.exit(1)
                    if __parse.path[-4:] == '.jpg' or __parse.path[-4:] == '.png':
                        __image_url = value_object
                        __title = '[] a'
                    else:
                        __driver = ChromeDriverHelper(value_object, selectors)
                        __title = __driver.get_title()
                        __image_url = driver.get_last_image_url()
                    __image_urls = self.__deployment(__image_url)
                    self.value_object = UrlDeploymentValue(value_object,
                                                           selectors,
                                                           __title,
                                                           __image_urls,
                                                           )

    def __deployment(self, image_url):
        """末尾画像URLを展開して、URLリスト=url_listを作る
        :param image_url: str 末尾画像URL
        :return: list 展開した画像URLリスト
        """
        if not image_url:
            print('引数が不正です。空です。')
            sys.exit(1)
        __parse = urllib.parse.urlparse(image_url)
        if not __parse.scheme:
            print('引数が不正です。URLではない？')
            sys.exit(1)
        # pathを/前後で分ける
        __path_before_name = __parse.path[:__parse.path.rfind('/') + 1]
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        print(__path_before_name)
        print(__path_after_name)
        # path_after_nameを.前後で分ける
        __base_name = __path_after_name[:__path_after_name.rfind('.')]
        __extend_name = __path_after_name[__path_after_name.rfind('.'):]
        print(__base_name)
        print(__extend_name)
        if not __base_name.isdecimal():
            print('引数が不正です。数値ではない？')
            sys.exit(1)
        __count = int(__base_name)
        for d_count in range(__count):
            self.url_list.append(urllib.parse.urlunparse((__parse.scheme,
                                                          __parse.netloc,
                                                          __path_before_name + str(d_count + 1) + __extend_name,
                                                          __parse.params,
                                                          __parse.query,
                                                          __parse.fragment)))
        return self.url_list

    def get_title(self):
        """タイトル取得
        :return: str タイトル
        """
        return copy.deepcopy(self.value_object.title)

    def get_image_urls(self):
        """画像リスト取得
        :return: list 画像リスト
        """
        return copy.deepcopy(self.value_object.image_urls)


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    folder_path = OUTPUT_FOLDER_PATH
    url_list: list = []
    main_title = '[] a'
    list_file_path = './irvine_download_list.txt'
    # 引数チェック
    if 3 == len(sys.argv):
        # Pythonに以下の3つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        # 2.対象のタイトル(後にファイル名にする)
        paste_str = sys.argv[1]
        main_title = sys.argv[2]
    elif 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        paste_str = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
    else:
        print('引数が不正です。')
        sys.exit(1)

    # URLかチェックする
    if not paste_str:
        print('引数が不正です。空です。')
        sys.exit(1)
    parse = urlparse(paste_str)
    if not parse.scheme:
        print('引数が不正です。URLではない？')
        sys.exit(1)
    if parse.path[-4:] == '.jpg' or parse.path[-4:] == '.png':
        main_image_url = paste_str
    else:
        main_url = paste_str
        print(main_url)
        driver = ChromeDriverHelper(main_url, SELECTORS)
        main_title = driver.get_title()
        main_image_url = driver.get_last_image_url()
    print(main_title)
    print(main_image_url)

    # 末尾画像URL=main_image_urlを展開して、URLリスト=url_listを作る
    if not main_image_url:
        print('引数が不正です。空です。')
        sys.exit(1)
    parse = urllib.parse.urlparse(main_image_url)
    if not parse.scheme:
        print('引数が不正です。URLではない？')
        sys.exit(1)
    # pathを/前後で分ける
    path_before_name = parse.path[:parse.path.rfind('/') + 1]
    path_after_name = parse.path[parse.path.rfind('/') + 1:]
    print(path_before_name)
    print(path_after_name)
    # path_after_nameを.前後で分ける
    base_name = path_after_name[:path_after_name.rfind('.')]
    extend_name = path_after_name[path_after_name.rfind('.'):]
    print(base_name)
    print(extend_name)
    if not base_name.isdecimal():
        print('引数が不正です。数値ではない？')
        sys.exit(1)
    count = int(base_name)
    for i in range(count):
        url_list.append(urllib.parse.urlunparse((parse.scheme,
                                                 parse.netloc,
                                                 path_before_name + str(i + 1) + extend_name,
                                                 parse.params,
                                                 parse.query,
                                                 parse.fragment)))
    print(url_list)

    # irvineを起動して、ダウンロードする
    irvine = IrvineHelper(url_list)
    irvine.download()
    fileDownloader = Downloading(url_list, folder_path)

    if not fileDownloader.is_src_exist():
        # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
        fileDownloader.rename_ext_shift()
        irvine = IrvineHelper(fileDownloader.image_list)
        irvine.download()
        fileDownloader = Downloading(fileDownloader.image_list, folder_path)

    if not fileDownloader.rename_images():
        sys.exit()
    if not fileDownloader.make_zip_file():
        sys.exit()
    fileDownloader.rename_zip_file(main_title)
    fileDownloader.download_file_clear()
