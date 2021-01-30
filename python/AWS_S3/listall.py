#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file listall.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/30
# @brief AWS S3の指定バケットのオブジェクト情報をファイルに書き込む
# @details 
# @warning 
# @note 

# local source
from const import *
from func import *

if __name__ == '__main__': #インポート時には動かない
	#引数チェック
	if 2 == len(sys.argv):
		#Pythonに以下の2つ引数を渡す想定
		#0は固定でスクリプト名
		#1.書き込むファイルパス
		write_filepath = sys.argv[1]
	elif 1 == len(sys.argv):
		#引数がなければデフォルト
		#0は固定でスクリプト名
		write_filepath = RESULT_FILE_PATH
	else:
		print('引数が不正です。')
		print(msg_error_exit)
		sys.exit(False)

	ret = writefile_listall(write_filepath)
	#sys.exit(ret)
