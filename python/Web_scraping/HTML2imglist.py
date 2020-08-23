#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name: HTML2imglist.py
Purpose:Webサイトから画像のURLリストを作ってホワイトボードにコピーする
Description:ファイルにも保存する
"""
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
import os #ファイルパス分解
import glob #ファイル一覧取得
from urllib.parse import urlparse #URLパーサー
from urllib.parse import urljoin #URL結合

# 3rd party packages
import requests #HTTP通信
import bs4 #Beautiful Soup
import pyperclip #クリップボード

# local source
#from const import *

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
folder_name = 'folder01'
folder_path = '.\\' + folder_name + '\\*'
html = '''
sample html
'''

def HTML2imglist(base_url, title, img_urllist):
	#引数チェック
	if 0 == len(base_url):
		print(sys._getframe().f_code.co_name + '引数base_urlが空です。')
		return False
	if False == isinstance(img_urllist, list):
		print(sys._getframe().f_code.co_name + '引数img_urllistがlistではないです。')
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
			img_urllist.append(absolute_path)
			print(absolute_path)
			buff += absolute_path + '\n' #クリップボード用変数にurl追加
		imglist_file.write(buff) #ファイルへの保存
		pyperclip.copy(buff) #クリップボードへのコピー
	return True

def renameimg(src_imgfile_pathlist, dst_imgfile_pathlist):
	#引数チェック
	if 0 == len(src_imgfile_pathlist):
		print(sys._getframe().f_code.co_name + '引数src_imgfile_pathlistが空です。')
		return False
	if False == isinstance(dst_imgfile_pathlist, list):
		print(sys._getframe().f_code.co_name + '引数dst_imgfile_pathlistがlistではないです。')
		return False
	
	count = 0
	for src_img_path in src_imgfile_pathlist:
		print(src_img_path)
		count+=1
		root, ext = os.path.splitext(src_img_path)
		path, file = os.path.split(src_img_path)
		dst_img_path = path + '\\' + '{:03d}'.format(count) + ext
		print(dst_img_path)
		dst_imgfile_pathlist.append(dst_img_path)
		os.rename(src_img_path, dst_img_path)
	return True

def makezipfile(zipfile_path, imgfile_pathlist):
	#引数チェック
	if 0 == len(zipfile_path):
		print(sys._getframe().f_code.co_name + '引数zipfile_pathが空です。')
		return False
	if False == isinstance(imgfile_pathlist, list):
		print(sys._getframe().f_code.co_name + '引数imgfile_pathlistがlistではないです。')
		return False
	
	zip = zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED)
	for img_path in imgfile_pathlist:
		zip.write(img_path)
	zip.close()
	return True

if __name__ == '__main__': #インポート時には動かない
	#引数チェック
	if 2==len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.対象のURL
		target_url = sys.argv[1]
	print(target_url)
	
	#画像ファイルのURLリストを作成
	img_urllist = []
	title = ''
	ret = HTML2imglist(target_url, title, img_urllist)
	if False == ret:
		print('エラー終了します。')
		sys.exit(ret)
	
	#画像ファイルのダウンロード
	#irvineでダウンロードする。
	
	#画像ファイルリストの作成
	#画像ファイルの順序がファイル名順ではない場合、正しい順序のファイル名リストを作る必要がある。
	#img_urllistからsrc_imgfile_pathlistを作成する
	
	#ダウンロードした画像ファイルのファイル名付け直し
	src_imgfile_pathlist = glob.glob(folder_path)
	dst_imgfile_pathlist = []
	ret = renameimg(src_imgfile_pathlist, dst_imgfile_pathlist)
	if False == ret:
		print('エラー終了します。')
		sys.exit(ret)
	
	#圧縮ファイル作成
	ret = makezipfile(folder_name + '.zip', dst_imgfile_pathlist)
	if False == ret:
		print('エラー終了します。')
		sys.exit(ret)

