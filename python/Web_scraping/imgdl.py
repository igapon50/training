#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imgdl.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/26
# @brief Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる。
# @details Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる。
# @warning 
# @note 

# local source
from const import *
from func import *

if __name__ == '__main__':  # インポート時には動かない
    imglist_filepath = RESULT_FILE_PATH
    target_url = DEFAULT_TARGET_URL
    folder_path = OUTPUT_FOLDER_PATH
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        target_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            parse = urlparse(paste_str)
            if 0 < len(parse.scheme):
                target_url = paste_str
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit(ret)
    print(target_url)

    # ファイルのURLリストを作成
    file_urllist = []
    title = []
    ret = HTML2imglist(target_url, imglist_filepath, title, file_urllist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # ファイルのダウンロード
    print('タイトルとURLリストをクリップボードにコピーし、ファイルに保存済み')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
    print(title[0])
    # os.system('PAUSE')

    # ファイルのURLリストを作成
    file_urllist = []
    title = []
    ret = imglist2filelist(imglist_filepath, title, file_urllist)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

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
            images = download_image(file_url)
            if not os.path.isfile(dic[file_url]):  # ファイルの存在チェック
                with open(dic[file_url], "wb") as img_file:
                    img_file.write(images)
        except KeyboardInterrupt:
            break
        except Exception as err:
            print(file_url + ' ', end='')  # 改行なし
            print(err)

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
    zipfilename = '.\\' + re.sub(r'[\\/:*?"<>|]+', '', str(title[0]))  # 禁則文字を削除する
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
