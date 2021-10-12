#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file const.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/26
# @brief 共通な定数を定義する
# @details 共通な定数を定義する
# @warning 
# @note 

__author__ = "Ryosuke Igarashi(HN:igapon)"
__copyright__ = "Copyright (c) 2021 igapon"
__credits__ = ["Ryosuke Igarashi"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "igapon"
__email__ = "igapon@gmail.com"
__status__ = "Development"  # "Prototype" or "Development" or "Production"

msg_error_exit = 'エラー終了します。'
HEADERS_DIC = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"}
DEFAULT_TARGET_URL = 'https://www.hot-ishikawa.jp/photo/'

RESULT_FILE_PATH = './result.txt'  # タイトルと、ダウンロードするファイルのURLの列挙を書き込むファイル
OUTPUT_FOLDER_PATH = '.\\folder01'  # ダウンロードしたファイルの保存パス

# img_css_select = 'html body section.entry-content img'
# img_attr = 'src'

# img_css_select = 'html body main div.content img.content-img'
# img_attr = 'src'

# img_css_select = 'html body section.entry-content img.alignnone'
# img_attr = 'src'

# img_css_select = 'html body section.entry-content img'
# img_attr = 'src'

# img_css_select = 'img[data-src]'
# img_attr = 'data-src'

# img_css_select = 'html body div.kijibox p a'
# img_attr = 'href'

# img_css_select = 'html body noscript img.list-img'
# img_attr = 'src'

# img_css_select = 'html body div .content a'
# img_attr = 'href'

# img_css_select = 'html body main noscript img.vimg'
# img_attr = 'src'

img_css_select = 'html body div .photoItem img'
img_attr = 'src'

# img_css_select = 'html body article noscript img'
# img_attr = 'src'
