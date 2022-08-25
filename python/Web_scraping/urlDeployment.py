#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
引数URLのサイトにアクセスして、タイトルと最終画像URLをスクレイピングする。
最終画像URLの数字を展開した、URLリストをファイルに保存して、irvineに渡す。
    http:/hoge/10.jpg
    ↓
    http:/hoge/1.jpg ～ http:/hoge/10.jpg
irvineが起動してダウンロードが開始されるので、ダウンロードが終わったらirvineを手動で終了する。
irvineが終了したらダウンロードファイルをチェックする。
失敗している時は、拡張子を変えて、ファイルに保存して、irvineに渡す。
成功している時は、リネームしてzipして削除する。
"""
import urllib.parse
import subprocess
from downloading import *
import sys
from chrome import *
from irvineHelper import *

# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    folder_path = OUTPUT_FOLDER_PATH
    url_list: list = []
    main_title = '[] a'
    list_file_path = './irvine_download_list.txt'
    # 引数チェック
    if 3 == len(sys.argv):
        # Pythonに以下の3つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        # 2.対象のタイトル(後にファイル名にする)
        paste_str = sys.argv[1]
        main_title = sys.argv[2]
    elif 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        paste_str = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
    else:
        print('引数が不正です。')
        sys.exit(1)
    # URLかチェックする
    if 0 == len(paste_str):
        print('引数が不正です。空です。')
        sys.exit(1)
    parse = urlparse(paste_str)
    if 0 == len(parse.scheme):
        print('引数が不正です。URLではない？')
        sys.exit(1)
    if parse.path[-4:] == '.jpg' or parse.path[-4:] == '.png':
        main_image_url = paste_str
    else:
        main_url = paste_str
        main_selectors = {
            'title': [(By.XPATH,
                       '//div/div/div/h2',  # //*[@id="info"]/h2
                       lambda elem: elem.text),
                      ],
            'image_url': [(By.XPATH,
                           '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
                           lambda elem: elem.get_attribute("href")),
                          (By.XPATH,
                           '//*[@id="image-container"]/a/img',
                           lambda elem: elem.get_attribute("src")),
                          ],
        }
        driver = SeleniumDriver(main_url, main_selectors)
        main_title = driver.get_title()
        main_image_url = driver.get_image_url()
    print(main_title)
    print(main_image_url)

    if 0 == len(main_image_url):
        print('引数が不正です。空です。')
        sys.exit(1)
    parse = urllib.parse.urlparse(main_image_url)
    if 0 == len(parse.scheme):
        print('引数が不正です。URLではない？')
        sys.exit(1)
    # pathを/前後で分ける
    path_before_name = parse.path[:parse.path.rfind('/') + 1]
    path_after_name = parse.path[parse.path.rfind('/') + 1:]
    print(path_before_name)
    print(path_after_name)
    # path_after_nameを.前後で分ける
    base_name = path_after_name[:path_after_name.rfind('.')]
    extend_name = path_after_name[path_after_name.rfind('.'):]
    print(base_name)
    print(extend_name)
    if not base_name.isdecimal():
        print('引数が不正です。数値ではない？')
        sys.exit(1)
    count = int(base_name)
    for i in range(count):
        url_list.append(urllib.parse.urlunparse((parse.scheme,
                                                 parse.netloc,
                                                 path_before_name + str(i + 1) + extend_name,
                                                 parse.params,
                                                 parse.query,
                                                 parse.fragment)))
    print(url_list)

    with open(list_file_path, 'w', encoding='utf-8') as work_file:
        buff = ''
        for absolute_path in url_list:
            buff += absolute_path + '\n'  # 画像URL追加
        work_file.write(buff)  # ファイルへの保存
    fileDownloader = Downloading(url_list, folder_path)
    # irvineを起動して、ダウンロードする
    irvine = IrvineHelper(list_file_path)
    irvine.download()

    if not fileDownloader.is_src_exist():
        # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
        fileDownloader.rename_ext_shift()
        # ダウンロードリストを作り直す
        with open(list_file_path, 'w', encoding='utf-8') as work_file:
            buff = ''
            for absolute_path in fileDownloader.image_list:
                buff += absolute_path + '\n'  # 画像URL追加
            work_file.write(buff)  # ファイルへの保存
        fileDownloader = Downloading(fileDownloader.image_list, folder_path)
        # ダウンロードしなおす
        irvine = IrvineHelper(list_file_path)
        irvine.download()
    if not fileDownloader.rename_images():
        sys.exit()
    if not fileDownloader.make_zip_file():
        sys.exit()
    fileDownloader.rename_zip_file(main_title)
    fileDownloader.download_file_clear()
