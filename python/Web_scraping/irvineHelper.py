#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Irvineのヘルパー
"""
# standard library
import sys  # 終了時のエラー有無
import os  # ファイルパス分解
import subprocess

# 3rd party packages
from dataclasses import dataclass

# local source

# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class IrvineHelperValue:
    """
    Irvineのヘルパーオブジェクト
    """
    list_path: str = r'./irvine_download_list.txt'
    exe_path: str = r'c:\Program1\irvine1_3_0\irvine.exe'

    def __init__(self, list_path, exe_path=exe_path):
        """
        完全コンストラクタパターン
        :param list_path: str Irvineでダウンロードするファイルリストのファイルパス
        :param exe_path: str Irvine.exeのパス
        """
        if list_path:
            object.__setattr__(self, "list_path", list_path)
        if exe_path:
            object.__setattr__(self, "exe_path", exe_path)


class IrvineHelper:
    """
    Irvineのヘルパー
    """
    value_object: IrvineHelperValue = None
    running: bool = False
    list_path: str = r'./irvine_download_list.txt'

    def __init__(self, target_value=list_path, exe_path=None):
        """
        コンストラクタ
        :param target_value:
            list IrvineでダウンロードするURLリスト
            または、str IrvineでダウンロードするURLリストが列挙されたファイルへのパス
            または、IrvineHelperValue 値オブジェクト
        :param exe_path: str Irvine.exeのパス
        """
        if isinstance(target_value, IrvineHelperValue):
            self.value_object = target_value
        elif isinstance(target_value, str):
            if exe_path:
                self.value_object = IrvineHelperValue(target_value, exe_path)
            else:
                self.value_object = IrvineHelperValue(target_value)
        elif isinstance(target_value, list):
            with open(self.list_path, 'w', encoding='utf-8') as work_file:
                buff = ''
                for absolute_path in target_value:
                    buff += absolute_path + '\n'
                work_file.write(buff)
            if exe_path:
                self.value_object = IrvineHelperValue(self.list_path, exe_path)
            else:
                self.value_object = IrvineHelperValue(self.list_path)
        else:
            print('IrvineHelperで想定外の引数が指定された')
            exit()
        if not os.path.isfile(self.value_object.exe_path):
            print(f'Irvine.exeが見つかりません:{self.value_object.exe_path}')
            exit()
        if not os.path.isfile(self.value_object.list_path):
            print(f'ダウンロードファイルリストのファイルが見つかりません:{self.value_object.list_path}')
            exit()

    def download(self):
        """
        irvineを起動して、終了されるのを待つ
        :return:
        """
        cmd = self.value_object.exe_path
        cmd += ' '
        cmd += self.value_object.list_path
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()
