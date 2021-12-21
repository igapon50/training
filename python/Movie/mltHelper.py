#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file mltHelper.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/12/4
# @brief 動画編集shotcutのmltプロジェクトファイルを編集するヘルパー
# @details
# @warning
# @note
import datetime
import glob
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
# @details mltの値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class MltValue:
    target_filepath: 'str 対象のファイルパス'
    target_basename: 'str 対象のファイル名+拡張子'
    target_dirname: 'str 対象のディレクトリ'
    target_filename: 'str 対象のファイル名'
    target_ext: 'str 対象の拡張子'

    # コンストラクタ
    def __init__(self,
                 mlt_path: 'str movieのファイルパス',
                 ):
        if mlt_path is None:
            print('mltファイルパスがNoneです')
            sys.exit(1)
        if not os.path.isfile(mlt_path):
            print(mlt_path, 'mltファイルが存在しません', sep=':')
            sys.exit(1)
        object.__setattr__(self, "target_filepath", mlt_path)
        target_basename = os.path.basename(mlt_path)
        object.__setattr__(self, "target_basename", target_basename)
        target_dirname = os.path.dirname(mlt_path)
        object.__setattr__(self, "target_dirname", target_dirname)
        target_filename = os.path.splitext(target_basename)[0]
        object.__setattr__(self, "target_filename", target_filename)
        target_ext = os.path.splitext(target_basename)[1]
        object.__setattr__(self, "target_ext", target_ext)


