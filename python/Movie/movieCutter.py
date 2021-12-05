#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file movieCutter.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/05/03
# @brief 動画から音声のある部分だけ切り出す。
# @details 動画から音声のある部分だけ切り出す。
# @warning
# @note

from func import *

if __name__ == '__main__':  # インポート時には動かない
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のファイルパス
        target_filepath = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければデフォルト
        # 0は固定でスクリプト名
        target_filepath = DEFAULT_FILE_PATH
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit(False)
    print(target_filepath)

    # 動画から音声を切り出す
    basename = os.path.basename(target_filepath)
    target_filename = os.path.splitext(basename)[0]
    target_ext = os.path.splitext(basename)[1]
    if target_ext.lower() != '.mov':
        print('引数が不正です。ファイル拡張子movを指定してください')
        print(msg_error_exit)
        sys.exit(False)
    target_dirname = os.path.dirname(target_filepath)
    in_path = os.path.join(target_dirname, "{}{}".format(target_filename, target_ext))  # 入力する動画ファイルのパス
    out_path = os.path.join(target_dirname, "{}{}".format(target_filename, '.wav'))  # 出力する音声ファイルのパス
    # 動画出力
    command_output = ["ffmpeg", "-i", in_path, "-ac", "1", "-ar", "44100", "-acodec", "pcm_s16le", out_path]
    subprocess.run(command_output, shell=True, stdin=subprocess.DEVNULL)

    # ファイルのパスリストを作成
    filepath_list = []
    filename = []

    # 音声ファイル読込
    data, frequency = sf.read(out_path)  # file:音声ファイルのパス

    # 一定のレベル(振幅)以上の周波数にフラグを立てる
    threshold = 0.05  # 閾値
    amp = np.abs(data)
    list_overThreshold = amp > threshold

    # 一定時間以上、小音量が続く箇所を探す
    min_silence_duration = 0.5  # [秒]以上thresholdを下回っている個所を抽出する
    silences = []
    prev = 0
    entered = 0
    for i, v in enumerate(list_overThreshold):
        if prev == 1 and v == 0:  # enter silence
            entered = i
        if prev == 0 and v == 1:  # exit silence
            duration = (i - entered) / frequency
            if duration > min_silence_duration:
                silences.append({"from": entered, "to": i, "suffix": "cut"})
                entered = 0
        prev = v
    if 0 < entered < len(list_overThreshold):
        silences.append({"from": entered, "to": len(list_overThreshold), "suffix": "cut"})

    cut_blocks = []
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

    # 出力用テキストファイルパス
    padding_time = 0.1  # [秒]カットしない無音部分の長さ
    list_files_path = []

    # list_keep 残す動画部分のリスト：[{"from": 始点, "to": 終点}, {"from": ...}, ...]
    for i, block in enumerate(keep_blocks):
        fr = max(block["from"] / frequency - padding_time, 0)
        to = min(block["to"] / frequency + padding_time, len(data) / frequency)
        duration = to - fr
        in_path = os.path.join(target_dirname, "{}{}".format(target_filename, target_ext))  # 入力する動画ファイルのパス
        out_path = os.path.join(target_dirname, "{}_part{:2d}{}".format(target_filename, i, target_ext))  # 出力する動画ファイルのパス
        # 動画出力
        command_output = ["ffmpeg", "-i", in_path, "-ss", str(fr), "-t", str(duration), out_path]
        subprocess.run(command_output, shell=True, stdin=subprocess.DEVNULL)
