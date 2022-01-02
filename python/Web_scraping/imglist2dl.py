#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imglistファイルからファイル名リストを作り、ダウンロードする
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

    # 2つの配列から辞書型に変換
    dic = {key: val for key, val in zip(file_url_list, src_file_pathlist)}
    # フォルダーがなければ作成する
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    # ファイルのダウンロード
    for file_url in file_url_list:
        try:
            if not os.path.isfile(dic[file_url]):  # ファイルの存在チェック
                images = download_image(file_url)
                if not os.path.isfile(dic[file_url]):  # ファイルの存在チェック
                    with open(dic[file_url], "wb") as img_file:
                        img_file.write(images)
            else:
                print('Skip ' + dic[file_url])
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(file_url + ' ', end='')  # 改行なし
            print(err)
