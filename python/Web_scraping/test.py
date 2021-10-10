#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file test.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/10/10
# @brief 検証コード
# @details
# @warning 
# @note 

# local source
# from const import *
# from func import *
from xmlScraping import *

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
#    xmlScraping = XmlScraping(target_url, img_css_select, img_attr)  # 'img.vimg[src*="jpg"]'
    xmlScraping = XmlScraping(target_url, 'img.vimg[src*="jpg"]', img_attr)  #
    xmlScraping.save_text(RESULT_FILE_PATH)
    value_objects = xmlScraping.get_value_objects()
    xmlScraping.save_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.load_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.save_text(RESULT_FILE_PATH + '1.txt')
    xmlScraping2 = XmlScraping(None, None, None, value_objects)
    xmlScraping2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    xmlScraping2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    xmlScraping2.save_text(RESULT_FILE_PATH + '2.txt')
    xmlScraping2.load_text(RESULT_FILE_PATH + '2.txt')
    xmlScraping2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    xmlScraping2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    xmlScraping2.save_text(RESULT_FILE_PATH + '3.txt')
