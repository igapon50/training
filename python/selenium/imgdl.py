#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる
"""
# local source
from func import *
from python.Web_scraping.func import *
from python.Web_scraping.scraping_requests import ScrapingRequests
from python.Web_scraping.downloading import Downloading

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
    scraping_requests = ScrapingRequests(target_url, img_css_select, img_attr, img_title_css)
    if not scraping_requests:
        print(msg_error_exit)
        sys.exit()
    scraping_requests.save_text(RESULT_FILE_PATH + '1.txt')
    scraping_requests.save_pickle(RESULT_FILE_PATH + '1.pkl')
    file_url_list = scraping_requests.get_image_list()
    title = scraping_requests.get_title()
    # ダウンロードを開始する
    downloading = Downloading(file_url_list, folder_path)
    # 画像ファイルのダウンロード
    downloading.download()
    # ダウンロードファイルを変名する(ナンバリング)
    if not downloading.rename_images():
        # ダウンロードされていないファイルがあった
        print(msg_error_exit)
        sys.exit()
    # 圧縮ファイル作成
    downloading.make_zip_file()
    # 圧縮ファイル名付け直し
    downloading.rename_zip_file(title)
    # ファイルの削除
    downloading.download_file_clear()
