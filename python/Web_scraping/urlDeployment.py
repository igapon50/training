#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数値URLを展開して、ファイルに保存して、irvineに渡す。
    http:/hoge/10.jpg
    ↓
    http:/hoge/1.jpg ～ http:/hoge/10.jpg
irvineが起動してダウンロードが開始されるので、ダウンロードが終わったらirvineを手動で終了する。
irvineが終了したらダウンロードファイルをチェックする。
失敗している時は、拡張子を変えて、ファイルに保存して、irvineに渡す。
成功している時は、リネームしてzipして削除する。
"""
import urllib.parse
import subprocess
from downloading import *


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    target_url = None
    folder_path = OUTPUT_FOLDER_PATH
    parse = None
    url_list: list = []
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        paste_str = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
    else:
        print('引数が不正です。')
        sys.exit(1)
    # URLかチェックする
    if 0 < len(paste_str):
        parse = urllib.parse.urlparse(paste_str)
        if 0 < len(parse.scheme):
            target_url = paste_str
            # pathを/前後で分ける
            path_before_name = parse.path[:parse.path.rfind('/') + 1]
            path_after_name = parse.path[parse.path.rfind('/') + 1:]
            print(path_before_name)
            print(path_after_name)
            # path_after_nameを.前後で分ける
            base_name = path_after_name[:path_after_name.rfind('.')]
            extend_name = path_after_name[path_after_name.rfind('.'):]
            print(base_name)
            print(extend_name)
            if base_name.isdecimal():
                count = int(base_name)
                for i in range(count):
                    url_list.append(urllib.parse.urlunparse((parse.scheme,
                                                             parse.netloc,
                                                             path_before_name + str(i + 1) + extend_name,
                                                             parse.params,
                                                             parse.query,
                                                             parse.fragment)))
            else:
                print('引数が不正です。数値ではない？')
                sys.exit(1)
        else:
            print('引数が不正です。URLではない？')
            sys.exit(1)
    else:
        print('引数が不正です。空です。')
        sys.exit(1)
    print(target_url)
    print(url_list)

    with open('./result_list.txt', 'w', encoding='utf-8') as work_file:
        buff = ''
        for absolute_path in url_list:
            buff += absolute_path + '\n'  # 画像URL追加
        work_file.write(buff)  # ファイルへの保存
    fileDownloader = Downloading(url_list, folder_path)
    # irvineを起動して、終了されるのを待つ
    cmd = 'c:\\Program1\\irvine1_3_0\\irvine.exe ./result_list.txt'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    running = False
    for line in proc.stdout:
        if "irvine.exe" in str(line):
            running = True
    if not fileDownloader.is_src_exist():
        # ダウンロードに失敗しているときは、拡張子を変えてダウンロードしなおす
        if extend_name == '.jpg':
            fileDownloader.rename_ext()
        elif extend_name == '.png':
            fileDownloader.rename_ext('.jpg')
        # result_list.txtを作り直す
        with open('./result_list.txt', 'w', encoding='utf-8') as work_file:
            buff = ''
            for absolute_path in fileDownloader.image_list:
                buff += absolute_path + '\n'  # 画像URL追加
            work_file.write(buff)  # ファイルへの保存
        fileDownloader = Downloading(fileDownloader.image_list, folder_path)
        # ダウンロードしなおす
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        running = False
        for line in proc.stdout:
            if "irvine.exe" in str(line):
                running = True
    if not fileDownloader.rename_images():
        sys.exit()
    if not fileDownloader.make_zip_file():
        sys.exit()
    # fileDownloader.rename_zip_file('ファイル名')
    fileDownloader.download_file_clear()
