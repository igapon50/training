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
import zipfile #zipファイル
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
#from requests.adapters import HTTPAdapter
import bs4 #Beautiful Soup
import pyperclip #クリップボード

# local source
#from const import *
from makezip import *

#title_css_select = 'h1'
#img_css_select = 'img[data-src]'
#img_attr = 'data-src'

#title_css_select = 'html head title'
#img_css_select = 'html body div.kijibox p a'
#img_attr = 'href'

#title_css_select = 'html head title'
#img_css_select = 'html body noscript img.list-img'
#img_attr = 'src'

#title_css_select = 'html head title'
#img_css_select = 'html body div .content a'
#img_attr = 'href'

#title_css_select = 'html body main h1'
#img_css_select = 'html body main noscript img.vimg'
#img_attr = 'src'

title_css_select = 'html head title'
img_css_select = 'html body div .photoItem img'
img_attr = 'src'

HEADERS_DIC = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
DEFAULT_TARGET_URL = 'https://www.hot-ishikawa.jp/photo/'
RESULT_FILE_PATH = './result.txt' #タイトルと、ダウンロードするファイルのURLの列挙を書き込むファイル
OUTPUT_FOLDER_PATH = '.\\folder01' #ダウンロードしたファイルの保存パス、
msg_error_exit = 'エラー終了します。'

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
#	res = requests.get(base_url, headers=HEADERS_DIC)
#	res.raise_for_status() #200以外の時例外を出して処理を終了する
#	html = res.text
#	soup = bs4.BeautifulSoup(html, 'html.parser')
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

## 
# @brief 指定したURLリストから、ファイル名+拡張子部分を抽出したリストを作る
# @param file_urllist IN 基にするURLリスト
# @param dst_file_namelist OUT ファイル名+拡張子部分を抽出したリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details file_urllistで指定したファイルURLリストから、ファイル名+拡張子部分を抽出してdst_file_nakelistに作成して返す
# @warning 
# @note ファイル名に"?"がある場合は"_"に置換する
def getfilenamefromurl(file_urllist, dst_file_namelist):
	#引数チェック
	if 0 == len(file_urllist):
		print(sys._getframe().f_code.co_name + '引数file_urllistが空です。')
		return False
	if False == isinstance(dst_file_namelist, list):
		print(sys._getframe().f_code.co_name + '引数dst_file_namelistがlistではないです。')
		return False
	
	for src_img_url in file_urllist:
		dst_img_filename = src_img_url.rsplit('/', 1)[1].replace('?', '_') #禁則文字の変換
		print(dst_img_filename)
		dst_file_namelist.append(dst_img_filename)
	return True

## 
# @brief 指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイルパスリストを作る
# @param src_file_pathlist IN 基にするファイルパスリスト
# @param dst_file_pathlist OUT ナンバリングし直したファイルパスリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details src_file_pathlistで指定したファイルパスリストから、ファイル名部分をナンバリングし直したファイル名に付け直したファイルパスリストをdst_file_pathlistに作成して返す
# @warning 
# @note 
def renameimg(src_file_pathlist, dst_file_pathlist):
	#引数チェック
	if 0 == len(src_file_pathlist):
		print(sys._getframe().f_code.co_name + '引数src_file_pathlistが空です。')
		return False
	if False == isinstance(dst_file_pathlist, list):
		print(sys._getframe().f_code.co_name + '引数dst_file_pathlistがlistではないです。')
		return False
	
	count = 0
	for src_file_path in src_file_pathlist:
		print(src_file_path)
		count+=1
		root, ext = os.path.splitext(src_file_path)
		path, file = os.path.split(src_file_path)
		dst_img_path = path + '\\' + '{:03d}'.format(count) + ext
		print(dst_img_path)
		dst_file_pathlist.append(dst_img_path)
		os.rename(src_file_path, dst_img_path)
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
