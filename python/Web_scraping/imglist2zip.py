#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imglistファイルからファイル名リストを作り、ダウンロードされていたらzipファイルにまとめる
"""
# local source
from const import *
from func import *
from crawling import *

if __name__ == '__main__':  # インポート時には動かない
    imglist_filepath = RESULT_FILE_PATH
    folder_path = OUTPUT_FOLDER_PATH
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のファイルパス
        imglist_filepath = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、デフォルトファイルパスを用いる
        if 0 == len(imglist_filepath):
            imglist_filepath = RESULT_FILE_PATH
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit()
    print(imglist_filepath)

    # ファイルのURLリストを作成
    crawling = Crawling()
    if not crawling:
        print(msg_error_exit)
        sys.exit(crawling)
    crawling.load_text(RESULT_FILE_PATH + '1.txt')
    file_url_list = crawling.get_image_list()
    title = crawling.get_title()

    # ファイルのダウンロード
    print('ファイルリストを読み込み済み、irvineでダウンロード完了まで待つ')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
    print(title)
    os.system('PAUSE')

    # ファイルリストの作成
    # ファイルの順序がファイル名順ではない場合、正しい順序のファイル名リストを作る必要がある。
    # file_urllistからdst_file_namelistを作成する
    dst_file_namelist = []
    src_file_pathlist = []
    ret = getfilenamefromurl(file_url_list, dst_file_namelist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)
    if folder_path[len(folder_path) - 1] == '\\':
        for file_name in dst_file_namelist:
            src_file_pathlist.append(folder_path + file_name)
    else:
        for file_name in dst_file_namelist:
            src_file_pathlist.append(folder_path + '\\' + file_name)

    # ファイルの存在確認
    for src_file_path in src_file_pathlist:
        if not os.path.isfile(src_file_path):
            print('ファイル[' + src_file_path + ']が存在しません。')
            print(msg_error_exit)
            sys.exit(ret)

    # ダウンロードしたファイルのファイル名付け直し
    file_pathlist = []
    ret = renameimg(src_file_pathlist, file_pathlist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # 圧縮ファイル作成
    ret = makezipfile(folder_path + '.zip', file_pathlist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # 圧縮ファイル名付け直し
    zipfilename = '.\\' + re.sub(r'[\\/:*?"<>|]+', '', title)  # 禁則文字を削除する
    print('圧縮ファイル名を付け直します(タイトル)')
    print(zipfilename)
    # os.system('PAUSE')
    os.rename(folder_path + '.zip', zipfilename + '.zip')

    # ファイルの削除
    print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
    print(folder_path)
    # os.system('PAUSE')
    shutil.rmtree(folder_path)
    if folder_path[len(folder_path) - 1] == '\\':
        os.mkdir(folder_path)
    else:
        os.mkdir(folder_path + '\\')
