#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルリストのヘルパー
"""
import os
import copy
import sys
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー
from dataclasses import dataclass

from const import *
from webFileHelper import *


@dataclass(frozen=True)
class WebFileListHelperValue:
    """Webファイルリスト値オブジェクト
    """
    file_list: list

    def __init__(self, file_list):
        """完全コンストラクタパターン
        :param file_list: list webファイルリスト
        """
        if not file_list:
            raise ValueError(f"不正:引数file_listが無い")
        for count, item in enumerate(file_list):
            if not isinstance(item, WebFileHelper):
                raise ValueError(f"不正:引数file_listの{count}個目がWebFileHelperで無い")
        object.__setattr__(self, "file_list", file_list)


class WebFileListHelper:
    """webファイルのヘルパー
    """
    # value_object: WebFileListHelperValue = None
    __driver = None
    __web_file_list: list = []
    __root_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(__root_path, OUTPUT_FOLDER_PATH).replace(os.sep, '/')

    def __init__(self, value_object, folder_path=folder_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlリストとfolder_pathより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param folder_path: str フォルダのフルパス
        """
        if value_object is not None:
            if isinstance(value_object, WebFileListHelperValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, list):
                    if folder_path is not None:
                        urls = value_object
                        for url in urls:
                            self.__web_file_list.append(WebFileHelper(url,
                                                                      folder_path,
                                                                      ))
                        self.value_object = WebFileListHelperValue(self.__web_file_list)

    def get_web_file_list_helper(self):
        return copy.deepcopy(self.__web_file_list)
    # downloading.pyから以下を移植する
    # ファイルリストのファイルが存在する is_src_exist/is_dst_exist
    # ファイルリストのファイルが存在しないファイルの拡張子をシフトする rename_ext_shift
    # ファイルリストのファイル名を付け直す rename_images
    # 圧縮ファイルを作る make_zip_file
    # 圧縮ファイルのファイル名を付け直す rename_zip_file
    # ファイルリストのファイル削除(フォルダ削除) rename_file_clear


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

    # テスト　若者 | かわいいフリー素材集 いらすとや
    image_url_list = [
        'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'
        's180-c/fashion_dekora.png',
        'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/'
        's180-c/otaku_girl_fashion.png',
    ]
    web_file_list = WebFileListHelper(image_url_list)
    for web_file in web_file_list.value_object.file_list:
        path = web_file.get_path()
        filename = web_file.get_filename()
        ext = web_file.get_ext()
        print(path + ", " + filename + ", " + ext)
