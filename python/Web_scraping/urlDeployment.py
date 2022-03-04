#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数値URLを展開して、リストにして、ファイルに保存する
    http:/hoge/10.jpg
    ↓
    http:/hoge/1.jpg ～ http:/hoge/10.jpg
"""
import urllib.parse
# from urllib.parse import urlparse  # URLパーサー
# from urllib.parse import urljoin  # URL結合
import sys
import pyperclip


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    target_url = None
    folder_path = None
    parse = None
    url_list = []
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        paste_str = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit(1)
    # URLかチェックする
    if 0 < len(paste_str):
        parse = urllib.parse.urlparse(paste_str)
        if 0 < len(parse.scheme):
            target_url = paste_str
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
            if base_name.isdecimal():
                count = int(base_name)
                for i in range(count):
                    url_list.append(urllib.parse.urlunparse((parse.scheme,
                                                             parse.netloc,
                                                             path_before_name + str(i + 1) + extend_name,
                                                             parse.params,
                                                             parse.query,
                                                             parse.fragment)))
            else:
                print('引数が不正です。数値ではない？')
                sys.exit(1)
    print(target_url)
    print(url_list)

    with open('./result_list.txt', 'w', encoding='utf-8') as work_file:
        buff = ''
        for absolute_path in url_list:
            buff += absolute_path + '\n'  # 画像URL追加
        work_file.write(buff)  # ファイルへの保存
