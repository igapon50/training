#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スクレイピング
"""
# standard library
import sys  # 終了時のエラー有無
import os  # ファイルパス分解
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

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

sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class ScrapingValue:
    """
    スクレイピング値オブジェクト
    """
    image_list: list = None
    save_path: str = None

    def __init__(self, image_list, save_path):
        """
        完全コンストラクタパターン

        :param image_list: list ダウンロードするURLのリスト
        :param save_path: str ダウンロード後に保存するフォルダパス
        """
        if 0 < len(image_list):
            object.__setattr__(self, "image_list", image_list)
        if save_path is not None:
            object.__setattr__(self, "save_path", save_path)


class Scraping:
    """
    スクレイピングのユーティリティ
    """
    files_downloader_value: ScrapingValue = None
    image_list: list = None
    save_path: str = None
    src_file_list: list = []
    dst_file_list: list = []
    rename_file_dic: dict = None

    def __init__(self, target_value, save_path=None):
        """
        コンストラクタ

        :param target_value: list ダウンロードするURLのリスト、または、ScrapingValue 値オブジェクト
        :param save_path: str ダウンロード後に保存するフォルダパス
        """
        if target_value is None:
            print('target_valueがNoneです')
            sys.exit(1)
        if isinstance(target_value, ScrapingValue):
            if 0 < len(target_value.image_list):
                self.files_downloader_value = target_value
                self.image_list = self.files_downloader_value.image_list
                if self.files_downloader_value.save_path is not None:
                    self.save_path = self.files_downloader_value.save_path
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
        return copy.deepcopy(self.files_downloader_value)

    def get_image_list(self):
        """
        画像URLリストを取得する

        :return: list 画像URLリスト
        """
        return copy.deepcopy(self.files_downloader_value.image_list)

    def get_src_file_list(self):
        """
        保存ファイルパスリストを取得する

        :return: list 保存ファイルパスリスト
        """
        return copy.deepcopy(self.src_file_list)

    def get_dst_file_list(self):
        """
        保存ファイルパスリストを取得する

        :return: list リネームファイルパスリスト
        """
        return copy.deepcopy(self.dst_file_list)

    def get_dic_file_list(self):
        """
        リネームファイルパス辞書を取得する

        :return: dict リネームファイルパス辞書
        """
        return copy.deepcopy(self.rename_file_dic)

    def initialize(self):
        """
        初期化
            * 画像URLリストと保存ファイルパスから、保存ファイルパスリストを作る
            * 辞書も作る
            * フォルダがなければフォルダも作る

        :return: None
        """
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

    def rename_images(self):
        """
        指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る

        :return: bool 成功/失敗=True/False
        """
        # ファイルの存在確認
        for src_file_path in self.src_file_list:
            if not os.path.isfile(src_file_path):
                print('ファイル[' + src_file_path + ']が存在しません。')
                print(msg_error_exit)
                # sys.exit()
                return False
        count = 0
        for src_file_path in self.src_file_list:
            print(src_file_path)
            count += 1
            root, ext = os.path.splitext(src_file_path)
            path, file = os.path.split(src_file_path)
            dst_img_path = path + '\\' + '{:03d}'.format(count) + ext
            print(dst_img_path)
            self.dst_file_list.append(dst_img_path)
            os.rename(src_file_path, dst_img_path)
        return True


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    imglist_filepath = RESULT_FILE_PATH
    target_url = DEFAULT_TARGET_URL
    folder_path = OUTPUT_FOLDER_PATH
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        target_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            parse = urlparse(paste_str)
            if 0 < len(parse.scheme):
                target_url = paste_str
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit()
    print(target_url)

    image_url_list = [
        'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/s180-c/fashion_dekora.png',
        'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/s180-c/otaku_girl_fashion.png',
    ]
    fileDownloader = Scraping(image_url_list, folder_path)
    fileDownloader.download()
    fileDownloader.rename_images()
