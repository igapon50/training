#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
動画ファイルを扱うヘルパー
    * 無音部分をカットした動画生成
    * 文字起こし
* @author Ryosuke Igarashi(HN:igapon)
* @version 1.1.1
* @date 2022/1/1
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


def movie_folder(target_path):
    """
    指定フォルダ内の全てのmovファイルについて、無音部分をカットした動画に分割し、それぞれ文字起こしする

    :param target_path: 動画ファイルが含まれるパス
    :return: None
    """
    if not os.path.isdir(target_path):
        print('フォルダが存在しません。', target_path)
        sys.exit(False)
    _movie_list = glob.glob(os.path.join(target_path, '**/*.mov'), recursive=True)
    for _movie in _movie_list:
        _mh = MovieHelper(_movie)
        movie_dividing_list = _mh.movie_dividing()
        for movie_dividing in movie_dividing_list:
            _mh_dividing = MovieHelper(movie_dividing)
            _mh_dividing.mov_to_text()


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
        exit(1)
    print(wav_filepath)
    r = sr.Recognizer()
    # 音声->テキスト
    with sr.AudioFile(wav_filepath) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio, language='ja-JP')
        except Exception:
            text = '[文字起こしでエラー]'
    return text


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

    def __init__(self, movie_path):
        """
        コンストラクタ

        :param movie_path: str movieのファイルパス
        """
        if movie_path is None:
            print('動画ファイルパスがNoneです')
            sys.exit(1)
        if not os.path.isfile(movie_path):
            print(movie_path, '動画ファイルが存在しません', sep=':')
            sys.exit(1)
        object.__setattr__(self, "target_filepath", movie_path)
        target_basename = os.path.basename(movie_path)
        object.__setattr__(self, "target_basename", target_basename)
        target_dirname = os.path.dirname(movie_path)
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
            sys.exit(1)
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

        :return: 音声ファイルパス
        """
        # パスの分解
        if self.movie_value.target_ext.lower() != '.mov':
            print(self.movie_value.target_ext.lower(),
                  'ターゲットファイルの種類が不正です。ファイル拡張子movのファイルを指定してください',
                  sep=':')
            sys.exit(1)
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

        :param time: int 区切る時間[秒]
        :return: 分割した音声ファイルのパスリスト
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

        :return: 文字起こし結果の文字列
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

    def movie_dividing(self,
                       threshold=0.05,
                       min_silence_duration=0.5,
                       padding_time=0.1,
                       ):
        """
        動画から音声ファイルを作成して、無音部分をカットした部分動画群を作成する
        作成した動画のファイルパスリストを返す

        :param threshold: float 閾値
        :param min_silence_duration: float [秒]以上thresholdを下回っている個所を抽出する
        :param padding_time: float [秒]カットしない無音部分の長さ
        :return: 分割したファイルのパスリスト
        """
        if not os.path.isfile(self.mov_to_wave()):
            print('動画から音声ファイルが作成できませんでした')
            sys.exit(1)
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

        self.movie_dividing_filepath.clear()
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
        sys.exit(1)
    print(target_path)

    # 指定フォルダ内のすべての動画文字起こし
    movie_folder(target_path)
