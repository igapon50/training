#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Webサイトから画像のURLリストを作ってクリップボードにコピーし、ファイルにも保存する
"""
# local source
from const import *
from func import *
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
    scraping = Scraping(target_url, img_css_select, img_attr)
    if not scraping:
        print(msg_error_exit)
        sys.exit(scraping)
    scraping.save_text(RESULT_FILE_PATH + '1.txt')
    scraping.save_pickle(RESULT_FILE_PATH + '1.pkl')
    file_url_list = scraping.get_image_list()
    title = scraping.get_title()
    scraping.clip_copy()

    # ファイルのダウンロード
    print('タイトルとURLリストをクリップボードにコピーし、ファイルに保存済み')
    print('irvineにペーストして、ダウンロード完了まで待つ')
    print('ファイルのURLリストを編集すれば、名前の付け直しと圧縮するファイルを調整可能')
    print(title)
# os.system('PAUSE')
