#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file movieHelper.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/12/12
# @brief 動画の音声について文字お起こしする。
# @details 動画の音声について文字起こしする。
# @warning
# @note

import sys  # 終了時のエラー有無
import os  # ファイルパス分解
from dataclasses import dataclass

import speech_recognition as sr
import math
import numpy as np
from pydub import AudioSegment
import pyperclip
import subprocess
import soundfile as sf


##
# @brief Value Objects
# @details 動画の値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class MovieValue:
    target_filepath: 'str 対象のファイルパス'
    target_basename: 'str 対象のファイル名+拡張子'
    target_dirname: 'str 対象のディレクトリ'
    target_filename: 'str 対象のファイル名'
    target_ext: 'str 対象の拡張子'

    # コンストラクタ
    def __init__(self,
                 movie_path: 'str movieのファイルパス',
                 ):
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
    movie_value: 'MovieValue movieの値オブジェクト'
    movie_filepath: 'str 動画ファイル入力パス'
    wave_filepath: 'str 音声ファイル出力パス'
    text_filepath: 'str 文字起こし出力パス'
    movie_dividing_filepath: 'list 分割動画ファイル出力パスリスト'

    # コンストラクタ
    def __init__(self,
                 movie_value,  # str movieのファイルパス、または、MovieValue movieの値オブジェクト
                 ):
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

    # 動画ファイルから音声ファイルを作る
    def mov_to_wave(self):
        # パスの分解
        # このメソッドはmovファイルを対象とする
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

    # 音声ファイルを消費して、指定秒数単位に分割した音声ファイルを作り、そのパスリストを返す
    def _split_wave(self,
                    time: 'int 区切る時間[秒]' = 30
                    ):
        # ファイルを読み込み
        source_audio = AudioSegment.from_wav(self.wave_filepath)
        # waveファイルの情報を取得
        total_time = source_audio.duration_seconds
        integer = math.floor(total_time)  # 小数点以下切り下げ
        num_cut = math.ceil(integer / time)  # 小数点以下切り上げ
        # TODO 別の場所に移動する
        #  wavファイルを削除
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

    # 分割した音声ファイルを消費して、文字起こし結果を返す
    def _split_waves_str(self,
                         input_file_list: 'list 音声ファイルパスリスト'
                         ):
        output_text = ''
        # 複数処理
        print('音声のテキスト変換')
        for fwav in input_file_list:
            print(fwav)
            r = sr.Recognizer()
            # 音声->テキスト
            with sr.AudioFile(fwav) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language='ja-JP')
            # 各ファイルの出力結果の結合
            output_text += text + '\n'
            # TODO 別の場所に移動する。
            #  wavファイルを削除
            os.remove(fwav)
        return output_text

    # 動画ファイルの文字起こし
    def mov_to_text(self):
        # 動画ファイルから音声ファイルを作る
        self.mov_to_wave()
        # 音声ファイルを消費して、指定秒数単位に分割した音声ファイルを作り、そのパスリストを返す
        split_waves = self._split_wave()
        # 分割した音声ファイルを消費して、文字起こし結果を返す
        out_text = self._split_waves_str(split_waves)
        # 文字起こし結果を保存する
        with open(self.text_filepath, 'w') as fp:
            fp.write(out_text)
        return out_text

    # 動画から音声ファイルを作成して、無音部分をカットした部分動画群を作成する
    # 作成した動画のファイルパスリストを返す
    def movie_dividing(self,
                       threshold: 'float 閾値' = 0.05,
                       min_silence_duration:  'float [秒]以上thresholdを下回っている個所を抽出する' = 0.5,
                       padding_time: 'float [秒]カットしない無音部分の長さ' = 0.1,
                       ):
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
        return self.movie_dividing_filepath


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
    else:
        print('引数が不正です。')
        sys.exit(1)
    print(target_file_path)

    # 文字起こし
    mh = MovieHelper(target_file_path)
    mh.mov_to_text()
    # 無音部分をカットした動画分割して、文字起こし
    movie_list = mh.movie_dividing()
    for movie in movie_list:
        mh_dividing = MovieHelper(movie)
        mh_dividing.mov_to_text()
