#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
動画から音声のある部分だけ切り出し、mltに二つトラックを追加し、一つ目に動画を追加、二つ目に文字起こしした字幕を追加する
"""
import os
import sys
import pyperclip
from movieHelper import MovieHelper
from mltHelper import MltHelper

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
        sys.exit()
    print(target_file_path)

    mlt_file_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート.mlt'
    target_folder = os.path.dirname(mlt_file_path)
    target_mlt_basename = os.path.basename(mlt_file_path)
    target_mlt_file_name = os.path.splitext(target_mlt_basename)[0]
    target_mlt_file_ext = os.path.splitext(target_mlt_basename)[1]
    create_mlt_path = os.path.join(target_folder, target_mlt_file_name + '_addMov2mlt' + target_mlt_file_ext)
    # mltヘルパー生成
    app = MltHelper(mlt_file_path)
    # トラックを二つ追加
    playlist_id_V2 = app.add_track('V2')
    playlist_id_V3 = app.add_track('V3')
    # 動画ヘルパー生成
    mh = MovieHelper(target_file_path)
    # 無音部分をカットした動画に分割する
    movie_list = mh.movie_dividing()
    # 動画をプレイリストに追加
    app.add_movies('main_bin', movie_list)
    # 動画をタイムラインに追加
    app.add_movies(playlist_id_V2, movie_list)
    # 字幕をプレイリストに追加
    app.add_subtitles('main_bin', movie_list)
    # 字幕をタイムラインに追加
    app.add_subtitles(playlist_id_V3, movie_list)
    # mltの保存
    app.save_xml(create_mlt_path)
