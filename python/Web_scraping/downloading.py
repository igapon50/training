#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ダウンロードユーティリティ
    * URLリストと、保存フォルダを指定して、ダウンロードする
        * URLリストのファイルをダウンロードする
        * ダウンロードしたファイルの名前を、ナンバリングした名前に付けなおす
        * 保存フォルダを圧縮する
        * 保存フォルダ内のファイルを削除する
"""
# standard library
import sys  # 終了時のエラー有無
import re  # 正規表現モジュール
import zipfile  # zipファイル
import os  # ファイルパス分解
import shutil  # 高水準のファイル操作
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
        if 0 < len(image_list):
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

    def get_image_list(self):
        """
        画像URLリストを取得する

        :return: list 画像URLリスト
        """
        return copy.deepcopy(self.value_object.image_list)

    def get_src_file_list(self):
        """
        リネーム前の、保存ファイルパスリストを取得する

        :return: list ダウンロードファイルパスリスト
        """
        return copy.deepcopy(self.src_file_list)

    def get_dst_file_list(self):
        """
        リネーム後の、保存ファイルパスリストを取得する

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
            * Input：
            *   画像URLリスト(image_list)
            *   保存ファイルパス(save_path)
            * Output：
            *   保存ファイルパスリスト(src_file_list)
            *   辞書(rename_file_dic)

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

    def is_exist(self):
        """
        ローカルにファイルが全て存在するか調べる
        :return: bool 存在する/存在しない=True/False
        """
        for img_path in self.dst_file_list:
            if not os.path.isfile(img_path):
                print('ファイル[' + img_path + ']が存在しません。')
                print(msg_error_exit)
                return False
        return True

    def rename_images(self):
        """
        指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る

        :return: bool 成功/失敗=True/False
        """
        # ファイルの存在確認
        if not self.is_exist():
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
            if os.path.isfile(dst_img_path):
                print(f'リネームファイル{dst_img_path}が存在しています')
                return False
            os.rename(src_file_path, dst_img_path)
        return True

    def rename_ext(self, ext='.png'):
        """
        ダウンロードできていないファイルの拡張子を変更する
        :param ext: str 変更する拡張子 
        :return:
        """
        for i, image_url in enumerate(self.image_list):
            if not os.path.isfile(self.rename_file_dic[image_url]):
                parse_path = urlparse(image_url)
                image_url = urljoin(parse_path.scheme, image_url)
                root, _ext = os.path.splitext(self.rename_file_dic[image_url])
                self.image_list[i] = urljoin(image_url, root + ext)
        self.initialize()

    def make_zip_file(self):
        """
        リネーム後のダウンロードファイルを、一つの圧縮ファイルにする

        :return: bool 成功/失敗=True/False
        """
        if not self.is_exist():
            return False
        if os.path.isfile(self.save_path + '.zip'):
            print(f'圧縮ファイル{self.save_path}.zipが既に存在しています')
            return False
        with zipfile.ZipFile(self.save_path + '.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img_path in self.dst_file_list:
                zip_file.write(img_path)
        return True

    def download_file_clear(self):
        """
        保存フォルダからダウンロードファイルを削除する

        :return: None
        """
        print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
        shutil.rmtree(self.save_path)
        if self.save_path[len(self.save_path) - 1] == '\\':
            os.mkdir(self.save_path)
        else:
            os.mkdir(self.save_path + '\\')

    def rename_zip_file(self, title):
        """
        圧縮ファイルの名前を付けなおす

        :param title: str 付け直すファイル名(禁則文字は削除される)
        :return: bool 成功/失敗=True/False
        """
        # 禁則文字を削除する
        zip_file_new_name = '.\\' + re.sub(r'[\\/:*?"<>|]+', '', title)
        print(f'圧縮ファイル名を付け直します:{zip_file_new_name}.zip')
        if os.path.isfile(zip_file_new_name + '.zip'):
            print(f'圧縮リネームファイル{zip_file_new_name}.zipが既に存在しています')
            return False
        os.rename(self.save_path + '.zip', zip_file_new_name + '.zip')
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

    # テスト　若者 | かわいいフリー素材集 いらすとや
    image_url_list = [
        'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/s180-c/fashion_dekora.png',
        'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/s180-c/otaku_girl_fashion.png',
    ]
    fileDownloader = Downloading(image_url_list, folder_path)
    ret = fileDownloader.download()
    if not ret:
        sys.exit()
    ret = fileDownloader.rename_images()
    if not ret:
        sys.exit()
    ret = fileDownloader.make_zip_file()
    if not ret:
        sys.exit()
    fileDownloader.rename_zip_file('若者 | かわいいフリー素材集 いらすとや')
    fileDownloader.download_file_clear()
    # 拡張子をjpgに変更する
    fileDownloader.rename_ext('jpg')
    print(fileDownloader.image_list)
