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
    exe_path: str = r'c:\Program1\irvine1_3_0\irvine.exe'
    list_path: str = r'./irvine_download_list.txt'

    def __init__(self, exe_path=exe_path, list_path=list_path):
        """
        完全コンストラクタパターン
        :param exe_path: str Irvine.exeのパス
        :param list_path: str Irvineでダウンロードするファイルリストのファイルパス
        """
        if exe_path:
            object.__setattr__(self, "exe_path", exe_path)
        if list_path:
            object.__setattr__(self, "list_path", list_path)


class IrvineHelper:
    """
    Irvineのヘルパー
    """
    value_object: IrvineHelperValue = None
    running: bool = False

    def __init__(self, target_value=None, list_path=None):
        """
        コンストラクタ
        :param target_value: list Irvine.exeのパス、または、IrvineHelperValue 値オブジェクト
        :param list_path: str Irvineでダウンロードするファイルリストのファイルパス
        """
        if isinstance(target_value, IrvineHelperValue):
            self.value_object = target_value
        elif isinstance(target_value, str):
            if list_path:
                self.value_object = IrvineHelperValue(target_value, list_path)
            else:
                self.value_object = IrvineHelperValue(target_value)
        else:
            self.value_object = IrvineHelperValue()
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
