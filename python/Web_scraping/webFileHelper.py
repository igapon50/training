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
    """webファイルヘルパー値オブジェクト
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
    """webファイルのヘルパー
    """
    value_object: WebFileHelperValue = None
    __root_path = os.path.dirname(os.path.abspath(__file__))
    __folder_path = os.path.join(__root_path, OUTPUT_FOLDER_PATH).replace(os.sep, '/')
    # TODO: ext_list増やすなら、優先度順にrename_url_ext_shiftが働くようにしたい
    # ext_list = ['.jpg', '.png', '.jpeg', '.webp', '.svg', '.svgz', '.gif', '.tif', '.tiff', '.psd', '.bmp']
    ext_list = ['.jpg', '.png']  # これを画像とする
    dst_filename: str = None

    def __init__(self, value_object, folder_path=__folder_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlとfolder_pathより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param folder_path: str フォルダのフルパス
        """
        if value_object:
            if isinstance(value_object, WebFileHelperValue):
                self.value_object = value_object
                self.dst_filename = self.get_filename()
            else:
                if isinstance(value_object, str):
                    __url = value_object
                    if folder_path:
                        self.value_object = WebFileHelperValue(__url,
                                                               folder_path,
                                                               )
                        self.dst_filename = self.get_filename()

    def is_image(self):
        """画像化判定
        :return: bool
        """
        __parse = urlparse(self.get_url())
        for __ext in self.ext_list:
            offset = len(__ext)
            if __parse.path[-offset:].lower() == __ext:
                return True
        return False

    def get_url(self):
        """URLを得る
        :return: str URL
        """
        return copy.deepcopy(self.value_object.url)

    def get_folder_path(self):
        """フォルダーパスを得る
        :return: str folder_path
        """
        return copy.deepcopy(self.value_object.folder_path)

    def get_filename(self):
        """ファイル名を得る
        :return: str ファイル名(拡張子除く)
        """
        __parse = urlparse(self.get_url())
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        __base_name = __path_after_name[:__path_after_name.rfind('.')]
        if self.dst_filename:
            return copy.deepcopy(self.dst_filename)
        else:
            return copy.deepcopy(__base_name)

    def get_ext(self):
        """拡張子を得る
        :return: str ファイルの拡張子(ドットを含む)
        """
        __parse = urlparse(self.get_url())
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        __extend_name = __path_after_name[__path_after_name.rfind('.'):]
        return copy.deepcopy(__extend_name)

    def get_path(self):
        """ファイルのフルパスを得る
        :return: str ファイルのフルパス(セパレータはスラッシュ)
        """
        return copy.deepcopy(os.path.join(self.get_folder_path(),
                                          self.get_filename() + self.get_ext(),
                                          ).replace(os.sep, '/'))

    def rename_url_ext_shift(self):
        """ext_listの次の拡張子に、urlの拡張子をシフトする
        現在の拡張子はext_listの何番目か調べて、次の拡張子にurlを変更して、値オブジェクトを作り直す
        :return:
        """
        if not self.is_image():
            print('画像じゃないので処理をスキップ')
        else:
            __index = self.ext_list.index(self.get_ext())
            __index = (__index + 1) % len(self.ext_list)
            __ext = self.ext_list[__index]
            __url = self.get_url()[::-1].replace(self.get_ext()[::-1], __ext[::-1])[::-1]
            self.value_object = WebFileHelperValue(__url,
                                                   self.get_folder_path(),
                                                   )

    def rename_filename(self, new_file_name):
        """ローカルにあるファイルのファイル名を変更する
        :param new_file_name: str 変更する新しいファイル名
        :return: bool
        """
        if not os.path.isfile(self.get_path()):
            print('ファイルがローカルにないので処理をスキップします')
        else:
            dst_path = os.path.join(self.get_folder_path(), new_file_name + self.get_ext())
            if os.path.isfile(dst_path):
                print(f'リネームファイル[{dst_path}]が存在しています')
                return False
            os.rename(self.get_path(), dst_path)
            self.dst_filename = new_file_name
        return True


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
        if paste_str:
            parse = urlparse(paste_str)
            if parse.scheme:
                main_url = paste_str
        # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()

    # テスト　若者 | かわいいフリー素材集 いらすとや
    image_url = 'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'\
                '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'\
                's180-c/fashion_dekora.png'
    web_file_helper = WebFileHelper(image_url)
    print(web_file_helper.is_image())
    for __item in web_file_helper.ext_list:
        main_url = web_file_helper.get_url()
        main_folder_path = web_file_helper.get_folder_path()
        main_path = web_file_helper.get_path()
        main_filename = web_file_helper.get_filename()
        main_ext = web_file_helper.get_ext()
        print(main_url + ", " + main_folder_path)
        print(main_path + ", " + main_filename + ", " + main_ext)
        web_file_helper.rename_url_ext_shift()
    # pyperclip.copy(path + ", " + filename + ", " + ext)
