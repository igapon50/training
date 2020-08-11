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
from urllib.parse import urlparse #URLパーサー
from urllib.parse import urljoin #URL結合

# 3rd party packages
import requests #HTTP通信
import bs4 #Beautiful Soup
import pyperclip #クリップボード

# local source
#from const import *

#title_tag = 'h1'
#css_select = 'img[data-src]'
#target_attr = 'data-src'

#title_tag = 'h1'
#css_select = 'noscript .vimg'
#target_attr = 'src'

title_tag = 'title'
css_select = 'div .photoItem img'
target_attr = 'src'

target_url = 'https://www.hot-ishikawa.jp/photo/'
output_file = './result.txt'
html = '''
sample html
'''

def HTML2imglist(base_url):
	res = requests.get(base_url)
	res.raise_for_status()
	html = res.text
	soup = bs4.BeautifulSoup(html, 'html.parser')
	for title in soup.select(title_tag):
		print(title)
	with open(output_file, 'w', encoding='utf-8') as imglist_file:
		buff = str(title) + '\n' #クリップボード用変数にタイトル追加
		for img in soup.select(css_select):
			print(img)
			absolute_path = str(img[target_attr])
			parse = urlparse(absolute_path)
			if len(parse.scheme) == 0: #絶対パスかチェックする
				absolute_path = urljoin(base_url, absolute_path)
			buff += absolute_path + '\n' #クリップボード用変数にurl追加
		imglist_file.write(buff) #ファイルへの保存
		pyperclip.copy(buff) #クリップボードへのコピー

if __name__ == '__main__': #インポート時には動かない
	if 2==len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.対象のURL
		target_url = sys.argv[1]
	print(target_url)
	HTML2imglist(target_url)

