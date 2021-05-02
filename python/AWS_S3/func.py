#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file func.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/05/02
# @brief 関数群
# @details 
# @warning 
# @note 

# standard library
import sys  # 終了時のエラー有無
import re  # 正規表現モジュール
import pathlib  # 相対パス絶対パス変換
import time
from datetime import timezone
import zipfile  # zipファイル
import os  # ファイルパス分解
import shutil  # 高水準のファイル操作
import glob  # ファイル一覧取得
import datetime  # 日付時刻変換
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

# 3rd party packages
import requests  # HTTP通信
import urllib3
from urllib3.util.retry import Retry
import bs4  # Beautiful Soup
import pyperclip  # クリップボード
import boto3  # AWS S3

# local source
from const import *


##
# @brief 指定したバケットのオブジェクト情報を、指定した結果ファイルに、書き込み、オブジェクトとupdate時刻の辞書を作る
# @param bucket IN 読み込むバケット名
# @param result_path IN 書き込みファイルのパス
# @param bucket_dic OUT オブジェクトとupdate時刻JSTのディクショナリ
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning 
# @note 
def get_bucket_filelist(bucket, result_path, bucket_dic):
    # 引数チェック
    if bucket is None:
        print(sys._getframe().f_code.co_name + 'bucket')
        return False
    if 0 == len(result_path):
        print(sys._getframe().f_code.co_name + 'result_path')
        return False
    if bucket_dic is None:
        print(sys._getframe().f_code.co_name + 'bucket_dic')
        return False

    print(bucket.name)
    bucket_dic.clear()
    with open(result_path, 'w', encoding='utf-8') as write_file:
        buff = bucket.name + '\n'  # ファイル書き込み用変数にバケット名追加
        for obj_summary in bucket.objects.all():
            obj = bucket.Object(obj_summary.key)
            file_modified = utc_to_jst(str(obj.last_modified))
            buff += obj_summary.key + '\t' \
                    + file_modified + '\t' \
                    + str(obj.content_length) + 'byte\n'
            # + str(obj.content_type) + '\t'
            if obj_summary.key[len(obj_summary.key) - 1] != '/':
                bucket_dic.setdefault(obj_summary.key, file_modified)
        # pyperclip.copy(str(bucket_dic))  # クリップボードへのコピー
        write_file.write(buff)  # ファイルへの保存
    return True


##
# @brief 指定したフォルダ以下のオブジェクト情報を、指定した結果ファイルに書き込み、オブジェクトと更新時刻の辞書を作る
# @param target_path IN オブジェクト情報を読み込むルートフォルダ
# @param result_path IN オブジェクト情報を書き込むファイルパス
# @param local_dic OUT オブジェクトと更新時刻JSTのディクショナリ
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning
# @note
def get_local_filelist(target_path, result_path, local_dic):
    if 0 == len(target_path):
        print(sys._getframe().f_code.co_name + 'target_path')
        return False
    if 0 == len(result_path):
        print(sys._getframe().f_code.co_name + 'result_path')
        return False
    if local_dic is None:
        print(sys._getframe().f_code.co_name + 'local_dic')
        return False

    local_dic.clear()
    with open(result_path, 'w', encoding='utf-8') as write_file:
        temp_path = os.path.join(target_path, '**')
        if temp_path[len(temp_path) - 1] != '\n':
            temp_path.strip('\n')
        buff = temp_path + '\n'
        for x in listup_files(temp_path):  # ファイル判定
            if os.path.isfile(x):
                p = pathlib.Path(x)
                dt = datetime.datetime.fromtimestamp(p.stat().st_mtime)  # JST
                buff += x.strip(target_path).replace(os.sep, '/') + '\t' \
                        + str(dt) + '\t' \
                        + str(os.path.getsize(x)) + 'byte\n'
                local_dic.setdefault(x.strip(target_path).replace(os.sep, '/'), str(dt))
            else:  # フォルダの時
                buff += x.strip(target_path).replace(os.sep, '/') + '/\n'
        pyperclip.copy(str(local_dic))  # クリップボードへのコピー
        write_file.write(buff)  # ファイルへの保存
    return True


##
# @brief 指定したフォルダ以下のファイルパスリストを取得する
# @param temp_path IN 読み込むルートフォルダ
# @return ファイルパスリスト
# @details
# @warning
# @note
def listup_files(temp_path):
    for p in glob.glob(temp_path, recursive=True):
        yield p


##
# @brief 指定したバケット辞書とローカル辞書を比較して、更新日時がローカルの方が新しければアップロードする
# @param bucket_dic IN バケット辞書[パス,更新日時]
# @param local_dic IN ローカル辞書[パス,更新日時]
# @param result_path IN アップロード結果を書き込むファイルパス
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning
# @note フォルダやファイル名の大文字小文字区別が不十分
def bucket_upload(bucket_dic, local_dic, result_path):
    # 引数チェック
    if bucket_dic is None:
        print(sys._getframe().f_code.co_name + 'bucket_dic')
        return False
    if local_dic is None:
        print(sys._getframe().f_code.co_name + 'local_dic')
        return False
    if 0 == len(result_path):
        print(sys._getframe().f_code.co_name + 'result_path')
        return False

    with open(result_path, 'w', encoding='utf-8') as write_file:
        buff = str(datetime.datetime.now()) + '\n'
        for key in local_dic.keys():
            bucket_time = bucket_dic.get(key)
            if bucket_time is None:
                continue
            if local_dic[key] > bucket_time:
                print('アップデートする:' + key)
                buff += 'bucket <- local :' + key + '\n'
            else:
                print('アップデートしない:' + key)
                buff += 'bucket -- local :' + key + '\n'
        # pyperclip.copy(bucket_dic)  # クリップボードへのコピー
        write_file.write(buff)  # ファイルへの保存
    return True

##
# @brief UTC->JST変換
# @param timestamp_utc IN UTC時間
# @return JST時間
# @details
# @warning
# @note
def utc_to_jst(timestamp_utc):
    datetime_utc = datetime.datetime.strptime(timestamp_utc, "%Y-%m-%d %H:%M:%S%z")
    # datetime_utc = datetime.datetime.strptime(timestamp_utc + "+0000", "%Y-%m-%d %H:%M:%S.%f%z")
    datetime_jst = datetime_utc.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    timestamp_jst = datetime.datetime.strftime(datetime_jst, '%Y-%m-%d %H:%M:%S.%f')
    return timestamp_jst
