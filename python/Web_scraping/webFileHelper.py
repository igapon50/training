#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルのヘルパー
"""
import os
import copy
import sys
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー
from dataclasses import dataclass

from const import *


@dataclass(frozen=True)
class WebFileHelperValue:
    """Chromeドライバ値オブジェクト
    """
    url: str
    folder_path: str

    def __init__(self, url, folder_path):
        """完全コンストラクタパターン
        :param url: str webファイルのURL
        :param folder_path: str フォルダのフルパス(セパレータは、円マークでもスラッシュでもよい、内部ではスラッシュで持つ)
        """
        if not url:
            raise ValueError(f"不正:引数urlが無い")
        if not self.is_url_only(url):
            raise ValueError(f"不正:引数urlがURLではない[{url}]")
        object.__setattr__(self, "url", url)
        if not folder_path:
            raise ValueError(f"不正:引数file_pathが無い")
        object.__setattr__(self, "folder_path", folder_path.replace(os.sep, '/'))

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class WebFileHelper:
    """指定のサイトを読み込み、スクレイピングする
    """
    # value_object: WebFileHelperValue = None
    __driver = None
    __source = None
    root_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(root_path, OUTPUT_FOLDER_PATH).replace(os.sep, '/')

    def __init__(self, value_object, folder_path=folder_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlとfolder_pathより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param folder_path: str フォルダのフルパス
        """
        if value_object is not None:
            if isinstance(value_object, WebFileHelperValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, str):
                    url = value_object
                    if folder_path is not None:
                        self.value_object = WebFileHelperValue(url,
                                                               folder_path,
                                                               )

    def is_image(self):
        """画像化判定
        :return: bool
        """
        ext_list = ['.jpg', '.png']  # これを画像とする
        __parse = urlparse(self.value_object.url)
        for __ext in ext_list:
            offset = len(__ext)
            if __parse.path[-offset:].lower() == __ext:
                return True
        return False

    def get_filename(self):
        """ファイル名を得る
        :return: str ファイル名(拡張子除く)
        """
        __parse = urlparse(self.value_object.url)
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        __base_name = __path_after_name[:__path_after_name.rfind('.')]
        return copy.deepcopy(__base_name)

    def get_ext(self):
        """拡張子を得る
        :return: str ファイルの拡張子(ドットを含む)
        """
        __parse = urlparse(self.value_object.url)
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        __extend_name = __path_after_name[__path_after_name.rfind('.'):]
        return copy.deepcopy(__extend_name)

    def get_path(self):
        """ファイルのフルパスを得る
        :return: str ファイルのフルパス(セパレータはスラッシュ)
        """
        return copy.deepcopy(os.path.join(self.folder_path, self.get_filename() + self.get_ext()).replace(os.sep, '/'))


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
        if not paste_str:
            parse = urlparse(paste_str)
            if not parse.scheme:
                main_url = paste_str
        # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()

    file = WebFileHelper(main_url)
    path = file.get_path()
    filename = file.get_filename()
    ext = file.get_ext()
    print(path + ", " + filename + ", " + ext)
    pyperclip.copy(path + ", " + filename + ", " + ext)
