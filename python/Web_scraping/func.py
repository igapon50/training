#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
関数群、ユーティリティ
"""
# standard library
import sys  # 終了時のエラー有無
import re  # 正規表現モジュール
import pathlib  # 相対パス絶対パス変換
import zipfile  # zipファイル
import os  # ファイルパス分解
import shutil  # 高水準のファイル操作
import glob  # ファイル一覧取得
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

# 3rd party packages
import requests  # HTTP通信
import urllib3
from urllib3.util.retry import Retry
import bs4  # Beautiful Soup
import pyperclip  # クリップボード

# local source
from const import *


def getfilenamefromurl(file_urllist, dst_file_namelist):
    """
    指定したURLリストから、ファイル名+拡張子部分を抽出したリストを作る
    ファイル名に"?"がある場合は"_"に置換する

    :param file_urllist: str 基にするURLリスト
    :param dst_file_namelist: list ファイル名+拡張子部分を抽出したリスト
    :return: bool True 成功 / False 失敗(引数チェックエラーで中断)
    """
    # 引数チェック
    if 0 == len(file_urllist):
        print(sys._getframe().f_code.co_name + '引数file_urllistが空です。')
        return False
    if not isinstance(dst_file_namelist, list):
        print(sys._getframe().f_code.co_name + '引数dst_file_namelistがlistではないです。')
        return False

    for src_img_url in file_urllist:
        dst_img_filename = src_img_url.rsplit('/', 1)[1].replace('?', '_')  # 禁則文字の変換
        print(dst_img_filename)
        dst_file_namelist.append(dst_img_filename)
    return True


def download_image(file_url, timeout=30):
    """
    指定したURLのimageをgetして返す
    サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse

    :param file_url: str 基にするURL
    :param timeout: int タイムアウト時間[s]
    :return: 読み込んだimageのバイナリデータ
    """
    response = requests.get(file_url, allow_redirects=False, timeout=timeout)
    if response.status_code != requests.codes.ok:
        e = Exception("HTTP status: " + str(response.status_code))  # + " " + file_url + " " + response.url)
        raise e
    content_type = response.headers["content-type"]
    if 'image' not in content_type:
        e = Exception("Content-Type: " + content_type)  # + " " + file_url + " " + response.url)
        raise e
    return response.content


def renameimg(src_file_pathlist, dst_file_pathlist):
    """
    指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る
    src_file_pathlistで指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイル名に付け直したファイルパスリストをdst_file_pathlistに作成して返す

    :param src_file_pathlist: list 基にするファイルパスリスト
    :param dst_file_pathlist: list ナンバリングし直したファイルパスリスト
    :return: bool True 成功 / False 失敗(引数チェックエラーで中断)
    """
    # 引数チェック
    if 0 == len(src_file_pathlist):
        print(sys._getframe().f_code.co_name + '引数src_file_pathlistが空です。')
        return False
    if not isinstance(dst_file_pathlist, list):
        print(sys._getframe().f_code.co_name + '引数dst_file_pathlistがlistではないです。')
        return False

    count = 0
    for src_file_path in src_file_pathlist:
        print(src_file_path)
        count += 1
        root, ext = os.path.splitext(src_file_path)
        path, file = os.path.split(src_file_path)
        dst_img_path = path + '\\' + '{:03d}'.format(count) + ext
        print(dst_img_path)
        dst_file_pathlist.append(dst_img_path)
        os.rename(src_file_path, dst_img_path)
    return True


def makezipfile(zipfile_path, file_pathlist):
    """
    指定ファイル群が入ったzip圧縮ファイルを作成する
    zipfile_pathで指定したファイルパスにzip圧縮ファイルを作成する。file_pathlistで指定したファイルパスリストを圧縮ファイルに含める。

    :param zipfile_path: str 圧縮ファイルパス
    :param file_pathlist: list 圧縮するファイルパスリスト
    :return: bool True 成功 / False 失敗(引数チェックエラーで中断)
    """
    # 引数チェック
    if 0 == len(zipfile_path):
        print(sys._getframe().f_code.co_name + '引数zipfile_pathが空です。')
        return False
    if not isinstance(file_pathlist, list):
        print(sys._getframe().f_code.co_name + '引数file_pathlistがlistではないです。')
        return False

    zip = zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED)
    for img_path in file_pathlist:
        zip.write(img_path)
    zip.close()
    return True


def downloadfileclear(save_path):
    """
    保存フォルダからダウンロードファイルを削除する

    :param save_path: str 保存フォルダ
    :return: None
    """
    print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
    shutil.rmtree(save_path)
    if save_path[len(save_path) - 1] == '\\':
        os.mkdir(save_path)
    else:
        os.mkdir(save_path + '\\')
