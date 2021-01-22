#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file HTML2imglist.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2020/08/26
# @brief Webサイトから画像のURLリストを作る
# @details Webサイトから画像のURLリストを作ってホワイトボードにコピーし、ファイルにも保存する
# @warning 
# @note 

__author__ = "Ryosuke Igarashi(HN:igapon)"
__copyright__ = "Copyright (c) 2020 igapon"
__credits__ = ["Ryosuke Igarashi"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "igapon"
__email__ = "igapon@gmail.com"
__status__ = "Development" #"Prototype" or "Development" or "Production"

# standard library
import sys #終了時のエラー有無
import re #正規表現モジュール
import pathlib #相対パス絶対パス変換
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

# local source
from const import *

## 
# @brief 指定したURLからタイトルと画像URLリストを読み込みクリップボードとファイルに書き込む
# @param base_url IN 対象のURL
# @param title OUT タイトルリストを返す
# @param file_urllist OUT 画像URLリストを返す
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details title_css_selectで指定した値をタイトル扱いする。img_css_selectで指定したタグのimg_attrで指定した属性を画像URL扱いする。title_css_selectとimg_css_selectは、CSSセレクタで指定する。
# @warning 
# @note 
def HTML2imglist(base_url, title, file_urllist):
	#引数チェック
	if 0 == len(base_url):
		print(sys._getframe().f_code.co_name + '引数base_urlが空です。')
		return False
	if False == isinstance(file_urllist, list):
		print(sys._getframe().f_code.co_name + '引数file_urllistがlistではないです。')
		return False
	
	retries = Retry(connect=5, read=2, redirect=5)
	http = urllib3.PoolManager(retries=retries)
	res = http.request('GET', base_url, timeout=10, headers=HEADERS_DIC)
	soup = bs4.BeautifulSoup(res.data, 'html.parser')
	for title_tag in soup.select(title_css_select):
		title.append(title_tag.string)
		print(title_tag.string)
	with open(RESULT_FILE_PATH, 'w', encoding='utf-8') as imglist_file:
		buff = str(title[0]) + '\n' #クリップボード用変数にタイトル追加
		for img in soup.select(img_css_select):
			absolute_path = str(img[img_attr])
			parse = urlparse(absolute_path)
			if 0 == len(parse.scheme): #絶対パスかチェックする
				absolute_path = urljoin(base_url, absolute_path)
			file_urllist.append(absolute_path)
			print(absolute_path)
			buff += absolute_path + '\n' #クリップボード用変数にurl追加
		imglist_file.write(buff) #ファイルへの保存
		pyperclip.copy(buff) #クリップボードへのコピー
	return True

if __name__ == '__main__': #インポート時には動かない
	target_url = DEFAULT_TARGET_URL
	folder_path = OUTPUT_FOLDER_PATH
	#引数チェック
	if 2==len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.対象のURL
		target_url = sys.argv[1]
	elif 1 == len(sys.argv):
		#引数がなければクリップボードからURLを得る
		if 0 < len(target_url):
			paste_url = pyperclip.paste()
			parse = urlparse(paste_url)
			if 0 < len(parse.scheme):
				target_url = paste_url
	else:
		print('引数が不正です。')
		print(msg_error_exit)
		sys.exit(ret)
	print(target_url)
	if folder_path[len(folder_path)-1]=='\\':
		files_path = folder_path + '*'
	else:
		files_path = folder_path + '\\*'
	print(files_path)
	
	#ファイルのURLリストを作成
	file_urllist = []
	title = []
	ret = HTML2imglist(target_url, title, file_urllist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#ファイルのダウンロード
	#irvineでダウンロードする。
	print('irvineにペーストして、ダウンロード完了まで待つ')
	#os.system('PAUSE')
