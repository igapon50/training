#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imglist2clip.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/23
# @brief imglistファイルを読み込んでクリップボードにコピーする
# @details imglistファイルを読み込んでクリップボードにコピーする
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
import os #ファイルパス分解
from urllib.parse import urlparse #URLパーサー

# 3rd party packages
import pyperclip #クリップボード

# local source
from const import *

## 
# @brief 指定したファイルからタイトルと画像URLリストを読み込み、クリップボードに書き込む
# @param imglist_filepath IN 対象のファイルパス
# @return True 成功 / False 失敗(エラーで中断)
# @details 
# @warning 
# @note 
def imglist2clip(imglist_filepath):
	#引数チェック
	if 0 == len(imglist_filepath):
		print(sys._getframe().f_code.co_name + '引数imglist_filepathが空です。')
		return False
	if False == os.path.isfile(imglist_filepath):
		print(sys._getframe().f_code.co_name + '引数imglist_filepath=[' + imglist_filepath + ']のファイルが存在しません。')
		return False
	
	with open(imglist_filepath, 'r', encoding='utf-8') as imglist_file:
		line = imglist_file.readline()
		buff = line.rstrip('\n') + '\n' #クリップボード用変数にタイトル追加
		line = imglist_file.readline()
		while line:
			absolute_path = str(line.rstrip('\n'))
			parse = urlparse(absolute_path)
			if 0 == len(parse.scheme): #絶対パスかチェックする
				return False
			print(absolute_path)
			buff += absolute_path + '\n' #クリップボード用変数にurl追加
			line = imglist_file.readline()
		pyperclip.copy(buff) #クリップボードへのコピー
	return True

if __name__ == '__main__': #インポート時には動かない
	imglist_filepath = RESULT_FILE_PATH
	folder_path = OUTPUT_FOLDER_PATH
	#引数チェック
	if 2 == len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.対象のファイルパス
		imglist_filepath = sys.argv[1]
	elif 1 == len(sys.argv):
		#引数がなければデフォルト、デフォルトがなければクリップボードからファイルパスを得る
		if 0 == len(imglist_filepath):
			paste_url = pyperclip.paste()
			parse = urlparse(paste_url)
			if 0 < len(parse.scheme):
				imglist_filepath = paste_url
	else:
		print('引数が不正です。')
		print(msg_error_exit)
		sys.exit(ret)
	print(imglist_filepath)
	if folder_path[len(folder_path)-1] == '\\':
		files_path = folder_path + '*'
	else:
		files_path = folder_path + '\\*'
	print(files_path)
	
	#ファイルのURLリストを作成
	ret = imglist2clip(imglist_filepath)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#ファイルのダウンロード
	#irvineでダウンロードする。
	print('タイトルとURLリストをクリップボードにコピーしました。')
	#os.system('PAUSE')
