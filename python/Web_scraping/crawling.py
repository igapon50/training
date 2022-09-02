#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * downloadlist.txtから、URLを読み込んでスクレイピング＆ダウンロードする。
    * downloadlist.txtファイルに処理対象サイトURLを、一行に一URL記載しておく。
"""
import subprocess


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    load_path = './downloadlist.txt'
    with open(load_path, 'r', encoding='utf-8') as work_file:
        buff = work_file.readlines()
        for line in buff:
            target_url = line.rstrip('\n')
            # subprocess.run(['python', 'imgdl.py', target_url])

            # 画像が連番の場合、selenium
            subprocess.run(['python', 'urlDeployment.py', target_url])
