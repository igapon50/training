#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる
"""
# local source
from const import *
from func import *
from crawling import *
from scraping import *

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
        sys.exit()
    print(target_url)

    # ファイルのURLリストを作成
    crawling = Crawling(target_url, img_css_select, img_attr)
    if not crawling:
        print(msg_error_exit)
        sys.exit(1)
    crawling.save_text(RESULT_FILE_PATH + '1.txt')
    crawling.save_pickle(RESULT_FILE_PATH + '1.pkl')
    # target_data = crawling.get_value_objects()
    file_url_list = crawling.get_image_list()
    title = crawling.get_title()

    fileDownloader = Scraping(file_url_list, folder_path)
    fileDownloader.download()
    if not fileDownloader.rename_images():
        print(msg_error_exit)
        sys.exit(1)

    # 圧縮ファイル作成
    ret = makezipfile(folder_path + '.zip', fileDownloader.get_dst_file_list())
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
