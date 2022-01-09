#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
動画ファイルを扱うヘルパー MovieHelper
    * 動画ファイルから音声ファイルを作成する mov_to_wave
    * 動画ファイルから文字起こしして返す。ファイルにも保存する mov_to_text
    * 動画ファイルから無音部分を除いた動画ファイル群を作成する movie_dividing
    * 分割動画ファイル群から文字起こしして返す。ファイルにも保存する movie_dividing_to_text
    * mov_to_textで作った文字起こしファイルを削除する clear_text
    * movie_dividingで作った動画ファイル群を削除する clear_movie_dividing
MovieHelperの関連関数
    * 音声ファイルから文字起こしする wav_to_text
    * 動画ファイル群から文字起こしする movies_to_subtitles
    * ディレクトリ内の全ての動画ファイルから文字起こしする movie_to_subtitles_in_directory
    * movies_to_subtitlesで作った文字起こしファイル群を削除する clear_movies_to_subtitles
    * movie_to_subtitles_in_directoryで作った文字起こしファイルを削除する clear_movie_to_subtitles_in_directory
"""
import sys  # 終了時のエラー有無
import os  # ファイルパス分解
import glob
from dataclasses import dataclass

import speech_recognition as sr
import math
import numpy as np
from pydub import AudioSegment
import pyperclip
import subprocess
import soundfile as sf


def wav_to_text(wav_filepath):
    """
    音声ファイルから文字起こしして返す(長いと失敗するので1分以下のファイルにする)

    Todo:
        * wavHelperとかあってもいいかも。
        * エラーの回避策がわからないので、とりあえず例外処理にした。
    :param wav_filepath: str 音声ファイルのパス
    :return: str 文字起こし結果
    """
    if not os.path.isfile(wav_filepath):
        print('音声ファイルがありません', wav_filepath)
        exit()
    print(wav_filepath)
    r = sr.Recognizer()
    # 音声->テキスト
    with sr.AudioFile(wav_filepath) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio, language='ja-JP')
        except Exception as e:
            text = f'[文字起こしでエラー:{e}]'
    return text


def movies_to_subtitles(movies):
    """
    動画ファイル群から文字起こしする

    :param movies: str 文字起こしする動画ファイル群のファイルパスリスト
    :return: tuple (list 動画ファイルパスのリストと、list MovieHelperと , list str 文字起こしの結果リスト))を返す
    """
    if movies is None:
        print('引数moviesが不正です。', movies)
        sys.exit()
    movie_helper = []
    movie_text = []
    for _movie in movies:
        mh = MovieHelper(_movie)
        txt = mh.mov_to_text()
        movie_helper.append(mh)
        movie_text.append(txt)
    return movies, movie_helper, movie_text


def movie_to_subtitles_in_directory(path):
    """
    指定ディレクトリ内の全てのmovファイルについて、無音部分をカットした動画に分割し、それぞれ文字起こしする

    :param path: str 動画ファイルが含まれるパス
    :return: tuple (list 動画ファイルパスのリストと、list MovieHelperのリストと , list str 文字起こし結果のリスト))を返す
    """
    if not os.path.isdir(path):
        print('ディレクトリが存在しません。', path)
        sys.exit()
    _movie_list = glob.glob(os.path.join(path, '**/*.mov'), recursive=True)
    _, movie_helper, movie_text = movies_to_subtitles(_movie_list)
    return _movie_list, movie_helper, movie_text


def clear_movies_to_subtitles(movie_helper_list):
    """
    movies_to_subtitles実行時の生成ファイルを削除する

    :param movie_helper_list: list MovieHelper ヘルパーのリスト
    :return: None
    """
    if movie_helper_list is None:
        print('引数movie_helper_listが不正です')
        sys.exit()
    # 生成ファイルを削除する
    for mh in movie_helper_list:
        mh.clear_text()


def clear_movie_to_subtitles_in_directory(movie_helper_list):
    """
    movie_to_subtitles_in_directory実行時の生成ファイルを削除する

    :param movie_helper_list: list MovieHelper ヘルパーのリスト
    :return: None
    """
    clear_movies_to_subtitles(movie_helper_list)


@dataclass(frozen=True)
class MovieValue:
    """
    動画の値オブジェクト
    """
    target_filepath: 'str 対象のファイルパス'
    target_basename: 'str 対象のファイル名+拡張子'
    target_dirname: 'str 対象のディレクトリ'
    target_filename: 'str 対象のファイル名'
    target_ext: 'str 対象の拡張子'

    def __init__(self, target_filepath):
        """
        コンストラクタ

        :param target_filepath: str movieのファイルパス
        """
        if target_filepath is None:
            print('動画ファイルパスがNoneです')
            sys.exit()
        if not os.path.isfile(target_filepath):
            print(target_filepath, '動画ファイルが存在しません', sep=':')
            sys.exit()
        object.__setattr__(self, "target_filepath", target_filepath)
        target_basename = os.path.basename(target_filepath)
        object.__setattr__(self, "target_basename", target_basename)
        target_dirname = os.path.dirname(target_filepath)
        object.__setattr__(self, "target_dirname", target_dirname)
        target_filename = os.path.splitext(target_basename)[0]
        object.__setattr__(self, "target_filename", target_filename)
        target_ext = os.path.splitext(target_basename)[1]
        object.__setattr__(self, "target_ext", target_ext)


class MovieHelper:
    """
    動画ファイルのヘルパー
    """
    movie_value: 'MovieValue movieの値オブジェクト'
    movie_filepath: 'str 動画ファイル入力パス'
    wave_filepath: 'str 音声ファイル出力パス'
    text_filepath: 'str 文字起こし出力パス'
    movie_dividing_filepath: 'list 分割動画ファイル出力パスリスト'

    def __init__(self, movie_value):
        """
        コンストラクタ

        :param movie_value: str movieのファイルパス、または、MovieValue movieの値オブジェクト
        """
        if movie_value is None:
            print('引数movie_valueがNoneです')
            sys.exit()
        if isinstance(movie_value, str):
            movie_value = MovieValue(movie_value)
        self.movie_value = movie_value
        self.movie_filepath = movie_value.target_filepath
        self.movie_dividing_filepath = []
        self.wave_filepath = os.path.join(self.movie_value.target_dirname,
                                          self.movie_value.target_filename + '.wav',
                                          )
        self.text_filepath = os.path.join(self.movie_value.target_dirname,
                                          self.movie_value.target_filename + '.txt',
                                          )

    def mov_to_wave(self):
        """
        動画ファイルから音声ファイルを作る(movファイルを対象とする)

        :return: str 音声ファイルパス
        """
        # パスの分解
        if self.movie_value.target_ext.lower() != '.mov':
            print(self.movie_value.target_ext.lower(),
                  'ターゲットファイルの種類が不正です。ファイル拡張子movのファイルを指定してください',
                  sep=':')
            sys.exit()
        # 動画ファイルから音声ファイルを作る
        command_output = ["ffmpeg",
                          "-i",
                          self.movie_filepath,
                          "-ac",
                          "1",
                          "-ar",
                          "44100",
                          "-acodec",
                          "pcm_s16le",
                          self.wave_filepath,
                          ]
        subprocess.run(command_output, shell=True, stdin=subprocess.DEVNULL)
        return self.wave_filepath

    def _split_wave(self, time=30):
        """
        動画について、指定秒数単位に分割した音声ファイルを作り、そのパスリストを返す
        一時的に全体のWaveファイルを作るが、使い終わったら削除する

        :param time: int 区切る時間[秒]
        :return: list 分割した音声ファイルのパスリスト
        """
        # 動画ファイルから音声ファイルを作る
        self.mov_to_wave()
        # ファイルを読み込み
        source_audio = AudioSegment.from_wav(self.wave_filepath)
        # waveファイルの情報を取得
        total_time = source_audio.duration_seconds
        integer = math.floor(total_time)  # 小数点以下切り下げ
        num_cut = math.ceil(integer / time)  # 小数点以下切り上げ
        # 音声ファイルを削除する
        os.remove(self.wave_filepath)
        output_file_list = []
        for i in range(num_cut):
            # 出力データを生成
            output_file_path = os.path.join(self.movie_value.target_dirname,
                                            self.movie_value.target_filename + '_' + str(i).zfill(3) + '.wav',
                                            )
            start_cut = i * time * 1000
            if total_time < (i + 1) * time:
                end_cut = total_time * 1000
            else:
                end_cut = (i + 1) * time * 1000
            new_audio = source_audio[start_cut:end_cut]
            # 書き出し
            new_audio.export(output_file_path, format="wav")
            # リストに追加
            output_file_list.append(output_file_path)
        return output_file_list

    def mov_to_text(self):
        """
        動画ファイルの文字起こしして返す。ファイルにも保存する
        一時的にWaveファイルを作るが、使い終わったら削除する

        :return: str 文字起こし結果の文字列
        """
        # 動画ファイルについて、指定秒数単位に分割した音声ファイルを作り、そのパスリストを返す
        split_waves = self._split_wave()
        # 分割した音声ファイルを消費して、文字起こしする
        output_text = ''
        for wav_filepath in split_waves:
            # 各ファイルの出力結果の結合
            output_text += wav_to_text(wav_filepath) + '\n'
            os.remove(wav_filepath)
        # 文字起こし結果を保存する
        with open(self.text_filepath, 'w') as fp:
            fp.write(output_text)
        return output_text

    def clear_text(self):
        """
        mov_to_textで作った文字起こしファイルを削除する

        :return: None
        """
        os.remove(self.text_filepath)

    def movie_dividing(self,
                       threshold=0.05,
                       min_silence_duration=0.5,
                       padding_time=0.1,
                       ):
        """
        動画ファイルから無音部分をカットした部分動画ファイル群を作成する
        作成した動画のファイルパスリストを返す
        一時的にWaveファイルを作るが、使い終わったら削除する

        :param threshold: float 閾値
        :param min_silence_duration: float [秒]以上thresholdを下回っている個所を抽出する
        :param padding_time: float [秒]カットしない無音部分の長さ
        :return: list 分割したファイルのパスリスト
        """
        if len(self.movie_dividing_filepath) > 0:
            print('すでに動画ファイルから無音部分をカットした部分動画ファイル群を作成済みです')
            sys.exit()
        if not os.path.isfile(self.mov_to_wave()):
            print('動画から音声ファイルが作成できませんでした')
            sys.exit()
        # 音声ファイル読込
        data, frequency = sf.read(self.wave_filepath)  # file:音声ファイルのパス
        # 一定のレベル(振幅)以上の周波数にフラグを立てる
        amp = np.abs(data)
        list_over_threshold = amp > threshold

        # 一定時間以上、小音量が続く箇所を探す
        silences = []
        prev = 0
        entered = 0
        for i, v in enumerate(list_over_threshold):
            if prev == 1 and v == 0:  # enter silence
                entered = i
            if prev == 0 and v == 1:  # exit silence
                duration = (i - entered) / frequency
                if duration > min_silence_duration:
                    silences.append({"from": entered, "to": i, "suffix": "cut"})
                    entered = 0
            prev = v
        if 0 < entered < len(list_over_threshold):
            silences.append({"from": entered, "to": len(list_over_threshold), "suffix": "cut"})

        list_block = silences  # 無音部分のリスト：[{"from": 始点, "to": 終点}, {"from": ...}, ...]
        cut_blocks = [list_block[0]]
        for i, v in enumerate(list_block):
            if i == 0:
                continue
            moment = (v["from"] - cut_blocks[-1]["to"]) / frequency
            # カット対象だった場合
            if 0.3 > moment:
                cut_blocks[-1]["to"] = v["to"]  # １つ前のtoを書き換え
            # カット対象でない場合
            else:
                cut_blocks.append(v)  # そのまま追加

        # カットする箇所を反転させて、残す箇所を決める
        keep_blocks = []
        for i, block in enumerate(cut_blocks):
            if i == 0 and block["from"] > 0:
                keep_blocks.append({"from": 0, "to": block["from"], "suffix": "keep"})
            if i > 0:
                prev = cut_blocks[i - 1]
                keep_blocks.append({"from": prev["to"], "to": block["from"], "suffix": "keep"})
            if i == len(cut_blocks) - 1 and block["to"] < len(data):
                keep_blocks.append({"from": block["to"], "to": len(data), "suffix": "keep"})

        # list_keep 残す動画部分のリスト：[{"from": 始点, "to": 終点}, {"from": ...}, ...]
        for i, block in enumerate(keep_blocks):
            fr = max(block["from"] / frequency - padding_time, 0)
            to = min(block["to"] / frequency + padding_time, len(data) / frequency)
            duration = to - fr
            in_path = os.path.join(self.movie_value.target_dirname,
                                   "{}{}".format(self.movie_value.target_filename, self.movie_value.target_ext)
                                   )  # 入力する動画ファイルのパス
            out_path = os.path.join(self.movie_value.target_dirname,
                                    "{}_part{}{}".format(self.movie_value.target_filename,
                                                         str(i).zfill(3),
                                                         self.movie_value.target_ext
                                                         )
                                    )  # 出力する動画ファイルのパス
            self.movie_dividing_filepath.append(out_path)
            # 動画出力
            command_output = ["ffmpeg", "-i", in_path, "-ss", str(fr), "-t", str(duration), out_path]
            subprocess.run(command_output, shell=True, stdin=subprocess.DEVNULL)
        os.remove(self.wave_filepath)
        return self.movie_dividing_filepath

    def movie_dividing_to_text(self):
        """
        分割動画ファイル群から文字起こしして返す。ファイルにも保存する

        :return: tuple (list 分割動画ファイルパスのリストと, list 文字起こしリスト)を返す
        """
        txt = []
        for movie in self.movie_dividing_filepath:
            _mh = MovieHelper(movie)
            txt.append(_mh.mov_to_text())
        return self.movie_dividing_filepath, txt

    def clear_movie_dividing(self):
        """
        movie_dividingで作った動画ファイル群を削除する

        :return: None
        """
        for movie_filepath in self.movie_dividing_filepath:
            os.remove(movie_filepath)
        self.movie_dividing_filepath.clear()


def test01():
    """
    指定動画ファイルの(無音部分をカットした動画分割後に)文字起こし

    :return: None
    """
    mh = MovieHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/JPIC3316.MOV')
    mh.movie_dividing()
    mov, txt = mh.movie_dividing_to_text()
    for m, t in zip(mov, txt):
        print(m, ': ', t)
    # 生成ファイルを削除する
    for m in mov:
        _mh = MovieHelper(m)
        _mh.clear_text()
    mh.clear_movie_dividing()


def test02():
    """
    指定動画ファイルの文字起こし

    :return: None
    """
    mov = ['C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test/JPIC3316.MOV']
    _, m_h, m_t = movies_to_subtitles(mov)
    for m1, m2, t1 in zip(mov, m_h, m_t):
        print(m1, ': ', m2.movie_value.target_basename, ': ', t1)
    # 生成ファイルを削除する
    clear_movies_to_subtitles(m_h)


def test03():
    """
    指定ディレクトリ内のすべての動画文字起こし

    :return: None
    """
    target_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test'
    mov, m_h, m_t = movie_to_subtitles_in_directory(target_path)
    for m1, m2, t1 in zip(mov, m_h, m_t):
        print(m1, ': ', m2.movie_value.target_basename, ': ', t1)
    # 生成ファイルを削除する
    clear_movie_to_subtitles_in_directory(m_h)


if __name__ == '__main__':  # インポート時には動かない
    target_path = 'C:/Git/igapon50/traning/python/Movie/せんちゃんネル/test'
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のファイルパス
        target_path = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードから得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            target_path = paste_str
    else:
        print('引数が不正です。')
        sys.exit()
    print(target_path)

    test01()
    test02()
    test03()
