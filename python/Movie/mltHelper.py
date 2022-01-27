#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
動画編集アプリshotcutのmltプロジェクトファイルを扱うヘルパー MltHelper
    * shotcutのmltプロジェクトファイルの読込と保存 load_xml/save_xml
    * 指定の動画ファイルについて、playlistにshotを追加する add_movie/add_movies
    * 指定の動画ファイルから文字起こししたテロップについて、playlistにshotを追加する add_subtitle/add_subtitles
    * タイムラインに(映像)トラックを追加する add_track
MltHelperの関連関数
    * 相対パスが指定されたら絶対パスを返す　get_abs_path
    * リストに無い次の(アルファベット+十進数値な)名前のindex(管理番号)を返す get_next_index_entry
ShotValue
    * ShotValueが字幕か判定する is_filter
    * playlistに追加するshotのodを作って返す create_shot_playlist
    * producerに追加するshotのodを作って返す create_shot_producer
MltValue
"""
import datetime
import glob
import os
import sys
import pyperclip
import xmltodict
import collections
import hashlib
from dataclasses import dataclass

from movieHelper import *


def get_abs_path(path):
    """
    相対パスが指定されたら絶対パスを返す

    :param path: 相対パスや絶対パス
    :return: 絶対パス
    """
    if path is not None:
        if os.path.isabs(path):
            _path = path
        else:
            _path = os.path.abspath(path)
        return _path


def get_next_index_entry(entry):
    """
    リストに無い次の(アルファベット+十進数値な)名前のindex(管理番号)を返す

    :param entry: list 対象の管理リスト
    :return: str 次のindex(管理番号)
    """
    ret_value = 0
    entry_length = len(entry)
    for index in range(entry_length):
        if index not in entry:
            return index
        ret_value = index + 1
    return ret_value


@dataclass(frozen=True)
class MltValue:
    """
    mltの値オブジェクト
    """
    target_filepath: 'str 対象のファイルパス'
    target_basename: 'str 対象のファイル名+拡張子'
    target_dirname: 'str 対象のディレクトリ'
    target_filename: 'str 対象のファイル名'
    target_ext: 'str 対象の拡張子'

    def __init__(self, mlt_path):
        """
        コンストラクタ

        :param mlt_path: str movieのファイルパス
        """
        if mlt_path is None:
            print('mltファイルパスがNoneです')
            sys.exit()
        if not os.path.isfile(mlt_path):
            print(mlt_path, 'mltファイルが存在しません', sep=':')
            sys.exit()
        object.__setattr__(self, "target_filepath", mlt_path)
        target_basename = os.path.basename(mlt_path)
        object.__setattr__(self, "target_basename", target_basename)
        target_dirname = os.path.dirname(mlt_path)
        object.__setattr__(self, "target_dirname", target_dirname)
        target_filename = os.path.splitext(target_basename)[0]
        object.__setattr__(self, "target_filename", target_filename)
        target_ext = os.path.splitext(target_basename)[1]
        object.__setattr__(self, "target_ext", target_ext)


@dataclass(frozen=True)
class ShotValue:
    """
    shot(動画やテロップなど操作の単位)の値オブジェクト

    Todo: このクラスを継承させて、動画やテロップなどのクラスを、個別に用意したほうがいいか。そんなに頑張るつもりないので困るまで放置
    """
    index: int = 0
    contents: str = None
    in_time: str = None
    out_time: str = None
    length_time: str = None
    creation_time: str = None
    shotcut_hash: str = None

    app_name: str = 'shotcut'
    mlt_name: str = 'mlt'
    tractor_name: str = 'tractor'
    track_name: str = 'track'
    transition_name: str = 'transition'
    playlist_name: str = 'playlist'
    producer_name: str = 'producer'
    property_name: str = 'property'
    filter_name: str = 'filter'

    def __init__(self, index, contents, in_time, out_time, length_time, creation_time=None, shotcut_hash=None):
        """
        完全コンストラクタパターン
            * 動画の時は、index,contents,in_time,out_time,creation_time,shotcut_hash
            * 字幕の時は、index,contents,in_time,out_time

        :param index: int 登録するインデックス番号
        :param contents: str 動画のファイルパス、または、str テロップの文字列
        :param in_time: str 開始時刻
        :param out_time: str 終了時刻
        :param length_time: str 長さ
        :param creation_time: str 作成時刻
        :param shotcut_hash: str 動画のハッシュ
        """
        if contents is None or in_time is None or out_time is None or length_time is None:
            print('引数が不正です。')
            sys.exit()
        if not shotcut_hash is None or not creation_time is None:
            object.__setattr__(self, "shotcut_hash", shotcut_hash)
            object.__setattr__(self, "creation_time", creation_time)
        object.__setattr__(self, "contents", contents)
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "in_time", in_time)
        object.__setattr__(self, "out_time", out_time)
        object.__setattr__(self, "length_time", length_time)

    def is_filter(self):
        """
        フィルター(字幕)の判定

        :return: bool フィルター(字幕)ならTrue/そうでないならFalse
        """
        if self.shotcut_hash is None:
            return True
        else:
            return False

    def create_shot_playlist(self):
        """
        playlistに追加するshotのodを作って返す

        :return: collections.OrderedDict playlistに追加するshot
        """
        if self.is_filter():
            # 字幕の時
            od = collections.OrderedDict([('@' + self.producer_name, self.producer_name + str(self.index)),
                                          ('@in', self.in_time),
                                          ('@out', self.out_time)])
        else:
            # 動画の時
            od = collections.OrderedDict([('@' + self.producer_name, self.producer_name + str(self.index)),
                                          ('@in', self.in_time),
                                          ('@out', self.out_time)])
        return od

    def create_shot_producer(self, index=None):
        """
        producerに追加するshotのodを作って返す
        todo indexの渡し方がビミョー

        :param index: str filterの次の登録番号
        :return: collections.OrderedDict playlistに追加するshot
        """
        if self.is_filter():
            # 字幕の時
            if index is None:
                print('引数indexがNoneです')
                sys.exit()
            od2 = collections.OrderedDict([('@id', self.filter_name + index),
                                           ('@out', self.out_time),
                                           (self.property_name, []),
                                           ])
            property_list2 = [collections.OrderedDict([('@name', 'argument'), ('#text', self.contents)]),
                              collections.OrderedDict([('@name', 'geometry'), ('#text', '0 810 1920 270 1')]),
                              collections.OrderedDict([('@name', 'family'), ('#text', 'Verdana')]),
                              collections.OrderedDict([('@name', 'size'), ('#text', '120')]),
                              collections.OrderedDict([('@name', 'weight'), ('#text', '750')]),
                              collections.OrderedDict([('@name', 'style'), ('#text', 'normal')]),
                              collections.OrderedDict([('@name', 'fgcolour'), ('#text', '#ffffffff')]),
                              collections.OrderedDict([('@name', 'bgcolour'), ('#text', '#00000000')]),
                              collections.OrderedDict([('@name', 'olcolour'), ('#text', '#aa000000')]),
                              collections.OrderedDict([('@name', 'pad'), ('#text', '0')]),
                              collections.OrderedDict([('@name', 'halign'), ('#text', 'center')]),
                              collections.OrderedDict([('@name', 'valign'), ('#text', 'top')]),
                              collections.OrderedDict([('@name', 'outline'), ('#text', '3')]),
                              collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'dynamictext')]),
                              collections.OrderedDict([('@name', 'shotcut:filter'), ('#text', 'dynamicText')]),
                              collections.OrderedDict([('@name', 'shotcut:usePointSize'), ('#text', '1')]),
                              collections.OrderedDict([('@name', 'shotcut:pointSize'), ('#text', '60')]),
                              ]
            for prop in property_list2:
                od2.get(self.property_name).append(prop)
            od = collections.OrderedDict([('@id', self.producer_name + str(self.index)),
                                          ('@in', self.in_time),
                                          ('@out', self.out_time),
                                          (self.property_name, []),
                                          (self.filter_name, od2),
                                          ])
            property_list = [collections.OrderedDict([('@name', 'length'), ('#text', '04:00:00.050')]),
                             collections.OrderedDict([('@name', 'eof'), ('#text', 'pause')]),
                             collections.OrderedDict([('@name', 'resource'), ('#text', '#00000000')]),
                             collections.OrderedDict([('@name', 'aspect_ratio'), ('#text', '1')]),
                             collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'color')]),
                             collections.OrderedDict([('@name', 'mlt_image_format'), ('#text', 'rgba')]),
                             collections.OrderedDict([('@name', 'shotcut:caption'), ('#text', 'transparent')]),
                             collections.OrderedDict([('@name', 'shotcut:detail'), ('#text', 'transparent')]),
                             collections.OrderedDict([('@name', 'ignore_points'), ('#text', '0')]),
                             collections.OrderedDict([('@name', 'xml'), ('#text', 'was here')]),
                             collections.OrderedDict([('@name', 'seekable'), ('#text', '1')]),
                             ]
        else:
            # 動画の時
            od = collections.OrderedDict([('@id', self.producer_name + str(self.index)),
                                          ('@in', self.in_time),
                                          ('@out', self.out_time),
                                          (self.property_name, []),
                                          ])
            property_list = [collections.OrderedDict([('@name', 'length'), ('#text', self.length_time)]),
                             collections.OrderedDict([('@name', 'eof'), ('#text', 'pause')]),
                             collections.OrderedDict([('@name', 'resource'), ('#text', self.contents)]),
                             collections.OrderedDict([('@name', 'audio_index'), ('#text', '-1')]),
                             collections.OrderedDict([('@name', 'video_index'), ('#text', '0')]),
                             collections.OrderedDict([('@name', 'mute_on_pause'), ('#text', '0')]),
                             collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'avformat-novalidate')]),
                             collections.OrderedDict([('@name', 'seekable'), ('#text', '1')]),
                             collections.OrderedDict([('@name', 'aspect_ratio'), ('#text', '1')]),
                             collections.OrderedDict([('@name', 'creation_time'), ('#text', self.creation_time)]),
                             collections.OrderedDict([('@name', 'global_feed'), ('#text', '1')]),
                             collections.OrderedDict([('@name', 'xml'), ('#text', 'was here')]),
                             collections.OrderedDict([('@name', 'shotcut:hash'), ('#text', self.shotcut_hash)]),
                             collections.OrderedDict([('@name', 'shotcut:caption'),
                                                      ('#text', os.path.basename(self.contents))])]
        for prop in property_list:
            od.get(self.property_name).append(prop)
        return od


class MltHelper:
    """
    動画編集shotcutのmltプロジェクトファイルを編集するヘルパー
    内部では辞書型でデータを保持する
    shotcutのmltプロジェクトファイルフォーマット https://shotcut.org/notes/mltxml-annotations/
    """
    app_name: str = 'shotcut'
    mlt_name: str = 'mlt'
    tractor_name: str = 'tractor'
    track_name: str = 'track'
    transition_name: str = 'transition'
    playlist_name: str = 'playlist'
    producer_name: str = 'producer'
    property_name: str = 'property'
    filter_name: str = 'filter'

    def __init__(self, mlt_value):
        """
        コンストラクタ

        :param mlt_value: str shotcutのmltプロジェクトファイルパス、または、MltValue mltの値オブジェクト
        """
        self.xml_data = None
        self.dict_data = None
        self.playlist_entry = []
        self.producer_entry = []
        self.transition_entry = []
        self.filter_entry = []
        if mlt_value is None:
            print('引数mlt_valueがNoneです')
            sys.exit()
        if isinstance(mlt_value, str):
            mlt_value = MltValue(mlt_value)
        self.mlt_value = mlt_value
        self.mlt_path = get_abs_path(self.mlt_value.target_filepath)
        self.load_xml()

    def __load_playlist(self):
        """
        playlist_entryのロード

        :return: None
        """
        self.__clear_playlist_entry()
        tractor_root = self.dict_data.get(self.mlt_name).get(self.tractor_name)
        count = len(self.app_name)
        if tractor_root.get('@title')[:count].lower() != self.app_name.lower():
            print('プロジェクトファイルにtractorがありません')
            sys.exit()
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
                sys.exit()
            self.__register_index_playlist_entry(int(number))

    def __load_producer(self):
        """
        producer_entryのロード

        :return: None
        """
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
                sys.exit()
            self.__register_index_producer_entry(int(number))

    def __load_transition(self):
        """
        transition_entryのロード

        :return: None
        """
        self.__clear_transition_entry()
        tractor_root = self.dict_data.get(self.mlt_name).get(self.tractor_name)
        count = len(self.app_name)
        if tractor_root.get('@title')[:count].lower() != self.app_name.lower():
            print('プロジェクトファイルにtractorがありません')
            sys.exit()
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
                sys.exit()
            self.__register_index_transition_entry(int(number))

    def __load_filter(self):
        """
        filter_entryのロード

        :return: None
        """
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
                sys.exit()
            self.__register_index_filter_entry(int(number))

    def load_xml(self):
        """
        プロジェクトファイルをロードする

        :return: None
        """
        if not os.path.isfile(self.mlt_path):
            print('プロジェクトファイルがありません')
            sys.exit()
        with open(self.mlt_path, encoding='utf-8') as fp:
            self.xml_data = fp.read()
        # xml → dict
        self.dict_data = xmltodict.parse(self.xml_data)
        # 各管理テーブルをロードする
        self.__load_playlist()
        self.__load_producer()
        self.__load_transition()
        self.__load_filter()

    def save_xml(self, save_path):
        """
        shotcutのmltプロジェクトファイルを保存する（ファイルがある場合は保存しない）

        :param save_path: str xmlで保存するファイルパス
        :return: None
        """
        if save_path is None:
            print('引数が空です')
            sys.exit()
        path = get_abs_path(save_path)
        if os.path.isfile(path):
            print('ファイルが存在します。xmlファイル保存を中止します。')
            sys.exit()
        with open(path, mode='w', encoding='utf-8') as fp:
            # dict → xml , xmlの整形 , xmlの保存
            self.xml_data = xmltodict.unparse(self.dict_data, pretty=True)
            fp.write(self.xml_data)

    def __get_count_playlist_entry(self):
        """
        現在のトラック数を取得する

        :return: int トラック数
        """
        return len(self.playlist_entry)

    def __get_next_index_playlist_entry(self):
        """
        次の登録番号を取得する

        :return: 次の登録番号
        """
        return get_next_index_entry(self.playlist_entry)

    def __get_next_index_producer_entry(self):
        """
        次の登録番号を取得する

        :return: 次の登録番号
        """
        return get_next_index_entry(self.producer_entry)

    def __get_next_index_transition_entry(self):
        """
        次の登録番号を取得する

        :return: 次の登録番号
        """
        return get_next_index_entry(self.transition_entry)

    def __get_next_index_filter_entry(self):
        """
        次の登録番号を取得する

        :return: 次の登録番号
        """
        return get_next_index_entry(self.filter_entry)

    def __register_index_playlist_entry(self, index):
        """
        管理番号を登録する

        :param index: int 登録する管理番号
        :return: None
        """
        self.playlist_entry.append(index)

    def __register_index_producer_entry(self, index):
        """
        管理番号を登録する

        :param index: int 登録する管理番号
        :return: None
        """
        self.producer_entry.append(index)

    def __register_index_transition_entry(self, index):
        """
        管理番号を登録する

        :param index: int 登録する管理番号
        :return: None
        """
        self.transition_entry.append(index)

    def __register_index_filter_entry(self, index: 'int 登録する管理番号'):
        """
        管理番号を登録する

        :param index: int 登録する管理番号
        :return: None
        """
        self.filter_entry.append(index)

    def __clear_playlist_entry(self):
        """
        管理番号を初期化する

        :return: None
        """
        self.playlist_entry.clear()

    def __clear_producer_entry(self):
        """
        管理番号を初期化する

        :return: None
        """
        self.producer_entry.clear()

    def __clear_transition_entry(self):
        """
        管理番号を初期化する

        :return: None
        """
        self.transition_entry.clear()

    def __clear_filter_entry(self):
        """
        管理番号を初期化する

        :return: None
        """
        self.filter_entry.clear()

    def __add_shot_to_playlist(self, playlist_id, shot_value):
        """
        playlistにshotを追加する

        :param playlist_id: str 追加するプレイリストのID
        :param shot_value: ShotValue shot(動画やテロップなど操作の単位)の値クラス
        :return: None
        """
        for target_root in self.dict_data.get(self.mlt_name).get(self.playlist_name):
            if target_root.get('@id') == playlist_id:
                od = shot_value.create_shot_playlist()
                if target_root.get('entry') is None:
                    # 作ったばかりのplaylistでentryがない場合作る
                    target_root['entry'] = []
                    # blankがあったら削除する
                    if not target_root.get('blank') is None:
                        del target_root['blank']
                target_root.get('entry').append(od)
                return
        print('プロジェクトファイルに指定のplaylistがありません')
        sys.exit()

    def __add_shot_to_producer(self, shot_value):
        """
        producerにshotを追加する

        :param shot_value: ShotValue shot(動画や字幕など操作の単位)の値クラス
        :return: None
        """
        target_root = self.dict_data.get('mlt').get(self.producer_name)
        if shot_value.is_filter():
            index = self.__get_next_index_filter_entry()
            od = shot_value.create_shot_producer(str(index))
            target_root.append(od)
            self.__register_index_filter_entry(index)
        else:
            od = shot_value.create_shot_producer()
            target_root.append(od)

    def add_movie(self, playlist_id, movie):
        """
        producerの空き番号を調べて、playlistとproducerに動画を追加する
        ※途中で失敗したらロールバックせずに中断

        :param playlist_id: str 対象のプレイリストのID
        :param movie: str 追加する動画のファイルパス
        :return: None
        """
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit()
        if movie is None:
            print('引数movieが空です')
            sys.exit()
        path = get_abs_path(movie)
        if not os.path.isfile(path):
            print('ファイルが見つかりません。処理を中止します。')
            sys.exit()
        # shot(動画や字幕など)の空き番号を調べる
        index = self.__get_next_index_producer_entry()
        # shot(動画や字幕など)の情報を集める
        mh = MovieHelper(path)
        shot_value = ShotValue(index,
                               path,
                               mh.get_in_time(),
                               mh.get_out_time(),
                               mh.get_length_time(),
                               mh.get_creation_time(),
                               mh.get_md5(),
                               )
        # playlistにshot(動画や字幕など)を追加する
        self.__add_shot_to_playlist(playlist_id, shot_value)
        # producerにshot(動画や字幕など)を追加する
        self.__add_shot_to_producer(shot_value)
        # 追加したshot(動画や字幕など)の管理番号を登録する
        self.__register_index_producer_entry(index)

    def add_movies(self, playlist_id, movie_list):
        """
        プレイリストに動画を追加する

        :param playlist_id: str 対象のプレイリストのID
        :param movie_list: list 追加する動画ファイルパスのリスト
        :return: None
        """
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit()
        if movie_list is None:
            print('引数movie_listが空です')
            sys.exit()
        for movie in movie_list:
            self.add_movie(playlist_id, movie)

    def add_subtitle(self, playlist_id, movie):
        """
        動画ファイルから文字起こしして、プレイリストに字幕を追加する

        :param playlist_id: str 対象のプレイリストのID
        :param movie: str 動画ファイルパス
        :return: None
        """
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit()
        if movie is None:
            print('引数movieが空です')
            sys.exit()
        path = get_abs_path(movie)
        if not os.path.isfile(path):
            print('ファイルが見つかりません。処理を中止します。')
            sys.exit()
        # shot(動画や字幕など)の空き番号を調べる
        index = self.__get_next_index_producer_entry()
        # shot(動画や字幕など)の情報を集める
        mh = MovieHelper(path)
        contents = mh.mov_to_subtitles()
        shot_value = ShotValue(index, contents, mh.get_in_time(), mh.get_out_time(), mh.get_length_time())
        # playlistにshot(動画や字幕など)を追加する
        self.__add_shot_to_playlist(playlist_id, shot_value)
        # producerにshot(動画や字幕など)を追加する
        self.__add_shot_to_producer(shot_value)
        # 追加したshot(動画や字幕など)の管理番号を登録する
        self.__register_index_producer_entry(index)

    def add_subtitles(self, playlist_id, movies):
        """
        動画ファイルから文字起こしして、プレイリストに字幕を追加する

        :param playlist_id: str 対象のプレイリストのID
        :param movies: list[str] 動画ファイルパスのリスト
        :return: None
        """
        if playlist_id is None:
            print('引数playlist_idが空です')
            sys.exit()
        if movies is None:
            print('引数moviesが空です')
            sys.exit()
        for movie in movies:
            self.add_subtitle(playlist_id, movie)

    def __add_playlist_to_mlt(self, index, name):
        """
        mltにplaylistを追加する(nameは他のトラックと重複可能)
        videoトラック追加用

        < playlist id = "playlist2" >
            < property name = "shotcut:video" > 1 < / property >
            < property name = "shotcut:name" > V2 < / property >
            < blank length = "00:00:00.050" / >
        < / playlist >

        :param index: int 登録するplaylistの番号
        :param name: str トラック名(他のトラックと重複可能)
        :return: None
        """
        playlist_root = self.dict_data.get('mlt').get(self.playlist_name)
        od2 = collections.OrderedDict([('@length', '00:00:00.040')])
        # playlistの空き番号を調べる
        od = collections.OrderedDict([('@id', self.playlist_name + str(index)),
                                      (self.property_name, []),
                                      ('blank', od2),
                                      ])
        property_list = [collections.OrderedDict([('@name', 'shotcut:video'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'shotcut:name'), ('#text', name)]),
                         ]
        for prop in property_list:
            od[self.property_name].append(prop)
        playlist_root.append(od)

    def __add_track_to_tractor(self, index):
        """
        mltのtractorにtrackを追加する
        transitionの空き番号を調べる

        < tractor id = "tractor6" title = "Shotcut version UNSTABLE-21.02.09" global_feed = "1"
         in = "00:00:00.000" out = "00:02:44.726" >
        < track producer = "playlist2" / >

        :param index: int 登録するplaylistの番号
        :return: str trackのproducer名
        """
        ret_producer = self.playlist_name + str(index)
        track_root = self.dict_data.get('mlt').get(self.tractor_name).get(self.track_name)
        od = collections.OrderedDict([('@producer', ret_producer)])
        track_root.append(od)
        return ret_producer

    def __add_transition_to_tractor(self):
        """
        mltのtractorにtransitionを二つ追加する
        ※映像トラック追加時に使用する
        ※先にplaylistの登録__register_index_playlist_entry()を行うこと

        < transition id = "transition0" >
            < property name = "a_track" > 0 < / property > 固定
            < property name = "b_track" > 3 < / property > track毎にインクリメント、1スタート、前詰め
            < property name = "mlt_service" > mix < / property > 固定
            < property name = "always_active" > 1 < / property > 固定
            < property name = "sum" > 1 < / property > 固定
        < / transition >

        < transition id = "transition1" >
            < property name = "a_track" > 1 < / property > 一つ目のトラック=0、二つ目以降=1
            < property name = "b_track" > 3 < / property > track毎にインクリメント、1スタート、前詰め
            < property name = "version" > 0.9 < / property > 固定
            < property name = "mlt_service" > frei0r.cairoblend < / property > 固定
            < property name = "threads" > 0 < / property > 固定
            < property name = "disable" > 0 < / property > 一つ目のトラック=1、二つ目以降=0
        < / transition >

        :return: None
        """
        transition_root = self.dict_data.get('mlt').get(self.tractor_name).get(self.transition_name)
        index = self.__get_next_index_transition_entry()
        od = collections.OrderedDict([('@id', self.transition_name + str(index)),
                                      (self.property_name, []),
                                      ])
        transition_root.append(od)
        property_list = [collections.OrderedDict([('@name', 'a_track'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'b_track'),
                                                  ('#text', str(self.__get_count_playlist_entry()))]),
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
        property_list = [collections.OrderedDict([('@name', 'a_track'), ('#text', '1')]),
                         collections.OrderedDict([('@name', 'b_track'),
                                                  ('#text', str(self.__get_count_playlist_entry()))]),
                         collections.OrderedDict([('@name', 'version'), ('#text', '0.9')]),
                         collections.OrderedDict([('@name', 'mlt_service'), ('#text', 'frei0r.cairoblend')]),
                         collections.OrderedDict([('@name', 'threads'), ('#text', '0')]),
                         collections.OrderedDict([('@name', 'disable'), ('#text', '0')]),
                         ]
        last_key = next(reversed(transition_root), None)
        for prop in property_list:
            last_key[self.property_name].append(prop)
        self.__register_index_transition_entry(index)

    def add_track(self, name):
        """
        タイムラインに(映像)トラックを追加する(mltファイルのplaylistタグid=playlist0..)
        videoトラック追加用

        Todo: トラックが一つもない時に未対応
            * mltにplaylist id="main_bin"がなければmain_binを追加し、mltのproducer="main_bin"に変更する
            * mltにtractorがなければ、playlist id="playlist0"をtractor id="tractor0"に変更し、tractorにtransitionを追加する
            * mltにplaylist id="background"がなければbackgroundを追加し、tractorにtrackを追加する

        :param name: str トラック名(他のトラックと重複可能)
        :return: str プレイリスト名
        """
        # 追加するプレイリストの管理番号を取得する
        index = self.__get_next_index_playlist_entry()
        # mltにplaylist id="playlist{index}"を追加する
        self.__add_playlist_to_mlt(index, name)
        # tractorにtrackを追加する
        ret_playlist = self.__add_track_to_tractor(index)
        # 追加したplaylistの管理番号を登録する
        self.__register_index_playlist_entry(index)
        # tractorにtransitionを追加する、一個目,二個目
        self.__add_transition_to_tractor()
        return ret_playlist

    def add_producer(self, movie):
        """
        TODO タイムラインにshotを追加する

        :param movie: str 動画のファイルパス
        :return:
        """
        # mltにproducerを追加
        # playlistにproducerを追加
        # playlistからblankを削除？
        return movie

    def add_tractor(self, movie):
        """
        TODO トランジション(フェード、ワイプ、クロスフェード、ミックス)

        :param movie: str 動画のファイルパス
        :return:
        """
        return movie


def test01():
    """
    絶対パスでmltファイルを読み込み、保存する

    :return: None
    """
    app = MltHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート.mlt')
    app.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート_test01.mlt')


def test02():
    """
    相対パスでmltファイルを読み込み、動画を2つプレイリストに追加して、保存する

    :return: None
    """
    app = MltHelper('./せんちゃんネル/test/テンプレート.mlt')
    movies = [
        './せんちゃんネル/mov/BPUB2392.MP4',
        './せんちゃんネル/20210306/JGWU8992.MOV',
    ]
    app.add_movies('main_bin', movies)
    app.save_xml('./せんちゃんネル/test/テンプレート_test02.mlt')


def test03():
    """
    カレントフォルダ以下で「*_part*.mov」を再帰検索して、見つけたファイルをトラックplaylist0に追加して、保存する

    :return: None
    """
    app = MltHelper('./せんちゃんネル/test/テンプレート.mlt')
    movies = glob.glob('./**/*_part*.mov', recursive=True)
    app.add_movies('playlist0', movies)
    app.save_xml('./せんちゃんネル/test/テンプレート_test03.mlt')


def test04():
    """
    トラックを1つ追加して、保存する

    :return: None
    """
    app = MltHelper('./せんちゃんネル/test/テンプレート.mlt')
    target_playlist = app.add_track('V2')
    app.save_xml('./せんちゃんネル/test/テンプレート_test04.mlt')


def test05():
    """
    トラックを1つ追加し、カレントフォルダ以下で「*_part*.mov」を再帰検索して、見つけたファイルを追加したトラックに追加して、保存する

    :return: None
    """
    app = MltHelper('./せんちゃんネル/test/テンプレート.mlt')
    playlist_id = app.add_track('V2')
    movies = glob.glob('./**/*_part*.mov', recursive=True)
    app.add_movies(playlist_id, movies)
    app.save_xml('./せんちゃんネル/test/テンプレート_test05.mlt')


def test06():
    """
    target_file_pathの親フォルダ以下で「*_part*.mov」を再帰検索して、見つけたファイルをプレイリストとV1トラックに追加して、保存する

    :return: None
    """
    # パスを作成
    target_file_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート.mlt'
    target_folder = os.path.dirname(target_file_path)
    target_mlt_basename = os.path.basename(target_file_path)
    target_mlt_file_name = os.path.splitext(target_mlt_basename)[0]
    target_mlt_file_ext = os.path.splitext(target_mlt_basename)[1]
    search_path = target_folder + '\\..\\**\\*_part*.mov'
    create_mlt_path = os.path.join(target_folder, target_mlt_file_name + '_test06' + target_mlt_file_ext)
    movies = glob.glob(search_path, recursive=True)
    app = MltHelper(target_file_path)
    # 動画をプレイリストに追加
    app.add_movies('main_bin', movies)
    # 動画をタイムラインに追加
    app.add_movies('playlist0', movies)
    app.save_xml(create_mlt_path)


def test07():
    """
    V2トラックを追加して、保存する。
    さらに、動画をプレイリストと追加したV2トラックに追加して、保存する。
    さらに、V3トラックを追加して、保存する。
    さらに、動画から文字起こしして、プレイリストと追加したV3トラックに追加して、保存する。

    :return: None
    """
    movies = ['C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/JPIC3316.MOV']
    app = MltHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート.mlt')
    # 動画や字幕用のトラックを追加'playlist2'
    playlist_id = app.add_track('V2')
    app.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート_test07_add_track.mlt')
    # 動画をプレイリストに追加'main_bin'
    app.add_movies('main_bin', movies)
    # 動画をプレイリストに追加'playlist2'
    app.add_movies(playlist_id, movies)
    app.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート_test07_add_track_mov.mlt')
    # 動画や字幕用のトラックを追加'playlist3'
    playlist_id = app.add_track('V3')
    app.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート_test07_add_track_mov_track.mlt')
    # 動画ファイルから文字起こししてプレイリストに追加'main_bin'
    app.add_subtitles('main_bin', movies)
    # 動画ファイルから文字起こししてタイムラインに追加'playlist3'
    app.add_subtitles(playlist_id, movies)
    app.save_xml('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/テンプレート_test07_add_track_mov_track_subtitles.mlt')


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
        sys.exit()
    print(target_file_path)

    test01()
    test02()
    test03()
    test04()
    test05()
    test06()
    test07()
