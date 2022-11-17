#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルのヘルパー
"""
import os
import copy
import sys

# 3rd party packages
import requests  # HTTP通信
import pyperclip  # クリップボード
from urllib.parse import urlparse  # URLパーサー
from dataclasses import dataclass
import shutil

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
        """画像か判定する(ext_listにある拡張子か調べる)
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
        if self.dst_filename:
            return copy.deepcopy(self.dst_filename)
        else:
            __parse = urlparse(self.get_url())
            __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
            __base_name = __path_after_name[:__path_after_name.rfind('.')]
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
        """urlの画像拡張子を、ext_listの次の拡張子にシフトする
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

    def download_requests(self):
        """requestsを用いて、ファイルをダウンロードする
        :return: bool 成功/失敗=True/False
        """
        # フォルダーがなければ作成する
        if not os.path.isdir(self.get_folder_path()):
            os.makedirs(self.get_folder_path())
        try:
            if not self.is_exist():
                images = self.get_image_content_by_requests()
                with open(self.get_path(), "wb") as img_file:
                    img_file.write(images)
            else:
                print('Skip ' + self.get_path())
        except KeyboardInterrupt:
            print("キーボード割込み")
        except Exception as err:
            print(self.get_url() + ' ', end='')  # 改行なし
            print(err)
            return False
        return True

    def get_image_content_by_requests(self, timeout=30):
        """requestsを用いて、imageのコンテンツを取得する。
        サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse
        :param timeout: int タイムアウト時間[s]
        :return: bytes 読み込んだimageのバイナリデータ
        """
        response = requests.get(self.get_url(), allow_redirects=False, timeout=timeout)
        if response.status_code != requests.codes.ok:
            e = Exception("HTTP status: " + str(response.status_code))  # + " " + file_url + " " + response.url)
            raise e
        content_type = response.headers["content-type"]
        if 'image' not in content_type:
            e = Exception("Content-Type: " + content_type)  # + " " + file_url + " " + response.url)
            raise e
        return response.content

    def rename_filename(self, new_file_name):
        """ローカルにあるファイルのファイル名を変更して、dst_filenameにも設定する
        :param new_file_name: str 変更する新しいファイル名
        :return: bool True/False=変更(した/しなかった)
        """
        if not os.path.isfile(self.get_path()):
            print('ファイルがローカルにないので処理をスキップします')
            return False
        else:
            dst_path = os.path.join(self.get_folder_path(), new_file_name + self.get_ext())
            if os.path.isfile(dst_path):
                print(f'リネームファイル[{dst_path}]が存在しています')
                return False
            os.rename(self.get_path(), dst_path)
            self.dst_filename = new_file_name
        return True

    def delete_local_file(self):
        """ローカルのファイルを削除する
        :return: None
        """
        if os.path.isfile(self.get_path()):
            os.remove(self.get_path())

    def move(self, new_path):
        """ファイルを移動する(get_folder_path()は変わらない)
        :param new_path: 移動先のフォルダーパス
        :return:
        """
        if self.is_exist():
            # TODO: 移動先のフォルダに同名のファイルが存在する場合の対応
            # TODO: new_pathが存在しない場合
            shutil.move(self.get_path(), new_path)
        else:
            print('ローカルファイルが不足しているため、ファイルの移動を中止した')
