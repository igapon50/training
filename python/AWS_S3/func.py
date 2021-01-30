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
# @brief 指定したファイルにすべてのオブジェクト情報を書き込む
# @param write_filepath IN 書き込みファイルのパス
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details
# @warning 
# @note 
def writefile_listall(write_filepath):
	#引数チェック
	if 0 == len(write_filepath):
		print(sys._getframe().f_code.co_name + 'write_filepath。')
		return False

	s3 = boto3.resource('s3')
	bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
	print(bucket.name)
	with open(write_filepath, 'w', encoding='utf-8') as write_file:
		buff = bucket.name + '\n' #ファイル書き込み用変数にバケット名追加
		for obj_summary in bucket.objects.all():
			buff += obj_summary.key
			obj = bucket.Object(obj_summary.key)
			buff += '\t' + str(obj.content_type)
			buff += '\t' + str(obj.content_length) + 'byte\n'
		write_file.write(buff) #ファイルへの保存
	return True
