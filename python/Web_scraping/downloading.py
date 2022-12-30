#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ダウンロードユーティリティ
    * URLリストと、保存フォルダを指定して、ダウンロードする
        * 保存フォルダにURLリストのファイルをダウンロードする
        * ダウンロードしたファイルの名前を、ナンバリングした名前に付けなおす
        * 保存フォルダを圧縮する
        * 保存フォルダ内のファイルを削除する
"""
# standard library
import sys  # 終了時のエラー有無
import re  # 正規表現モジュール
import os  # ファイルパス分解
import shutil  # 高水準のファイル操作
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合
import datetime

# 3rd party packages
import requests  # HTTP通信
import urllib3
import pickle
import copy
import bs4  # Beautiful Soup
import pyperclip  # クリップボード
from dataclasses import dataclass
from urllib3.util.retry import Retry

# local source
from const import *

# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class DownloadingValue:
    """
    ダウンロード値オブジェクト
    """
    image_list: list = None
    save_path: str = None

    def __init__(self, image_list, save_path):
        """
        完全コンストラクタパターン

        :param image_list: list ダウンロードするURLのリスト
        :param save_path: str ダウンロード後に保存するフォルダパス
        """
        if image_list:
            object.__setattr__(self, "image_list", image_list)
        if save_path is not None:
            object.__setattr__(self, "save_path", save_path)


class Downloading:
    """
    ダウンロードのユーティリティ
        * 指定のフォルダにダウンロードする
        * ダウンロードしたファイル群の名前を付け直す
        * 指定のフォルダを圧縮する
        * 指定のフォルダ内のファイルを削除する
    """
    value_object: DownloadingValue = None
    image_list: list = None
    save_path: str = None
    src_file_list: list = []
    dst_file_list: list = []
    rename_file_dic: dict = None

    def __init__(self, target_value, save_path=None):
        """
        コンストラクタ

        :param target_value: list ダウンロードするURLのリスト、または、DownloadingValue 値オブジェクト
        :param save_path: str ダウンロード後に保存するフォルダパス
        """
        if target_value is None:
            print('target_valueがNoneです')
            sys.exit(1)
        if isinstance(target_value, DownloadingValue):
            if 0 < len(target_value.image_list):
                self.value_object = target_value
                self.image_list = self.value_object.image_list
                if self.value_object.save_path is not None:
                    self.save_path = self.value_object.save_path
                    self.initialize()
        else:
            if isinstance(target_value, list):
                if 0 < len(target_value):
                    self.image_list = target_value
                    if save_path is not None:
                        self.save_path = save_path
                        self.initialize()

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: ScrapingValue 値オブジェクト
        """
        return copy.deepcopy(self.value_object)

    def initialize(self):
        """
        初期化
            * Input：
            *   画像URLリスト(image_list)
            *   保存ファイルパス(save_path)
            * Output：
            *   保存ファイルパスリスト(src_file_list)
            *   辞書(rename_file_dic)

        :return: None
        """
        self.src_file_list = []
        self.rename_file_dic = {}
        dst_file_namelist = []
        for image_url in self.image_list:
            temp_img_filename = image_url.rsplit('/', 1)[1].replace('?', '_')  # 禁則文字の変換
            print(temp_img_filename)
            dst_file_namelist.append(temp_img_filename)
        if self.save_path[len(self.save_path) - 1] == '\\':
            for file_name in dst_file_namelist:
                self.src_file_list.append(self.save_path + file_name)
        else:
            for file_name in dst_file_namelist:
                self.src_file_list.append(self.save_path + '\\' + file_name)
        # 2つの配列から辞書型に変換
        self.rename_file_dic = {key: val for key, val in zip(self.image_list, self.src_file_list)}
        return

    def download(self):
        """
        target_urlに接続して、image_attrでスクレイピングして、titleとimage_listを更新する

        :return: bool 成功/失敗=True/False
        """
        # フォルダーがなければ作成する
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)
        # ファイルのダウンロード
        for image_url in self.image_list:
            try:
                if not os.path.isfile(self.rename_file_dic[image_url]):  # ファイルの存在チェック
                    images = self.download_image(image_url)
                    if not os.path.isfile(self.rename_file_dic[image_url]):  # ファイルの存在チェック
                        with open(self.rename_file_dic[image_url], "wb") as img_file:
                            img_file.write(images)
                else:
                    print('Skip ' + self.rename_file_dic[image_url])
            except KeyboardInterrupt:
                break
            except Exception as err:
                print(image_url + ' ', end='')  # 改行なし
                print(err)
                return False
        return True

    def download_image(self, image_url=None, timeout=30):
        """
        指定したURLのimageをgetして返す。サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse

        :param image_url: str ダウンロードするURL
        :param timeout: int タイムアウト時間[s]
        :return: bytes 読み込んだimageのバイナリデータ
        """
        response = requests.get(image_url, allow_redirects=False, timeout=timeout)
        if response.status_code != requests.codes.ok:
            e = Exception("HTTP status: " + str(response.status_code))  # + " " + file_url + " " + response.url)
            raise e
        content_type = response.headers["content-type"]
        if 'image' not in content_type:
            e = Exception("Content-Type: " + content_type)  # + " " + file_url + " " + response.url)
            raise e
        return response.content
