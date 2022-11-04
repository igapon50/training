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
    folder_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FOLDER_PATH).replace(os.sep, '/')

    def __init__(self, url, folder_path=folder_path):
        """完全コンストラクタパターン
        :param url: str webファイルのURL
        :param folder_path: str フォルダのフルパス(セパレータは、円マークでもスラッシュでもよい、内部ではスラッシュで持つ)
        """
        if not url:
            raise ValueError(f"{self.__class__}引数エラー:url=None")
        if not self.is_url_only(url):
            raise ValueError(f"{self.__class__}引数エラー:urlがURLではない[{url}]")
        object.__setattr__(self, "url", url)
        if not folder_path:
            raise ValueError(f"{self.__class__}引数エラー:file_path=None")
        object.__setattr__(self, "folder_path", folder_path.replace(os.sep, '/'))

    @staticmethod
    def is_url_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class WebFileHelper:
    """webファイルのヘルパー
    """
    value_object: WebFileHelperValue = None
    folder_path: str = WebFileHelperValue.folder_path
    # TODO: ext_list増やすなら、優先度順にrename_url_ext_shiftが働くようにしたい
    # ext_list = ['.jpg', '.png', '.jpeg', '.webp', '.svg', '.svgz', '.gif', '.tif', '.tiff', '.psd', '.bmp']
    ext_list: list = ['.jpg', '.png', '.gif']  # これを画像とする
    dst_filename: str = None

    def __init__(self, value_object=None, folder_path=folder_path):
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
            elif isinstance(value_object, str):
                __url = value_object
                if folder_path:
                    self.value_object = WebFileHelperValue(__url, folder_path)
                    self.dst_filename = self.get_filename()
            else:
                raise ValueError(f"{self.__class__}引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__}引数エラー:value_object=None")

    @staticmethod
    def fixed_path(file_path):
        """フォルダ名の禁止文字を全角文字に置き換える
        :param file_path: str 置き換えたいフォルダパス
        :return: str 置き換え後のフォルダパス
        """
        __file_path = copy.deepcopy(file_path)
        __file_path = __file_path.replace(':', '：')
        __file_path = __file_path.replace('*', '＊')
        __file_path = __file_path.replace('?', '？')
        __file_path = __file_path.replace('"', '”')
        __file_path = __file_path.replace('<', '＜')
        __file_path = __file_path.replace('>', '＞')
        __file_path = __file_path.replace('|', '｜')
        return __file_path

    @staticmethod
    def fixed_file_name(file_name):
        """ファイル名の禁止文字を全角文字に置き換える
        :param file_name: str 置き換えたいファイル名
        :return: str 置き換え後のファイル名
        """
        __file_name = copy.deepcopy(file_name)
        __file_name = __file_name.replace(os.sep, '￥')
        __file_name = __file_name.replace('/', '／')
        return WebFileHelper.fixed_path(__file_name)

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

    def is_exist(self):
        """ファイルがローカルに存在すればTrueを返す
        :return: bool
        """
        return os.path.isfile(self.get_path())

    def get_url(self):
        """URLを得る
        :return: str URL
        """
        return copy.deepcopy(self.value_object.url)

    def get_path(self):
        """ファイルのフルパスを得る
        :return: str ファイルのフルパス(セパレータはスラッシュ)
        """
        return copy.deepcopy(os.path.join(self.get_folder_path(),
                                          self.get_filename() + self.get_ext(),
                                          ).replace(os.sep, '/'))

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
            self.value_object = WebFileHelperValue(__url, self.get_folder_path())

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
