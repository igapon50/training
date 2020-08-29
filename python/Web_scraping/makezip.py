#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file makezip.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2020/08/30
# @brief 指定フォルダ内のファイル群をzip圧縮する
# @details 指定フォルダ内のファイル群をzip圧縮する
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
import zipfile #zipファイル
import os #ファイルパス分解
import glob #ファイル一覧取得

# local source
#from const import *

folder_path = '.\\folder01'
msg_error_exit = 'エラー終了します。'

## 
# @brief 指定ファイル群が入ったzip圧縮ファイルを作成する
# @param zipfile_path IN 圧縮ファイルパス
# @param file_pathlist IN 圧縮するファイルパスリスト
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details zipfile_pathで指定したファイルパスにzip圧縮ファイルを作成する。file_pathlistで指定したファイルパスリストを圧縮ファイルに含める。
# @warning 
# @note 
def makezipfile(zipfile_path, file_pathlist):
	#引数チェック
	if 0 == len(zipfile_path):
		print(sys._getframe().f_code.co_name + '引数zipfile_pathが空です。')
		return False
	if False == isinstance(file_pathlist, list):
		print(sys._getframe().f_code.co_name + '引数file_pathlistがlistではないです。')
		return False
	
	zip = zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED)
	for img_path in file_pathlist:
		zip.write(img_path)
	zip.close()
	return True

if __name__ == '__main__': #インポート時には動かない
	#引数チェック
	if 2==len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.圧縮したいファイル群が入っているフォルダー
		folder_path = sys.argv[1]
	elif 1==len(sys.argv):
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
	
	file_pathlist = glob.glob(files_path)
	
	#圧縮ファイル作成
	ret = makezipfile(folder_path + '.zip', file_pathlist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)

