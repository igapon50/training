#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imglistファイルからファイル名リストを作り、ダウンロードする
"""
# local source
from const import *
from func import *
from crawling import *
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

    # クローリングを開始する
    crawling = Crawling()
    if not crawling:
        print(msg_error_exit)
        sys.exit(crawling)
    # クローリング情報をロードする
    crawling.load_text(RESULT_FILE_PATH + '1.txt')
    file_url_list = crawling.get_image_list()

    # スクレイピングを開始する
    scraping = Downloading(file_url_list, folder_path)
    # 画像ファイルのダウンロード
    scraping.download()