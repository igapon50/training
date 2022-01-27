#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード
"""
# local source
# from const import *
# from func import *
from crawling import *

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
#    crawling = Crawling(target_url, img_css_select, img_attr)  # 'img.vimg[src*="jpg"]'
    crawling = Crawling(target_url, 'img.vimg[src*="jpg"]', img_attr)  #
    crawling.save_text(RESULT_FILE_PATH)
    value_objects = crawling.get_value_objects()
    crawling.save_pickle(RESULT_FILE_PATH + '1.pkl')
    crawling.load_pickle(RESULT_FILE_PATH + '1.pkl')
    crawling.save_text(RESULT_FILE_PATH + '1.txt')
    crawling2 = Crawling(value_objects)
    crawling2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    crawling2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    crawling2.save_text(RESULT_FILE_PATH + '2.txt')
    crawling2.load_text(RESULT_FILE_PATH + '2.txt')
    crawling2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    crawling2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    crawling2.save_text(RESULT_FILE_PATH + '3.txt')
