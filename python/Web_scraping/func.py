#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file func.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/26
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
# @brief 指定したURLからタイトルと画像URLリストを読み込みクリップボードとファイルに書き込む
# @param base_url IN 対象のURL
# @param imglist_filepath IN URLリストを保存するファイルパス
# @param title OUT タイトルリストを返す
# @param file_urllist OUT 画像URLリストを返す
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details title_css_selectで指定した値をタイトル扱いする。img_css_selectで指定したタグのimg_attrで指定した属性を画像URL扱いする。title_css_selectとimg_css_selectは、CSSセレクタで指定する。
# @warning 
# @note 
def HTML2imglist(base_url, imglist_filepath, title, file_urllist):
    # 引数チェック
    if 0 == len(base_url):
        print(sys._getframe().f_code.co_name + '引数base_urlが空です。')
        return False
    if not isinstance(file_urllist, list):
        print(sys._getframe().f_code.co_name + '引数file_urllistがlistではないです。')
        return False

    retries = Retry(connect=5, read=2, redirect=5)
    http = urllib3.PoolManager(retries=retries)
    res = http.request('GET', base_url, timeout=10, headers=HEADERS_DIC)
    soup = bs4.BeautifulSoup(res.data, 'html.parser')
    title_tag = soup.title
    title.append(title_tag.string)
    print(title_tag.string)
    with open(imglist_filepath, 'w', encoding='utf-8') as imglist_file:
        buff = str(title[0]) + '\n'  # クリップボード用変数にタイトル追加
        for img in soup.select(img_css_select):
            absolute_path = str(img[img_attr])
            parse = urlparse(absolute_path)
            if 0 == len(parse.scheme):  # 絶対パスかチェックする
                absolute_path = urljoin(base_url, absolute_path)
            file_urllist.append(absolute_path)
            print(absolute_path)
            buff += absolute_path + '\n'  # クリップボード用変数にurl追加
        imglist_file.write(buff)  # ファイルへの保存
        pyperclip.copy(buff)  # クリップボードへのコピー
    return True


## 
# @brief 指定したファイルからタイトルと画像URLリストを読み込み、クリップボードに書き込む
# @param imglist_filepath IN 対象のファイルパス
# @return True 成功 / False 失敗(エラーで中断)
# @details 
# @warning 
# @note 
def imglist2clip(imglist_filepath):
    # 引数チェック
    if 0 == len(imglist_filepath):
        print(sys._getframe().f_code.co_name + '引数imglist_filepathが空です。')
        return False
    if not os.path.isfile(imglist_filepath):
        print(sys._getframe().f_code.co_name + '引数imglist_filepath=[' + imglist_filepath + ']のファイルが存在しません。')
        return False

    with open(imglist_filepath, 'r', encoding='utf-8') as imglist_file:
        line = imglist_file.readline()
        buff = line.rstrip('\n') + '\n'  # クリップボード用変数にタイトル追加
        line = imglist_file.readline()
        while line:
            absolute_path = str(line.rstrip('\n'))
            parse = urlparse(absolute_path)
            if 0 == len(parse.scheme):  # 絶対パスかチェックする
                return False
            print(absolute_path)
            buff += absolute_path + '\n'  # クリップボード用変数にurl追加
            line = imglist_file.readline()
        pyperclip.copy(buff)  # クリップボードへのコピー
    return True


## 
# @brief 指定したファイルからタイトルと画像URLリストを読み込む
# @param imglist_filepath IN 対象のファイルパス
# @param title OUT タイトルリストを返す
# @param file_urllist OUT 画像ファイル名リストを返す
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details 
# @warning 
# @note 
def imglist2filelist(imglist_filepath, title, file_urllist):
    # 引数チェック
    if 0 == len(imglist_filepath):
        print(sys._getframe().f_code.co_name + '引数imglist_filepathが空です。')
        return False
    if not isinstance(file_urllist, list):
        print(sys._getframe().f_code.co_name + '引数file_urllistがlistではないです。')
        return False

    with open(imglist_filepath, 'r', encoding='utf-8') as imglist_file:
        line = imglist_file.readline()
        title.append(line.rstrip('\n'))  # タイトル追加
        # line = imglist_file.readline() #空読みで一行読み捨てする(内容がわかる画像を最初に表示するタイプのサイトで読み捨てする)
        line = imglist_file.readline()
        while line:
            absolute_path = str(line.rstrip('\n'))
            parse = urlparse(absolute_path)
            if 0 == len(parse.scheme):  # 絶対パスかチェックする
                return False
            file_urllist.append(absolute_path)
            line = imglist_file.readline()
    return True


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
