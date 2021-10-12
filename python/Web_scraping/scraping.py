#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file scraping.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/10/10
# @brief
# @details
# @warning 
# @note

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


##
# @brief Value Objects
# @details scrapingクラスの値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class scrapingValue:
    image_list: list = None
    save_path: str = None

    # 完全コンストラクタパターン
    def __init__(self,
                 image_list: 'list ダウンロードするURLのリスト',
                 save_path: 'str ダウンロード後に保存するフォルダパス',
                 ):
        if 0 < len(image_list):
            object.__setattr__(self, "image_list", image_list)
        if save_path is not None:
            object.__setattr__(self, "save_path", save_path)


##
# @brief
# @details
# @warning
# @note

class scraping:
    files_downloader_value: scrapingValue = None
    image_list: list = None
    save_path: str = None
    src_file_list: list = []
    dst_file_list: list = []
    rename_file_dic: dict = None

    # コンストラクタ
    def __init__(self,
                 image_list: 'list ダウンロードするURLのリスト' = None,
                 save_path: 'str ダウンロード後に保存するフォルダパス' = None,
                 files_downloader_value: 'scrapingValue 値オブジェクト' = None,
                 ):
        if files_downloader_value is not None:
            self.files_downloader_value = files_downloader_value
            if 0 < len(self.files_downloader_value.image_list):
                self.image_list = self.files_downloader_value.image_list
                if self.files_downloader_value.save_path is not None:
                    self.save_path = self.files_downloader_value.save_path
                    self.initialize()
        else:
            if 0 < len(image_list):
                self.image_list = image_list
                if save_path is not None:
                    self.save_path = save_path
                    self.initialize()

    # 値オブジェクトを取得する
    def get_value_objects(self
                          ) -> 'scrapingValue 値オブジェクト':
        return copy.deepcopy(self.files_downloader_value)

    # 画像URLリストを取得する
    def get_image_list(self
                       ) -> 'list 画像URLリスト':
        return copy.deepcopy(self.files_downloader_value.image_list)

    # 保存ファイルパスリストを取得する
    def get_src_file_list(self
                          ) -> 'list 保存ファイルパスリスト':
        return copy.deepcopy(self.src_file_list)

    # 保存ファイルパスリストを取得する
    def get_dst_file_list(self
                          ) -> 'list リネームファイルパスリスト':
        return copy.deepcopy(self.dst_file_list)

    # リネームファイルパス辞書を取得する
    def get_dic_file_list(self
                          ) -> 'dict リネームファイルパス辞書':
        return copy.deepcopy(self.rename_file_dic)

    # 初期化、画像URLリストと保存ファイルパスから、保存ファイルパスリストを作る。辞書も作る。フォルダがなければフォルダも作る。
    def initialize(self):
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

    # target_urlに接続して、image_attrでスクレイピングして、titleとimage_listを更新する
    def download(self
                 ) -> 'bool 成功/失敗=True/False':
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

    # 指定したURLのimageをgetして返す。サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse
    def download_image(self,
                       image_url: 'str ダウンロードするURL' = None,
                       timeout: 'int タイムアウト時間[s]' = 30,
                       ) -> 'bytes 読み込んだimageのバイナリデータ':
        response = requests.get(image_url, allow_redirects=False, timeout=timeout)
        if response.status_code != requests.codes.ok:
            e = Exception("HTTP status: " + str(response.status_code))  # + " " + file_url + " " + response.url)
            raise e
        content_type = response.headers["content-type"]
        if 'image' not in content_type:
            e = Exception("Content-Type: " + content_type)  # + " " + file_url + " " + response.url)
            raise e
        return response.content

    # 指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る
    def renameimg(self
                  ) -> 'bool 成功/失敗=True/False':
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
    fileDownloader = scraping(image_url_list, folder_path)
    fileDownloader.download()
    fileDownloader.renameimg()
