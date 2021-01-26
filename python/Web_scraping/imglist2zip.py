#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imglist2zip.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/26
# @brief imglistファイルからファイル名リストを作り、ダウンロードされていたらzipファイルにまとめる。
# @details imglistファイルからファイル名リストを作り、ダウンロードされていたらzipファイルにまとめる。
# @warning 
# @note 

# local source
from const import *
from func import *

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
		#引数がなければ、デフォルトファイルパスを用いる
		if 0 == len(imglist_filepath):
			imglist_filepath = RESULT_FILE_PATH
	else:
		print('引数が不正です。')
		print(msg_error_exit)
		sys.exit(ret)
	print(imglist_filepath)
	
	#ファイルのURLリストを作成
	file_urllist = []
	title = []
	ret = imglist2filelist(imglist_filepath, title, file_urllist)
	if False == ret:
		print(msg_error_exit)
		sys.exit(ret)
	
	#ファイルのダウンロード
	#irvineでダウンロードする。
	print('ファイルリストを読み込み済み、irvineでダウンロード完了まで待つ')
	print(title[0])
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
	#os.system('PAUSE')
	os.rename(folder_path + '.zip', zipfilename + '.zip')
	
	#ファイルの削除
	print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
	print(folder_path)
	#os.system('PAUSE')
	shutil.rmtree(folder_path)
	if folder_path[len(folder_path)-1]=='\\':
		os.mkdir(folder_path)
	else:
		os.mkdir(folder_path + '\\')
	
