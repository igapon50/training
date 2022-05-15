#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imglistファイルからファイル名リストを作り、ダウンロードされていたらzipファイルにまとめる
"""
# local source
from const import *
from func import *
from scraping import *
from downloading import *

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
    scraping = Scraping()
    if not scraping:
        print(msg_error_exit)
        sys.exit(scraping)
    scraping.load_text(RESULT_FILE_PATH + '1.txt')
    file_url_list = scraping.get_image_list()
    title = scraping.get_title()
    # ダウンロードを開始する
    downloading = Downloading(file_url_list, folder_path)

    # ファイルのダウンロード
    print('ファイルリストを読み込み済み、irvineでダウンロード完了まで待つ')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
    print(title)
    os.system('PAUSE')

    # ダウンロードファイルを変名する(ナンバリング)
    if not downloading.rename_images():
        # ダウンロードされていないファイルがあった
        print(msg_error_exit)
        sys.exit(1)
    # 圧縮ファイル作成
    downloading.make_zip_file()
    # 圧縮ファイル名付け直し
    downloading.rename_zip_file(title)
    # ファイルの削除
    downloading.download_file_clear()
