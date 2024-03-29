#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
共通な定数を定義する
"""
__author__ = "Ryosuke Igarashi(HN:igapon)"
__copyright__ = "Copyright (c) 2021 igapon"
__credits__ = ["Ryosuke Igarashi"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "igapon"
__email__ = "igapon@gmail.com"
__status__ = "Development"  # "Prototype" or "Development" or "Production"

from selenium.webdriver.common.by import By

msg_error_exit = 'エラー終了します。'
# chromeなら、拡張機能のコンソールに「navigator.userAgent;」と入力して確認する
HEADERS_DIC = {
    "User-Agent":
#    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
DEFAULT_TARGET_URL = 'https://www.hot-ishikawa.jp/photo/'

RESULT_FILE_PATH = './result.txt'  # タイトルと、ダウンロードするファイルのURLの列挙を書き込むファイル
OUTPUT_FOLDER_PATH = './folder01'  # ダウンロードしたファイルの保存パス

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

img_title_css = 'h2.title'
img_css_select = ['div.thumb-container > a', '#image-container > a > img']
img_attr = ['href', 'src']

# img_css_select = 'html body div .content a'
# img_attr = 'href'

# img_css_select = 'html body main noscript img.vimg'
# img_attr = 'src'

# img_css_select = ['html body div .photoItem img']
# img_attr = ['src']

# img_css_select = 'html body article noscript img'
# img_attr = 'src'

SELECTORS = {
    'title_jp': [(By.XPATH,
                  '//div/div/div/h2',  # //*[@id="info"]/h2
                  lambda el: el.text),
                 ],
    'title_en': [(By.XPATH,
                  '//div/div/div/h1',  # //*[@id="info"]/h1
                  lambda el: el.text),
                 ],
    'image_url': [(By.XPATH,
                   '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
                   lambda el: el.get_attribute("href")),
                  (By.XPATH,
                   '//*[@id="image-container"]/a/img',
                   lambda el: el.get_attribute("src")),
                  ],
    # 'image_urls': [(By.XPATH,
    #                 '//*[@id="thumbnail-container"]/div/div/a',
    #                 lambda el: el.get_attribute("href")),
    #                (By.XPATH,
    #                 '//*[@id="image-container"]/a/img',
    #                 lambda el: el.get_attribute("src")),
    #                ],
}
