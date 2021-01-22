#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imglist2zip.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/21
# @brief imglistファイルからファイル名リストを作りそのファイルでzipファイルを作る
# @details imglistファイルからファイル名リストを作りそのファイルでzipファイルを作る
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
from const import *
from makezip import *

## 
# @brief 指定したファイルからタイトルと画像URLリストを読み込み、クリップボードに書き込む
# @param imglist_filepath IN 対象のファイルパス
# @param title OUT タイトルリストを返す
# @param file_urllist OUT 画像ファイル名リストを返す
# @return True 成功 / False 失敗(引数チェックエラーで中断)
# @details 
# @warning 
# @note 
def imglist2filelist(imglist_filepath, title, file_urllist):
	#引数チェック
	if 0 == len(imglist_filepath):
		print(sys._getframe().f_code.co_name + '引数imglist_filepathが空です。')
		return False
	if False == isinstance(file_urllist, list):
		print(sys._getframe().f_code.co_name + '引数file_urllistがlistではないです。')
		return False
	
	with open(imglist_filepath, 'r', encoding='utf-8') as imglist_file:
		line = imglist_file.readline()
		title.append(line.rstrip('\n')) #タイトル追加
		line = imglist_file.readline()
		while line:
			absolute_path = str(line.rstrip('\n'))
			parse = urlparse(absolute_path)
			if 0 == len(parse.scheme): #絶対パスかチェックする
				return False
			file_urllist.append(absolute_path)
			line = imglist_file.readline()
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
	imglist_filepath = RESULT_FILE_PATH
	folder_path = OUTPUT_FOLDER_PATH
	#引数チェック
	if 2==len(sys.argv):
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
	if folder_path[len(folder_path)-1]=='\\':
		files_path = folder_path + '*'
	else:
		files_path = folder_path + '\\*'
	print(files_path)
	
	#ファイルのURLリストを作成
	file_urllist = []
	title = []
	ret = imglist2filelist(imglist_filepath, title, file_urllist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#ファイルのダウンロード
	#irvineでダウンロードする。
	print('ファイル名をナンバリングして圧縮ファイルを作ります')
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
	
	#ファイルの存在確認
	for src_file_path in src_file_pathlist:
		if False == os.path.isfile(src_file_path):
			print('ファイル[' + src_file_path + ']が存在しません。')
			print(msg_error_exit)
			sys.exit(ret)
	
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
	
	#圧縮ファイル名付け直し
	zipfilename = '.\\' + re.sub(r'[\\/:*?"<>|]+','',str(title[0])) #禁則文字を削除する
	print('圧縮ファイル名を付け直します(タイトル)')
	print(zipfilename)
	os.system('PAUSE')
	os.rename(folder_path + '.zip', zipfilename + '.zip')
	
	#ファイルの削除
	print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
	print(folder_path)
	os.system('PAUSE')
	shutil.rmtree(folder_path)
	if folder_path[len(folder_path)-1]=='\\':
		os.mkdir(folder_path)
	else:
		os.mkdir(folder_path + '\\')
	
