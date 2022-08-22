#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クローリング
    * urlDeployment_list.txtから、URLを読み込んでスクレイピング＆ダウンロードする。
    * urlDeployment_list.txtファイルに処理対象サイトURLとタイトルを、一行に一URLと一タイトルをカンマ区切りで記載する。
"""
import subprocess


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    load_path = './urlDeployment_list.txt'
    with open(load_path, 'r', encoding='utf-8') as work_file:
        buff = work_file.readlines()
        for count, line in enumerate(buff):
            target_url, target_title = line.rstrip('\n').split(',')
            # requests-html
            # subprocess.run(['python', 'imgdl.py', target_url])
            if not target_title:
                target_title = f'[] {count}'
            # URLが画像連番の末尾の場合、
            subprocess.run(['python', 'urlDeployment.py', target_url, target_title])
