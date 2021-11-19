#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file movieCutter.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/11/13
# @brief 動画編集shotcutのプロジェクトファイルを編集するヘルパー
# @details
# @warning
# @note
import datetime
import os
import re
import sys
import pyperclip
import xmltodict
import collections
import ffmpeg
import hashlib


##
# @brief 相対パスが指定されたら絶対パスを返す
# @details
# @warning
# @note
def get_abs_path(path: 'str 変換対象パス'):
    if path is not None:
        if os.path.isabs(path):
            target_path = path
        else:
            target_path = os.path.abspath(path)
        return target_path

##
# @brief 動画編集shotcutのプロジェクトファイルを編集するヘルパー
# @details 内部では辞書型でデータを保持する
# @warning
# @note


class ShotcutHelper:
    playlist_name: str = 'playlist'
    producer_name: str = 'producer'
    property_name: str = 'property'

    # コンストラクタ
    def __init__(self,
                 mlt_path: 'str shotcutのプロジェクトファイルパス',
                 ):
        self.mlt_path = None
        self.xml_data = None
        self.dict_data = None
        self.playlist_entry = []
        if mlt_path is None:
            print('プロジェクトパスがNoneです')
            sys.exit(1)
        self.mlt_path = get_abs_path(mlt_path)
        self.load_xml()

    # プロジェクトファイルをロードする
    def load_xml(self):
        if not os.path.isfile(self.mlt_path):
            print('プロジェクトファイルがありません')
            sys.exit(1)
        with open(self.mlt_path, encoding='utf-8') as fp:
            self.xml_data = fp.read()
        # xml → dict
        self.dict_data = xmltodict.parse(self.xml_data)
        # プレイリストのロード
        playlist_main_bin = self.dict_data.get('mlt').get('playlist')[0]
        if playlist_main_bin.get('@id') != 'main_bin':
            print('プロジェクトファイルにmain_binがありません')
            sys.exit(1)
        for index in range(len(playlist_main_bin.get('entry'))):
            element = playlist_main_bin.get('entry')[index]
            key = '@' + self.producer_name
            name = element[key]
            count = len(self.producer_name)
            if len(name) < count:
                print('プロジェクトファイルのプレイリストentryのプレフィックスがproducerではない')
                sys.exit(1)
            number = name[count:]
            if not number.isdecimal():
                print('プロジェクトファイルのプレイリストentryに追加するindexを決定できなかった')
                sys.exit(1)
            self.playlist_entry.append(int(number))

    # shotcutプロジェクトファイルを保存する（ファイルがある場合は保存しない）
    def save_xml(self,
                 save_path: 'str xmlで保存するファイルパス',
                 ):
        if save_path is None:
            print('引数が空です')
            sys.exit(1)
        path = get_abs_path(save_path)
        if os.path.isfile(path):
            print('ファイルが存在します。xmlファイル保存を中止します。')
            sys.exit(1)
        with open(path, mode='w', encoding='utf-8') as fp:
            # dict → xml , xmlの整形 , xmlの保存
            self.xml_data = xmltodict.unparse(self.dict_data, pretty=True)
            fp.write(self.xml_data)

    # xml_dataに動画を追加する
    def add_movies(self,
                   movies: 'list 追加する動画ファイルのリスト'
                   ):
        if movies is None:
            print('引数が空です')
            sys.exit(1)
        for movie in movies:
            path = get_abs_path(movie)
            if not os.path.isfile(path):
                print('ファイルが見つかりません。処理を中止します。')
                sys.exit(1)
            self.add_item(path)

    # プレイリストにitemを増やす(mltファイルのplaylistタグid=main_bin)
    def add_item(self,
                 movie: 'str 動画のファイルパス',
                 ):
        # 動画の情報を集める
        video_info = ffmpeg.probe(movie)
        creation_time = video_info.get('format').get('tags').get('creation_time')
        start_time = video_info.get('format').get('start_time')
        time_s = int(float(start_time))
        time_m = int((float(start_time) - float(time_s)) * 1000000)
        dt = datetime.time(hour=0, minute=0, second=time_s, microsecond=time_m, tzinfo=None)
        in_time = dt.strftime('%H:%M:%S.%f')[:12]
        end_time = video_info.get('format').get('duration')
        time_s = int(float(end_time))
        time_m = int((float(end_time) - float(time_s)) * 1000000)
        dt = datetime.time(hour=0, minute=0, second=time_s, microsecond=time_m, tzinfo=None)
        out_time = dt.strftime('%H:%M:%S.%f')[:12]
        # ハッシュの計算
        algo = 'md5'
        hash_object = hashlib.new(algo)
        hash_size = hash_object.block_size * 0x800
        with open(movie, 'rb') as fp:
            binary_data = fp.read(hash_size)
            while binary_data:
                hash_object.update(binary_data)
                binary_data = fp.read(hash_size)
        shotcut_hash = hash_object.hexdigest()

        # プレイリストの空き番号を調べる
        index = self.get_next_index_playlist_entry()

        # プレイリストを追加する
        playlist_main_bin = self.dict_data.get('mlt').get('playlist')[0]
        if playlist_main_bin.get('@id') != 'main_bin':
            print('プロジェクトファイルにmain_binがありません')
            sys.exit(1)
        od = collections.OrderedDict()
        od['@' + self.producer_name] = self.producer_name + str(index)
        od['@in'] = in_time
        od['@out'] = out_time
        playlist_main_bin.get('entry').append(od)

        # producerを追加する
        mlt_dict = self.dict_data.get('mlt').get(self.producer_name)
        od = collections.OrderedDict()
        od['@id'] = self.producer_name + str(index)
        od['@in'] = in_time
        od['@out'] = out_time
        od[self.property_name] = []
        mlt_dict.append(od)
        producer_list = [collections.OrderedDict([('@name', 'length'), ('#text', out_time)]),
                         collections.OrderedDict([('@name', 'eof'), ('#text', 'pause')]),
                         collections.OrderedDict([('@name', 'resource'), ('#text', movie)]),
                         collections.OrderedDict([('@name', 'audio_index'), ('#text', '-1')]),
                         collections.OrderedDict([('@name', 'video_index'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mute_on_pause'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'avformat-novalidate')]),
                         collections.OrderedDict([('@name', 'seekable'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'aspect_ratio'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'global_feed'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'xml'), ('#text', 'was here')]),
                         collections.OrderedDict([('@name', 'shotcut:hash'), ('#text', shotcut_hash)]),
                         collections.OrderedDict([('@name', 'shotcut:caption'), ('#text', os.path.basename(movie))])]
        last_key = next(reversed(mlt_dict), None)
        for od in producer_list:
            last_key[self.property_name].append(od)

        # 追加した動画の管理番号を登録する
        self.playlist_entry.append(index)
        return

    # リストに無い次の(アルファベット+十進数値な)名前のindexを返す
    def get_next_index_playlist_entry(self):
        for index in range(len(self.playlist_entry)):
            if not index in self.playlist_entry:
                return index
        return index + 1

# windowsでMD5ハッシュを出力する方法
# > certutil -hashfile C:\Git\igapon50\traning\python\Movie\せんちゃんネル\mov\BPUB2392.MP4 MD5
# shotcutのmltプロジェクトファイルフォーマット
# https://shotcut.org/notes/mltxml-annotations/
# < producer id = "producer0" in = "00:00:00.000" out = "00:00:03.448" >
#   < property name = "length" > 00:00: 03.498 < / property >
#   < property name = "eof" > pause < / property >
#   < property name = "resource" > mov / BPUB2392.MP4 < / property >
#   < property name = "audio_index" > -1 < / property >
#   < property name = "video_index" > 0 < / property >
#   < property name = "mute_on_pause" > 0 < / property >
#   < property name = "mlt_service" > avformat - novalidate < / property >
#   < property name = "seekable" > 1 < / property >
#   < property name = "aspect_ratio" > 1 < / property >
#   < property name = "creation_time" > 2020 - 10 - 10 T06: 41:41 < / property >
#   < property name = "global_feed" > 1 < / property >
#   < property name = "xml" > was here < / property >
#   < property name = "shotcut:hash" > b296c075554cbbadaacf3110a66ffdd9 < / property >
# < / producer >
# < playlist id = "main_bin" >
#   < property name = "xml_retain" > 1 < / property >
#   < entry producer = "producer1" in = "00:00:00.000" out = "00:00:18.140" / >
#   < entry producer = "producer2" in = "00:00:00.000" out = "00:00:59.968" / >
#   < entry producer = "producer0" in = "00:00:00.000" out = "00:00:03.448" / >
# < / playlist >
    # 作成中 タイムラインにトラックを増やす(mltファイルのplaylistタグid=playlist0..)
    def add_trac(self,
                     name: 'str トラック名'
                     ):
        return name

    # 作成中 タイムラインにshotを追加する
    def add_producer(self,
                     movie: 'str 動画のファイルパス'
                     ):
        return movie

    # 作成中 トランジション(フェード、ワイプ、クロスフェード、ミックス)
    def add_tractor(self,
                    movie: 'str 動画のファイルパス'
                    ):
        return movie


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    target_file_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/テンプレート.mlt'
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
    shotcut1 = ShotcutHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/テンプレート.mlt')
    shotcut2 = ShotcutHelper('./せんちゃんネル/テンプレート.mlt')
    movies = [
        './せんちゃんネル/mov/BPUB2392.MP4',
        './せんちゃんネル/20210306/JGWU8992.MOV',
    ]
    shotcut2.add_movies(movies)
    shotcut2.save_xml('C:/Git/igapon50/traning/python/Movie/test.mlt')
