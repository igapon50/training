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
import wave
import math
import struct
from pydub import AudioSegment
import pyperclip
import subprocess


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

    # コンストラクタ
    def __init__(self,
                 movie_value: 'MovieValue movieの値オブジェクト',
                 ):
        if movie_value is None:
            print('動画の値オブジェクトがNoneです')
            sys.exit(1)
        self.movie_value = movie_value
        self.movie_filepath = movie_value.target_filepath
        self.wave_filepath = os.path.join(self.movie_value.target_dirname,
                                          "{}{}".format(self.movie_value.target_filename, '.wav')
                                          )
        self.text_filepath = os.path.join(self.movie_value.target_dirname,
                                          "{}{}".format(self.movie_value.target_filename, '.txt')
                                          )

    # 動画ファイルから音声ファイルを作る
    def mov_to_wave(self):
        # パスの分解
        # このメソッドはmovファイルを対象とする
        if self.movie_value.target_ext.lower() != '.mov':
            print('ターゲットファイルの種類が不正です。ファイル拡張子movを指定してください')
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

    def cut_wave(self,
                 time: 'int 区切り時間[秒]' = 30
                 ):
        # timeの単位は[sec]
        # ファイルを読み出し
        source_audio = AudioSegment.from_wav(self.wave_filepath)
        # waveファイルが持つ性質を取得
        total_time = source_audio.duration_seconds
        integer = math.floor(total_time)  # 小数点以下切り捨て
        num_cut = int(integer // time)
        # wavファイルを削除
        os.remove(self.wave_filepath)
        outf_list = []
        for i in range(num_cut):
            # 出力データを生成
            outf = os.path.join(self.movie_value.target_dirname,
                                "{}{}".format(self.movie_value.target_filename + '_' + str(i).zfill(3), '.wav')
                                )
            start_cut = i * time * 1000
            end_cut = (i + 1) * time * 1000
            new_audio = source_audio[start_cut:end_cut]
            # 書き出し
            new_audio.export(outf, format="wav")
            # リストに追加
            outf_list.append(outf)
        return outf_list

    # 複数ファイルの音声のテキスト変換
    def cut_waves_str(self,
                      outf_list
                      ):
        output_text = ''
        # 複数処理
        print('音声のテキスト変換')
        for fwav in outf_list:
            print(fwav)
            r = sr.Recognizer()
            # 音声->テキスト
            with sr.AudioFile(fwav) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language='ja-JP')
            # 各ファイルの出力結果の結合
            output_text = output_text + text + '\n'
            # wavファイルを削除
            os.remove(fwav)
        return output_text

    # movからwavへの変換から音声のテキスト変換まで
    def mov_to_text(self):
        # 音声ファイルへの変換
        self.mov_to_wave()
        # 音声ファイルの分割(デフォルト30秒)
        cut_waves = self.cut_wave()
        # 複数ファイルの音声のテキスト変換
        out_text = self.cut_waves_str(cut_waves)
        # テキストファイルへの入力
        with open(self.text_filepath, 'w') as fp:
            fp.write(out_text)


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

    # 動画から音声を切り出す
    movie_value = MovieValue(target_file_path)
    mh = MovieHelper(movie_value)
    # 変換の実行
    mh.mov_to_text()
