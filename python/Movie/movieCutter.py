#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file movieCutter.py
# @version 1.1.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/12/19
# @brief 動画から音声のある部分だけ切り出す。
# @details 動画から音声のある部分だけ切り出す。
# @warning
# @note
import sys
import pyperclip
from movieHelper import MovieHelper

if __name__ == '__main__':  # インポート時には動かない
    target_file_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/JPIC3316.MOV'
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のファイルパス
        target_file_path = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードから得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            target_file_path = paste_str
    # クリップボードが空なら、デフォルトを用いる
    else:
        print('引数が不正です。')
        sys.exit(False)
    print(target_file_path)

    # 無音部分をカットした動画分割して、文字起こし
    mh = MovieHelper(target_file_path)
    movie_list = mh.movie_dividing()
    for movie in movie_list:
        mh_dividing = MovieHelper(movie)
        mh_dividing.mov_to_text()
