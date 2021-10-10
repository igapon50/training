#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file func.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/10/10
# @brief 関数群
# @details 
# @warning 
# @note 

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


##
# @brief 指定したURLリストから、ファイル名+拡張子部分を抽出したリストを作る
# @param file_urllist IN 基にするURLリスト
# @param dst_file_namelist OUT ファイル名+拡張子部分を抽出したリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details file_urllistで指定したファイルURLリストから、ファイル名+拡張子部分を抽出してdst_file_namelistに作成して返す
# @warning 
# @note ファイル名に"?"がある場合は"_"に置換する
def getfilenamefromurl(file_urllist, dst_file_namelist):
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


##
# @brief 指定したURLのimageをgetして返す
# @param url IN 基にするURL
# @param timeout IN タイムアウト時間[s]
# @return dst_file_namelist 読み込んだimageのバイナリデータ
# @details 
# @warning 
# @note サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse
def download_image(file_url, timeout=30):
    response = requests.get(file_url, allow_redirects=False, timeout=timeout)
    if response.status_code != requests.codes.ok:
        e = Exception("HTTP status: " + str(response.status_code))
        raise e
    content_type = response.headers["content-type"]
    if 'image' not in content_type:
        e = Exception("Content-Type: " + content_type)
        raise e
    return response.content


##
# @brief 指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る
# @param src_file_pathlist IN 基にするファイルパスリスト
# @param dst_file_pathlist OUT ナンバリングし直したファイルパスリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details src_file_pathlistで指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイル名に付け直したファイルパスリストをdst_file_pathlistに作成して返す
# @warning 
# @note 
def renameimg(src_file_pathlist, dst_file_pathlist):
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


##
# @brief 指定ファイル群が入ったzip圧縮ファイルを作成する
# @param zipfile_path IN 圧縮ファイルパス
# @param file_pathlist IN 圧縮するファイルパスリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details zipfile_pathで指定したファイルパスにzip圧縮ファイルを作成する。file_pathlistで指定したファイルパスリストを圧縮ファイルに含める。
# @warning 
# @note 
def makezipfile(zipfile_path, file_pathlist):
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
