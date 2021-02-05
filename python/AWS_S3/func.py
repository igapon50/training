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
import sys #終了時のエラー有無
import re #正規表現モジュール
import pathlib #相対パス絶対パス変換
import zipfile #zipファイル
import os #ファイルパス分解
import shutil #高水準のファイル操作
import glob #ファイル一覧取得
import datetime #日付時刻変換
from urllib.parse import urlparse #URLパーサー
from urllib.parse import urljoin #URL結合

# 3rd party packages
import requests #HTTP通信
import urllib3
from urllib3.util.retry import Retry
import bs4 #Beautiful Soup
import pyperclip #クリップボード
import boto3 #AWS S3

# local source
from const import *

## 
# @brief 指定したファイルにオブジェクト情報を書き込む
# @param bucket IN 読み込むバケット名
# @param write_filepath IN 書き込みファイルのパス
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning 
# @note 
def get_bucket_filelist(bucket, result_path):
	#引数チェック
	if bucket is None:
		print(sys._getframe().f_code.co_name + 'bucket')
		return False
	if 0 == len(result_path):
		print(sys._getframe().f_code.co_name + 'result_path')
		return False

	print(bucket.name)
	with open(result_path, 'w', encoding='utf-8') as write_file:
		buff = bucket.name + '\n' #ファイル書き込み用変数にバケット名追加
		for obj_summary in bucket.objects.all():
			buff += obj_summary.key
			obj = bucket.Object(obj_summary.key)
			#buff += '\t' + str(obj.content_type)
			buff += '\t' + str(obj.last_modified)
			buff += '\t' + str(obj.content_length) + 'byte\n'
		write_file.write(buff) #ファイルへの保存
	return True

##
# @brief 指定したフォルダ以下のオブジェクト情報を取得する
# @param target_path IN オブジェクト情報を読み込むルートフォルダ
# @param result_path IN オブジェクト情報を書き込むファイルパス
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning
# @note
def get_local_filelist(target_path, result_path):
	if 0 == len(target_path):
		print(sys._getframe().f_code.co_name + 'target_path')
		return False
	if 0 == len(result_path):
		print(sys._getframe().f_code.co_name + 'result_path')
		return False

	with open(result_path, 'w', encoding='utf-8') as write_file:
		temp_path = os.path.join(target_path, '**')
		buff = temp_path + '\n'
		for x in listup_files(temp_path): #ファイル判定
			if os.path.isfile(x):
				p = pathlib.Path(x)
				dt = datetime.datetime.fromtimestamp(p.stat().st_mtime)
				buff += x.strip(target_path) + '\t'\
						+ str(dt) + '\t'\
						+ str(os.path.getsize(x)) + 'byte\n'
			else: #フォルダの時
				buff += x.strip(target_path) + '\n'
		write_file.write(buff) #ファイルへの保存
	return True
##
# @brief 指定したフォルダ以下のファイルパスリストを取得する
# @param temp_path IN 読み込むルートフォルダ
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning
# @note
def listup_files(temp_path):
	for p in glob.glob(temp_path, recursive=True):
	    yield p

##
# @brief 指定したファイルにすべてのオブジェクト情報を書き込む
# @param write_filepath IN 書き込みファイルのパス
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning
# @note
def download_listall(bucket, read_filepath):
	#引数チェック
	if 0 == len(read_filepath):
		print(sys._getframe().f_code.co_name + 'read_filepath')
		return False

	print(bucket.name)
	with open(read_filepath, 'r', encoding='utf-8') as read_file:
		buff = bucket.name + '\n' #ファイル書き込み用変数にバケット名追加
		for obj_summary in bucket.objects.all():
			buff += obj_summary.key
			obj = bucket.Object(obj_summary.key)
			#buff += '\t' + str(obj.content_type)
			buff += '\t' + str(obj.last_modified)
			buff += '\t' + str(obj.content_length) + 'byte\n'
		line = read_file.readline() #ファイルへの保存
	return True