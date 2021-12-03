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
import sys
import pyperclip
import xmltodict
import collections
import ffmpeg
import hashlib
from dataclasses import dataclass


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


# item(動画)のハッシュを計算して返す
# 参考)windowsでMD5ハッシュを出力するコマンド例
# > certutil -hashfile C:\Git\igapon50\traning\python\Movie\せんちゃんネル\mov\BPUB2392.MP4 MD5
def get_md5(movie: 'str ハッシュを計算するファイルパス'):
    algo = 'md5'
    hash_object = hashlib.new(algo)
    hash_size = hash_object.block_size * 0x800
    with open(movie, 'rb') as fp:
        binary_data = fp.read(hash_size)
        while binary_data:
            hash_object.update(binary_data)
            binary_data = fp.read(hash_size)
    return hash_object.hexdigest()


# リストに無い次の(アルファベット+十進数値な)名前のindex(管理番号)を返す
def get_next_index_entry(entry: 'list 対象の管理リスト'):
    ret_value = 0
    entry_length = len(entry)
    for index in range(entry_length):
        if index not in entry:
            return index
        ret_value = index + 1
    return ret_value


##
# @brief Value Objects
# @details item(動画)の値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class ItemValue:
    movie: str = None
    index: int = 0
    shotcut_hash: str = None
    in_time: str = None
    out_time: str = None
    creation_time: str = None

    # 完全コンストラクタパターン
    def __init__(self,
                 movie: 'str 動画のファイルパス',
                 index: 'int 登録するインデックス番号',
                 shotcut_hash: 'str 動画のハッシュ',
                 ):
        if movie is None or shotcut_hash is None:
            print('引数が不正です。')
            sys.exit(1)
        object.__setattr__(self, "movie", movie)
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "shotcut_hash", shotcut_hash)
        # item(動画)の情報を集める
        video_info = ffmpeg.probe(movie)
        creation_str = video_info.get('format').get('tags').get('creation_time')
        date_dt = datetime.datetime.strptime(creation_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        creation_time = date_dt.strftime('%Y-%m-%dT%H:%M:%S')
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
        object.__setattr__(self, "in_time", in_time)
        object.__setattr__(self, "out_time", out_time)
        object.__setattr__(self, "creation_time", creation_time)


##
# @brief 動画編集shotcutのプロジェクトファイルを編集するヘルパー
# @details 内部では辞書型でデータを保持する
# @warning
# @note
# shotcutのmltプロジェクトファイルフォーマット
# https://shotcut.org/notes/mltxml-annotations/


class ShotcutHelper:
    app_name: str = 'shotcut'
    mlt_name: str = 'mlt'
    tractor_name: str = 'tractor'
    track_name: str = 'track'
    transition_name: str = 'transition'
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
        self.producer_entry = []
        self.transition_entry = []
        if mlt_path is None:
            print('プロジェクトパスがNoneです')
            sys.exit(1)
        self.mlt_path = get_abs_path(mlt_path)
        self.load_xml()

    # playlist_entryのロード
    def __load_playlist(self):
        tractor_root = self.dict_data.get(self.mlt_name).get(self.tractor_name)
        count = len(self.app_name)
        if tractor_root.get('@title')[:count].lower() != self.app_name.lower():
            print('プロジェクトファイルにtractorがありません')
            sys.exit(1)
        track_root = tractor_root.get(self.track_name)
        for index in range(len(track_root)):
            element = track_root[index]
            key = '@' + self.producer_name
            name = element[key]
            count = len(self.producer_name)
            if self.playlist_name != name[:count]:
                continue
            number = name[count:]
            if not number.isdecimal():
                print('playlist_entryに追加するindexを決定できなかった')
                sys.exit(1)
            self.__register_index_playlist_entry(int(number))

    # producer_entryのロード
    def __load_producer(self):
        playlist_main_bin = self.dict_data.get(self.mlt_name).get(self.playlist_name)[0]
        if playlist_main_bin.get('@id') != 'main_bin':
            print('プロジェクトファイルにmain_binがありません')
            sys.exit(1)
        for index in range(len(playlist_main_bin.get('entry'))):
            element = playlist_main_bin.get('entry')[index]
            key = '@' + self.producer_name
            name = element[key]
            count = len(self.producer_name)
            if len(name) < count:
                print('producer_entryのプレフィックスがproducerではない')
                sys.exit(1)
            number = name[count:]
            if not number.isdecimal():
                print('producer_entryに追加するindexを決定できなかった')
                sys.exit(1)
            self.__register_index_producer_entry(int(number))

    # transition_entryのロード
    def __load_transition(self):
        tractor_root = self.dict_data.get(self.mlt_name).get(self.tractor_name)
        count = len(self.app_name)
        if tractor_root.get('@title')[:count].lower() != self.app_name.lower():
            print('プロジェクトファイルにtractorがありません')
            sys.exit(1)
        transition_root = tractor_root.get(self.transition_name)
        for index in range(len(transition_root)):
            element = transition_root[index]
            key = '@id'
            name = element[key]
            count = len(self.transition_name)
            if self.transition_name != name[:count]:
                continue
            number = name[count:]
            if not number.isdecimal():
                print('transition_entryに追加するindexを決定できなかった')
                sys.exit(1)
            self.__register_index_transition_entry(int(number))

    # プロジェクトファイルをロードする
    def load_xml(self):
        if not os.path.isfile(self.mlt_path):
            print('プロジェクトファイルがありません')
            sys.exit(1)
        with open(self.mlt_path, encoding='utf-8') as fp:
            self.xml_data = fp.read()
        # xml → dict
        self.dict_data = xmltodict.parse(self.xml_data)
        # トラックのロード
        self.__load_playlist()
        # プレイリストのロード
        self.__load_producer()
        # トランジションのロード
        self.__load_transition()

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

    def __get_next_index_playlist_entry(self):
        return get_next_index_entry(self.playlist_entry)

    def __get_next_index_producer_entry(self):
        return get_next_index_entry(self.producer_entry)

    def __get_next_index_transition_entry(self):
        return get_next_index_entry(self.transition_entry)

    # 追加したtrackの管理番号を登録する
    def __register_index_playlist_entry(self,
                                        index: 'int 登録する管理番号',
                                        ):
        self.playlist_entry.append(index)

    # 追加したitem(動画)の管理番号を登録する
    def __register_index_producer_entry(self,
                                        index: 'int 登録する管理番号',
                                        ):
        self.producer_entry.append(index)

    # 追加したitem(動画)の管理番号を登録する
    def __register_index_transition_entry(self,
                                          index: 'int 登録する管理番号',
                                          ):
        self.transition_entry.append(index)

    # playlistにitem(動画)を追加する
    def __add_item_to_playlist(self,
                               item_value: 'ItemValue item(動画)値クラス',
                               ):
        playlist_main_bin = self.dict_data.get(self.mlt_name).get(self.playlist_name)[0]
        if playlist_main_bin.get('@id') != 'main_bin':
            print('プロジェクトファイルにmain_binがありません')
            sys.exit(1)
        od = collections.OrderedDict([('@' + self.producer_name, self.producer_name + str(item_value.index)),
                                      ('@in', item_value.in_time),
                                      ('@out', item_value.out_time)])
        playlist_main_bin.get('entry').append(od)

    # producerにitem(動画)を追加する
    def __add_item_to_producer(self,
                               item_value: 'ItemValue item(動画)値クラス',
                               ):
        mlt_dict = self.dict_data.get('mlt').get(self.producer_name)
        od = collections.OrderedDict([('@id', self.producer_name + str(item_value.index)),
                                      ('@in', item_value.in_time),
                                      ('@out', item_value.out_time),
                                      (self.property_name, [])])
        mlt_dict.append(od)
        property_list = [collections.OrderedDict([('@name', 'length'), ('#text', item_value.out_time)]),
                         collections.OrderedDict([('@name', 'eof'), ('#text', 'pause')]),
                         collections.OrderedDict([('@name', 'resource'), ('#text', item_value.movie)]),
                         collections.OrderedDict([('@name', 'audio_index'), ('#text', '-1')]),
                         collections.OrderedDict([('@name', 'video_index'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mute_on_pause'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'avformat-novalidate')]),
                         collections.OrderedDict([('@name', 'seekable'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'aspect_ratio'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'creation_time'), ('#text', item_value.creation_time)]),
                         collections.OrderedDict([('@name', 'global_feed'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'xml'), ('#text', 'was here')]),
                         collections.OrderedDict([('@name', 'shotcut:hash'), ('#text', item_value.shotcut_hash)]),
                         collections.OrderedDict([('@name', 'shotcut:caption'),
                                                  ('#text', os.path.basename(item_value.movie))])]
        last_key = next(reversed(mlt_dict), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)

    # producerの空き番号を調べて、playlistとproducerにitem(動画)を追加する
    # ※途中で失敗したらロールバックせずに中断
    def add_item(self,
                 movie: 'str 動画のファイルパス',
                 ):
        # item(動画)の空き番号を調べる
        index = self.__get_next_index_producer_entry()
        # item(動画)のハッシュを計算
        shotcut_hash = get_md5(movie)
        # item(動画)の情報を集める
        item_value = ItemValue(movie, index, shotcut_hash)
        # playlistにitem(動画)を追加する
        self.__add_item_to_playlist(item_value)
        # producerにitem(動画)を追加する
        self.__add_item_to_producer(item_value)
        # 追加したitem(動画)の管理番号を登録する
        self.__register_index_producer_entry(index)
        return

    # プレイリストに動画を追加する
    def add_movies(self,
                   movie_list: 'list 追加する動画ファイルのリスト',
                   ):
        if movie_list is None:
            print('引数が空です')
            sys.exit(1)
        for movie in movie_list:
            path = get_abs_path(movie)
            if not os.path.isfile(path):
                print('ファイルが見つかりません。処理を中止します。')
                sys.exit(1)
            self.add_item(path)

# <producer id="producer4" in="00:00:00.000" out="00:00:03.448">
#   <property name="length">00:00:03.500</property>
#   <property name="eof">pause</property>
#   <property name="resource">C:\Git\igapon50\traning\python\Movie\せんちゃんネル\mov\BPUB2392.MP4</property>
#   <property name="audio_index">-1</property>
#   <property name="video_index">0</property>
#   <property name="mute_on_pause">0</property>
#   <property name="mlt_service">avformat-novalidate</property>
#   <property name="seekable">1</property>
#   <property name="aspect_ratio">1</property>
#   <property name="global_feed">1</property>
#   <property name="xml">was here</property>
#   <property name="shotcut:hash">b296c075554cbbadaacf3110a66ffdd9</property>
#   <property name="shotcut:caption">BPUB2392.MP4</property>
# </producer>
# <producer id="producer5" in="00:00:00.000" out="00:00:11.094">
#   <property name="length">00:00:11.148</property>
#   <property name="eof">pause</property>
#   <property name="resource">C:\Git\igapon50\traning\python\Movie\せんちゃんネル\20210306\JGWU8992.MOV</property>
#   <property name="audio_index">-1</property>
#   <property name="video_index">0</property>
#   <property name="mute_on_pause">0</property>
#   <property name="mlt_service">avformat-novalidate</property>
#   <property name="seekable">1</property>
#   <property name="aspect_ratio">1</property>
#   <property name="global_feed">1</property>
#   <property name="xml">was here</property>
#   <property name="shotcut:hash">58ecc0b168240fda90ce17106c5b50c8</property>
#   <property name="shotcut:caption">JGWU8992.MOV</property>
# </producer>
# <playlist id="playlist0">
#   <property name="shotcut:video">1</property>
#   <property name="shotcut:name">V1</property>
#   <entry producer="producer6" in="00:00:00.000" out="00:00:09.045"/>
#   <entry producer="producer11" in="00:00:00.500" out="00:00:10.894"/>
#   <entry producer="producer4" in="00:00:00.000" out="00:00:03.448"/>
#   <entry producer="producer5" in="00:00:00.000" out="00:00:11.094"/>
# </playlist>

    # TODO タイムラインにトラックを増やす(mltファイルのplaylistタグid=playlist0..)
    def add_trac(self,
                 name: 'str トラック名'
                 ):
        return name

# < playlist id = "playlist2" >
#   < property name = "shotcut:video" > 1 < / property >
#   < property name = "shotcut:name" > V2 < / property >
#   < blank length = "00:00:00.050" / >
# < / playlist >
# < tractor id = "tractor6" title = "Shotcut version UNSTABLE-21.02.09" global_feed = "1"
#    in = "00:00:00.000" out = "00:02:44.726" >
#   < property name = "shotcut" > 1 < / property >
#   < property name = "shotcut:projectAudioChannels" > 2 < / property >
#   < property name = "shotcut:projectFolder" > 1 < / property >
#   < property name = "shotcut:scaleFactor" > 0.814792 < / property >
#   < track producer = "background" / >
#   < track producer = "playlist0" / >
#   < track producer = "playlist1" hide = "video" / >
#   < track producer = "playlist2" / >
#   < transition id = "transition12" >
#     < property name = "a_track" > 0 < / property >
#     < property name = "b_track" > 1 < / property >
#     < property name = "mlt_service" > mix < / property >
#     < property name = "always_active" > 1 < / property >
#     < property name = "sum" > 1 < / property >
#   < / transition >
#   < transition id = "transition13" >
#     < property name = "a_track" > 0 < / property >
#     < property name = "b_track" > 1 < / property >
#     < property name = "version" > 0.9 < / property >
#     < property name = "mlt_service" > frei0r.cairoblend < / property >
#     < property name = "threads" > 0 < / property >
#     < property name = "disable" > 1 < / property >
#   < / transition >
#   < transition id = "transition14" >
#     < property name = "a_track" > 0 < / property >
#     < property name = "b_track" > 2 < / property >
#     < property name = "mlt_service" > mix < / property >
#     < property name = "always_active" > 1 < / property >
#     < property name = "sum" > 1 < / property >
#   < / transition >
#   < transition id = "transition0" >
#     < property name = "a_track" > 0 < / property >
#     < property name = "b_track" > 3 < / property >
#     < property name = "mlt_service" > mix < / property >
#     < property name = "always_active" > 1 < / property >
#     < property name = "sum" > 1 < / property >
#   < / transition >
#   < transition id = "transition1" >
#     < property name = "a_track" > 1 < / property >
#     < property name = "b_track" > 3 < / property >
#     < property name = "version" > 0.9 < / property >
#     < property name = "mlt_service" > frei0r.cairoblend < / property >
#     < property name = "threads" > 0 < / property >
#     < property name = "disable" > 0 < / property >
#   < / transition >
# < / tractor >

    # TODO プレイリストのリストを返す(id, type, shotcut:name)
    def get_playlist(self,
                     playlist_list: 'list '):
        return playlist_list

    # TODO タイムラインにshotを追加する
    def add_producer(self,
                     movie: 'str 動画のファイルパス'
                     ):
        return movie

    # TODO トランジション(フェード、ワイプ、クロスフェード、ミックス)
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

    # テストコード
    # 絶対パスでmltファイルを読み込み、保存する
    app1 = ShotcutHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/テンプレート.mlt')
    app1.save_xml('C:/Git/igapon50/traning/python/Movie/test1.mlt')
    # 相対パスでmltファイルを読み込み、動画を2つプレイリストに追加して、保存する
    app2 = ShotcutHelper('./せんちゃんネル/テンプレート.mlt')
    movies = [
        './せんちゃんネル/mov/BPUB2392.MP4',
        './せんちゃんネル/20210306/JGWU8992.MOV',
    ]
    app2.add_movies(movies)
    app2.save_xml('./test2.mlt')
    # TODO さらに、トラックを1つ追加して、保存する
    # mltにplaylistを追加
    # tractorにtrackを追加
    # tractorにtransitionを追加×2
    # app2.save_xml('./test3.mlt')
    # TODO さらに、前手順で追加したトラックに、動画を2つ追加して、保存する
    # mltにproducerを追加
    # playlistにproducerを追加
    # app2.save_xml('./test4.mlt')
