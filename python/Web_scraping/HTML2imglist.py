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
import bs4 #Beautiful Soup
import pyperclip #クリップボード

# local source
#from const import *
from makezip import *

#title_css_select = 'h1'
#img_css_select = 'img[data-src]'
#img_attr = 'data-src'

#title_css_select = 'html body main h1'
#img_css_select = 'html body main noscript img.vimg'
#img_attr = 'src'

title_css_select = 'html head title'
img_css_select = 'html body div .photoItem img'
img_attr = 'src'

target_url = 'https://www.hot-ishikawa.jp/photo/'
output_file = './result.txt'
folder_path = '.\\folder01'
msg_error_exit = 'エラー終了します。'
html = '''
sample html
'''

## 
# @brief 指定したURLからタイトルと画像URLリストを読み込みホワイトボードとファイルに書き込む
# @param base_url IN 対象のURL
# @param title OUT タイトルを返す
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
	
	res = requests.get(base_url)
	res.raise_for_status()
	html = res.text
	soup = bs4.BeautifulSoup(html, 'html.parser')
	for title_tag in soup.select(title_css_select):
		title = title_tag.string
		print(title)
	with open(output_file, 'w', encoding='utf-8') as imglist_file:
		buff = str(title) + '\n' #クリップボード用変数にタイトル追加
		for img in soup.select(img_css_select):
			absolute_path = str(img[img_attr])
			parse = urlparse(absolute_path)
			if len(parse.scheme) == 0: #絶対パスかチェックする
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
# @note 
def getfilenamefromurl(file_urllist, dst_file_namelist):
	#引数チェック
	if 0 == len(file_urllist):
		print(sys._getframe().f_code.co_name + '引数file_urllistが空です。')
		return False
	if False == isinstance(dst_file_namelist, list):
		print(sys._getframe().f_code.co_name + '引数dst_file_namelistがlistではないです。')
		return False
	
	for src_img_url in file_urllist:
		dst_img_filename = src_img_url.rsplit('/', 1)[1].replace('?', '_')
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
	#引数チェック
	if 2==len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.対象のURL
		target_url = sys.argv[1]
		#folder_path = sys.argv[1]
	elif 1==len(sys.argv):
		target_url = 'https://www.hot-ishikawa.jp/photo/'
		folder_path = '.\\folder01'
	else:
		print('引数が不正です。')
		print(msg_error_exit)
		sys.exit(ret)
	if folder_path[len(folder_path)-1]=='\\':
		files_path = folder_path + '*'
	else:
		files_path = folder_path + '\\*'
	print(files_path)
	
	#ファイルのURLリストを作成
	file_urllist = []
	title = ''
	ret = HTML2imglist(target_url, title, file_urllist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#ファイルのダウンロード
	#irvineでダウンロードする。
	print('ダウンロード完了まで待つ')
	os.system('PAUSE')
	
	#ファイルリストの作成
	#ファイルの順序がファイル名順ではない場合、正しい順序のファイル名リストを作る必要がある。
	#file_urllistからdst_file_namelistを作成する
	dst_file_namelist = []
	src_file_pathlist = []
	ret = getfilenamefromurl(file_urllist, dst_file_namelist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	if folder_path[len(folder_path)-1]=='\\':
		for file_name in dst_file_namelist:
			src_file_pathlist.append(folder_path + file_name)
	else:
		for file_name in dst_file_namelist:
			src_file_pathlist.append(folder_path + '\\' + file_name)
	
	#ダウンロードしたファイルのファイル名付け直し
	file_pathlist = []
	ret = renameimg(src_file_pathlist, file_pathlist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#圧縮ファイル作成
	ret = makezipfile(folder_path + '.zip', file_pathlist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)

	#ファイルの削除
	print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
	os.system('PAUSE')
	shutil.rmtree(folder_path)
	if folder_path[len(folder_path)-1]=='\\':
		os.mkdir(folder_path)
	else:
		os.mkdir(folder_path + '\\')
	
