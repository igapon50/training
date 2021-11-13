#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file movieCutter.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/11/13
# @brief 動画編集shotcutのプロジェクトファイルを編集するヘルパー。
# @details 。
# @warning
# @note

import os
import sys
import pyperclip
import xmltodict


##
# @brief 動画編集shotcutのプロジェクトファイルを編集するヘルパー。
# @details 内部では辞書型でデータを保持する。
# @warning
# @note
class ShotcutHelper:
    mlt_path: str = None
    xml_data: str = None
    yaml_data: str = None
#    json_data: str = None
    dict_data: dict = None

    # コンストラクタ
    def __init__(self,
                 mlt_path: 'str shotcutのプロジェクトファイルパス',
                 ):
        if mlt_path is not None:
            if os.path.isabs(mlt_path):
                object.__setattr__(self, "mlt_path", mlt_path)
            else:
                object.__setattr__(self, "mlt_path", os.path.abspath(mlt_path))
            self.initialize()

    # プロジェクトファイルをロードする
    def initialize(self):
        if os.path.isfile(self.mlt_path):
            with open(self.mlt_path, encoding='utf-8') as fp:
                self.xml_data = fp.read()
                # xml → dict
                self.dict_data = xmltodict.parse(self.xml_data)
#                print(self.dict_data)

    # shotcutプロジェクトファイルを保存する（ファイルがある場合は保存しない）
    def save_xml(self,
                 save_path: 'str xmlで保存するファイルパス',
                 ):
        if save_path is not None:
            if os.path.isabs(save_path):
                target_path = save_path
            else:
                target_path = os.path.abspath(save_path)
            if os.path.isfile(target_path):
                print('ファイルが存在します。xmlファイル保存を中止します。')
            else:
                with open(target_path, mode='w', encoding='utf-8') as fp:
                    # dict → xml , xmlの整形
                    self.xml_data = xmltodict.unparse(self.dict_data, pretty=True)
                    fp.write(self.xml_data)
                    # print(self.xml_data)


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
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            target_file_path = paste_str
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()
    print(target_file_path)
    shotcut1 = ShotcutHelper('C:/Git/igapon50/traning/python/Movie/せんちゃんネル/テンプレート.mlt')
    shotcut2 = ShotcutHelper('./せんちゃんネル/テンプレート.mlt')
    shotcut2.save_xml('C:/Git/igapon50/traning/python/Movie/test.mlt')
