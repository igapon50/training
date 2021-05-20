#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imglist2dl.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/05/21
# @brief imglistファイルからファイル名リストを作り、ダウンロードする。
# @details imglistファイルからファイル名リストを作り、ダウンロードする。
# @warning 
# @note 

# local source
from const import *
from func import *

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
        sys.exit(ret)
    print(imglist_filepath)

    # ファイルのURLリストを作成
    file_urllist = []
    title = []
    ret = imglist2filelist(imglist_filepath, title, file_urllist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # ファイルのダウンロード
    print('ファイルリストを読み込み済み、irvineでダウンロード完了まで待つ')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
    print(title[0])
    os.system('PAUSE')

    # ファイルリストの作成
    # ファイルの順序がファイル名順ではない場合、正しい順序のファイル名リストを作る必要がある。
    # file_urllistからdst_file_namelistを作成する
    dst_file_namelist = []
    src_file_pathlist = []
    ret = getfilenamefromurl(file_urllist, dst_file_namelist)
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
    dic = {key: val for key, val in zip(file_urllist, src_file_pathlist)}
    # フォルダーがなければ作成する
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    # ファイルのダウンロード
    for file_url in file_urllist:
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
