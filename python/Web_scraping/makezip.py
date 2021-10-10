#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file makezip.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/10/10
# @brief 指定フォルダ内のファイル群をzip圧縮する
# @details 指定フォルダ内のファイル群をzip圧縮する
# @warning 
# @note 

# local source
from const import *
from func import *

if __name__ == '__main__':  # インポート時には動かない
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.圧縮したいファイル群が入っているフォルダー
        folder_path = sys.argv[1]
    elif 1 == len(sys.argv):
        folder_path = OUTPUT_FOLDER_PATH
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit()
    if folder_path[len(folder_path) - 1] == '\\':
        files_path = folder_path + '*'
    else:
        files_path = folder_path + '\\*'
    print(files_path)

    file_pathlist = glob.glob(files_path)

    # 圧縮ファイル作成
    ret = makezipfile(folder_path + '.zip', file_pathlist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)