##
# @brief Value Objects
# @details shot(動画やテロップなど操作の単位)の値オブジェクト。
# @warning
# @note
# TODO このクラスを継承させて、動画やテロップなどのクラスを、個別に用意したほうがいいか。そんなに頑張るつもりないので困るまで放置。
@dataclass(frozen=True)
class ShotValue:
    movie: str = None
    index: int = 0
    shotcut_hash: str = None
    in_time: str = None
    out_time: str = None
    creation_time: str = None
    time: datetime = None

    # 完全コンストラクタパターン
    # 動画の時は、contents,index,shotcut_hash
    # テロップの時は、contents,index,time
    def __init__(self,
                 contents: 'str 動画のファイルパス、または、str テロップの文字列',
                 index: 'int 登録するインデックス番号',
                 shotcut_hash: 'str 動画のハッシュ' = None,
                 time: 'datetime 時間' = None,
                 ):
        # TODO 動画とテロップでの呼び分け処理
        if time is not None:
            object.__setattr__(self, "time", time)
        if contents is None or shotcut_hash is None:
            print('引数が不正です。')
            sys.exit(1)
        object.__setattr__(self, "movie", contents)
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "shotcut_hash", shotcut_hash)
        # item(動画)の情報を集める
        video_info = ffmpeg.probe(contents)
        creation_str = video_info.get('format').get('tags').get('creation_time')
        if creation_str is None:
            c_time = os.path.getctime(contents)
            dt = datetime.datetime.fromtimestamp(c_time)
            creation_time = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        else:
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
# @brief 動画編集shotcutのmltプロジェクトファイルを編集するヘルパー
# @details 内部では辞書型でデータを保持する
# @warning
# @note
# shotcutのmltプロジェクトファイルフォーマット
# https://shotcut.org/notes/mltxml-annotations/
class MltHelper:
    app_name: str = 'shotcut'
    mlt_name: str = 'mlt'
    tractor_name: str = 'tractor'
    track_name: str = 'track'
    transition_name: str = 'transition'
    playlist_name: str = 'playlist'
    producer_name: str = 'producer'
    property_name: str = 'property'
    filter_name: str = 'filter'

    # コンストラクタ
    def __init__(self,
                 mlt_value  # str shotcutのmltプロジェクトファイルパス、または、MltValue mltの値オブジェクト
                 ):
        self.xml_data = None
        self.dict_data = None
        self.playlist_entry = []
        self.producer_entry = []
        self.transition_entry = []
        self.filter_entry = []
        if mlt_value is None:
            print('引数mlt_valueがNoneです')
            sys.exit(1)
        if isinstance(mlt_value, str):
            mlt_value = MltValue(mlt_value)
        self.mlt_value = mlt_value
        self.mlt_path = get_abs_path(self.mlt_value.target_filepath)
        self.load_xml()

    # playlist_entryのロード
    def __load_playlist(self):
        self.__clear_playlist_entry()
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
        self.__clear_producer_entry()
        mlt_root = self.dict_data.get(self.mlt_name)
        target_root = mlt_root.get(self.producer_name)
        for index in range(len(target_root)):
            element = target_root[index]
            key = '@id'
            name = element[key]
            count = len(self.producer_name)
            if self.producer_name != name[:count]:
                continue
            number = name[count:]
            if not number.isdecimal():
                print('producer_entryに追加するindexを決定できなかった')
                sys.exit(1)
            self.__register_index_producer_entry(int(number))

    # transition_entryのロード
    def __load_transition(self):
        self.__clear_transition_entry()
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

    # filter_entryのロード
    def __load_filter(self):
        self.__clear_filter_entry()
        mlt_root = self.dict_data.get(self.mlt_name)
        target_root = mlt_root.get(self.producer_name)
        for index in range(len(target_root)):
            element = target_root[index]
            element = element.get(self.filter_name)
            if element is None:
                continue
            key = '@id'
            name = element[key]
            count = len(self.filter_name)
            if self.filter_name != name[:count]:
                continue
            number = name[count:]
            if not number.isdecimal():
                print('producer_entryに追加するindexを決定できなかった')
                sys.exit(1)
            self.__register_index_producer_entry(int(number))

    # プロジェクトファイルをロードする
    def load_xml(self):
        if not os.path.isfile(self.mlt_path):
            print('プロジェクトファイルがありません')
            sys.exit(1)
        with open(self.mlt_path, encoding='utf-8') as fp:
            self.xml_data = fp.read()
        # xml → dict
        self.dict_data = xmltodict.parse(self.xml_data)
        # 各管理テーブルをロードする
        self.__load_playlist()
        self.__load_producer()
        self.__load_transition()
        self.__load_filter()

    # shotcutのmltプロジェクトファイルを保存する（ファイルがある場合は保存しない）
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

    def __get_next_index_filter_entry(self):
        return get_next_index_entry(self.filter_entry)

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

    def __register_index_transition_entry(self,
                                          index: 'int 登録する管理番号',
                                          ):
        self.transition_entry.append(index)

    def __register_index_filter_entry(self,
                                      index: 'int 登録する管理番号',
                                      ):
        self.filter_entry.append(index)

    def __clear_playlist_entry(self):
        self.playlist_entry.clear()

    def __clear_producer_entry(self):
        self.producer_entry.clear()

    def __clear_transition_entry(self):
        self.transition_entry.clear()

    def __clear_filter_entry(self):
        self.filter_entry.clear()

    # playlistにitem(動画)を追加する
    def __add_item_to_playlist(self,
                               playlist_id: 'str 追加するプレイリストのID',
                               shot_value: 'ShotValue shot(動画やテロップなど操作の単位)の値クラス',
                               ):
        for target_root in self.dict_data.get(self.mlt_name).get(self.playlist_name):
            if target_root.get('@id') == playlist_id:
                od = collections.OrderedDict([('@' + self.producer_name, self.producer_name + str(shot_value.index)),
                                              ('@in', shot_value.in_time),
                                              ('@out', shot_value.out_time)])
                target_root.get('entry').append(od)
                return
        print('プロジェクトファイルに指定のplaylistがありません')
        sys.exit(1)

    # producerにitem(動画)を追加する
    def __add_item_to_producer(self,
                               shot_value: 'ShotValue shot(動画やテロップなど操作の単位)の値クラス',
                               ):
        mlt_dict = self.dict_data.get('mlt').get(self.producer_name)
        od = collections.OrderedDict([('@id', self.producer_name + str(shot_value.index)),
                                      ('@in', shot_value.in_time),
                                      ('@out', shot_value.out_time),
                                      (self.property_name, [])])
        mlt_dict.append(od)
        property_list = [collections.OrderedDict([('@name', 'length'), ('#text', shot_value.out_time)]),
                         collections.OrderedDict([('@name', 'eof'), ('#text', 'pause')]),
                         collections.OrderedDict([('@name', 'resource'), ('#text', shot_value.movie)]),
                         collections.OrderedDict([('@name', 'audio_index'), ('#text', '-1')]),
                         collections.OrderedDict([('@name', 'video_index'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mute_on_pause'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'avformat-novalidate')]),
                         collections.OrderedDict([('@name', 'seekable'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'aspect_ratio'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'creation_time'), ('#text', shot_value.creation_time)]),
                         collections.OrderedDict([('@name', 'global_feed'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'xml'), ('#text', 'was here')]),
                         collections.OrderedDict([('@name', 'shotcut:hash'), ('#text', shot_value.shotcut_hash)]),
                         collections.OrderedDict([('@name', 'shotcut:caption'),
                                                  ('#text', os.path.basename(shot_value.movie))])]
        last_key = next(reversed(mlt_dict), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)

    # producerの空き番号を調べて、playlistとproducerにitem(動画)を追加する
    # ※途中で失敗したらロールバックせずに中断
    def add_movie(self,
                  playlist_id: 'str 対象のプレイリストのID',
                  movie: 'str 追加する動画のファイルパス',
                  ):
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit(1)
        if movie is None:
            print('引数movieが空です')
            sys.exit(1)
        path = get_abs_path(movie)
        if not os.path.isfile(path):
            print('ファイルが見つかりません。処理を中止します。')
            sys.exit(1)
        # item(動画)の空き番号を調べる
        index = self.__get_next_index_producer_entry()
        # item(動画)のハッシュを計算
        shotcut_hash = get_md5(path)
        # item(動画)の情報を集める
        shot_value = ShotValue(path, index, shotcut_hash)
        # playlistにitem(動画)を追加する
        self.__add_item_to_playlist(playlist_id, shot_value)
        # producerにitem(動画)を追加する
        self.__add_item_to_producer(shot_value)
        # 追加したitem(動画)の管理番号を登録する
        self.__register_index_producer_entry(index)
        return

    # プレイリストに動画を追加する
    def add_movies(self,
                   playlist_id: 'str 対象のプレイリストのID',
                   movie_list: 'list 追加する動画ファイルパスのリスト',
                   ):
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit(1)
        if movie_list is None:
            print('引数movie_listが空です')
            sys.exit(1)
        for movie in movie_list:
            self.add_movie(playlist_id, movie)

    # mltにplaylistを追加する(nameは他のトラックと重複可能)
    # videoトラック追加用
    # < playlist id = "playlist2" >
    #     < property name = "shotcut:video" > 1 < / property >
    #     < property name = "shotcut:name" > V2 < / property >
    #     < blank length = "00:00:00.050" / >
    # < / playlist >
    def __add_playlist_to_mlt(self,
                              index: 'int 登録するplaylistの番号',
                              name: 'str トラック名(他のトラックと重複可能)',
                              ):
        playlist_root = self.dict_data.get('mlt').get(self.playlist_name)
        od2 = collections.OrderedDict([('@length', '00:00:00.040')])
        # playlistの空き番号を調べる
        od = collections.OrderedDict([('@id', self.playlist_name + str(index)),
                                      (self.property_name, []),
                                      ('blank', od2),
                                      ])
        playlist_root.append(od)
        property_list = [collections.OrderedDict([('@name', 'shotcut:video'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'shotcut:name'), ('#text', name)]),
                         ]
        last_key = next(reversed(playlist_root), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)

    # mltのtractorにtrackを追加する
    # < tractor id = "tractor6" title = "Shotcut version UNSTABLE-21.02.09" global_feed = "1"
    #    in = "00:00:00.000" out = "00:02:44.726" >
    #   < track producer = "playlist2" / >
    # transitionの空き番号を調べる
    def __add_track_to_tractor(self,
                               index: 'int 登録するplaylistの番号',
                               ):
        track_root = self.dict_data.get('mlt').get(self.tractor_name).get(self.track_name)
        od = collections.OrderedDict([('@producer', self.playlist_name + str(index))])
        track_root.append(od)

    # mltのtractorにtransitionを二つ追加する
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
    def __add_transition_to_tractor(self,
                                    ):
        transition_root = self.dict_data.get('mlt').get(self.tractor_name).get(self.transition_name)
        index = self.__get_next_index_transition_entry()
        od = collections.OrderedDict([('@id', self.transition_name + str(index)),
                                      (self.property_name, []),
                                      ])
        transition_root.append(od)
        # TODO 値の仕様が不明
        property_list = [collections.OrderedDict([('@name', 'a_track'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'b_track'), ('#text', '3')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'mix')]),
                         collections.OrderedDict([('@name', 'always_active'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'sum'), ('#text', '1')]),
                         ]
        last_key = next(reversed(transition_root), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)
        self.__register_index_transition_entry(index)
        index = self.__get_next_index_transition_entry()
        od = collections.OrderedDict([('@id', self.transition_name + str(index)),
                                      (self.property_name, []),
                                      ])
        transition_root.append(od)
        # TODO 値の仕様が不明
        property_list = [collections.OrderedDict([('@name', 'a_track'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'b_track'), ('#text', '3')]),
                         collections.OrderedDict([('@name', 'version'), ('#text', '0.9')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'frei0r.cairoblend')]),
                         collections.OrderedDict([('@name', 'threads'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'disable'), ('#text', '0')]),
                         ]
        last_key = next(reversed(transition_root), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)
        self.__register_index_transition_entry(index)

    # タイムラインにトラックを増やす(mltファイルのplaylistタグid=playlist0..)
    # videoトラック追加用
    def add_track(self,
                  name: 'str トラック名(他のトラックと重複可能)'
                  ):
        # TODO mltにplaylist id="main_bin"がなければmain_binを追加し、mltのproducer="main_bin"に変更する
        # TODO mltにtractorがなければ、playlist id="playlist0"をtractor id="tractor0"に変更し、tractorにtransitionを追加する
        # TODO mltにplaylist id="background"がなければbackgroundを追加し、tractorにtrackを追加する
        # 追加するプレイリストの管理番号を取得する
        index = self.__get_next_index_playlist_entry()
        # mltにplaylist id="playlist{index}"を追加する
        self.__add_playlist_to_mlt(index, name)
        # tractorにtrackを追加する
        self.__add_track_to_tractor(index)
        # 追加したplaylistの管理番号を登録する
        self.__register_index_playlist_entry(index)
        # tractorにtransitionを追加する、一個目,二個目
        self.__add_transition_to_tractor()
        return

    # TODO タイムラインにshotを追加する
    def add_producer(self,
                     movie: 'str 動画のファイルパス'
                     ):
        # mltにproducerを追加
        # playlistにproducerを追加
        # playlistからblankを削除？
        return movie

    # TODO トランジション(フェード、ワイプ、クロスフェード、ミックス)
    def add_tractor(self,
                    movie: 'str 動画のファイルパス'
                    ):
        return movie


def test(target_file_path: 'str 対象のファイルパス'):
    # 絶対パスでmltファイルを読み込み、保存する
    app1 = MltHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/テンプレート.mlt')
    app1.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test1.mlt')
    # 相対パスでmltファイルを読み込み、動画を2つプレイリストに追加して、保存する
    app2 = MltHelper('./せんちゃんネル/テンプレート.mlt')
    movies = [
        './せんちゃんネル/mov/BPUB2392.MP4',
        './せんちゃんネル/20210306/JGWU8992.MOV',
    ]
    app2.add_movies('main_bin', movies)
    app2.save_xml('./せんちゃんネル/test2.mlt')
    # さらに、カレントフォルダ以下で「*_part*.mov」を再起検索して、見つけたファイルをトラックplaylist0に追加して、保存する
    movies = glob.glob('./**/*_part*.mov', recursive=True)
    app2.add_movies('playlist0', movies)
    app2.save_xml('./せんちゃんネル/test3.mlt')
    # さらに、トラックを1つ追加して、保存する
    target_playlist = app2.add_track('V2')
    app2.save_xml('./せんちゃんネル/test4.mlt')
    # TODO さらに、前手順で追加したトラックに、動画を2つ追加して、保存する
    # app2.add_movies(target_playlist, movies)
    # app2.save_xml('./test5.mlt')


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
    else:
        print('引数が不正です。')
        sys.exit(1)
    print(target_file_path)

    # パスを作成
    target_folder = os.path.dirname(target_file_path)
    target_mlt_basename = os.path.basename(target_file_path)
    target_mlt_file_name = os.path.splitext(target_mlt_basename)[0]
    target_mlt_file_ext = os.path.splitext(target_mlt_basename)[1]
    search_path = target_folder + '\\**\\*_part*.mov'
    create_mlt_path = os.path.join(target_folder, target_mlt_file_name + '_new' + target_mlt_file_ext)
    movies = glob.glob(search_path, recursive=True)
    app = MltHelper(target_file_path)
    # 動画をプレイリストに追加
    app.add_movies('main_bin', movies)
    # 動画をタイムラインに追加
    app.add_movies('playlist0', movies)
    # テロップ用のトラックを追加'playlist2'
    app.add_track('V2')
    # TODO テロップの文字列をファイルから読み込む
    # TODO テロップをプレイリストに追加'main_bin'
    # app.add_telops('main_bin', telops)
    # TODO テロップをタイムラインに追加'playlist2'
    # app.add_telops('playlist2', telops)
    app.save_xml(create_mlt_path)

    # テストコード
    # test(target_file_path)
