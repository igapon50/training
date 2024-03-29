#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
imglistファイルを読み込んでクリップボードにコピーする
"""
# local source
from const import *
from func import *
from scraping_requests import *

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
        # 引数がなければデフォルト、デフォルトがなければクリップボードからファイルパスを得る
        if 0 == len(imglist_filepath):
            paste_url = pyperclip.paste()
            parse = urlparse(paste_url)
            if 0 < len(parse.scheme):
                imglist_filepath = paste_url
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit()
    print(imglist_filepath)

    # ファイルのURLリストを作成
    scraping_requests = ScrapingRequests()
    if not scraping_requests:
        print(msg_error_exit)
        sys.exit(scraping_requests)
    scraping_requests.load_text(RESULT_FILE_PATH + '1.txt')
    scraping_requests.clip_copy()

    # ファイルのダウンロード
    print('タイトルとURLリストをクリップボードにコピーしました。')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
# os.system('PAUSE')
