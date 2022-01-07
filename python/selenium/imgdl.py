#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる
"""
# local source
from func import *
from python.Web_scraping.func import *
from python.Web_scraping.crawling import Crawling
from python.Web_scraping.scraping import Scraping

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
    file_url_list = []
    title_list = []
    ret = HTML2imglist_SeleniumFireFox(target_url, imglist_filepath, title_list, file_url_list)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # ファイルのURLリストを作成
    crawling = Crawling(target_url, img_css_select, img_attr)
    if not crawling:
        print(msg_error_exit)
        sys.exit()
    crawling.save_text(RESULT_FILE_PATH + '1.txt')
    crawling.save_pickle(RESULT_FILE_PATH + '1.pkl')
    # target_data = crawling.get_value_objects()
    file_url_list = crawling.get_image_list()
    title = crawling.get_title()
    # スクレイピングを開始する
    scraping = Scraping(file_url_list, folder_path)
    # 画像ファイルのダウンロード
    scraping.download()
    # ダウンロードファイルを変名する(ナンバリング)
    if not scraping.rename_images():
        # ダウンロードされていないファイルがあった
        print(msg_error_exit)
        sys.exit()
    # 圧縮ファイル作成
    scraping.make_zip_file()
    # 圧縮ファイル名付け直し
    scraping.rename_zip_file(title)
    # ファイルの削除
    scraping.download_file_clear()
