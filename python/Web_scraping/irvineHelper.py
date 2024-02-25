#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Irvineのヘルパー
## 説明
- Irvineを使ってurlリストのファイルをダウンロードする
    - urlリストを渡してIrvineHelperインスタンスを作る。urlリストはIrvineHelperのlist_pathのファイルに保存される
        - 既にurlリストがファイルになっていれば、そのファイルパスを渡してIrvineHelperインスタンスを作る
    - downloadメソッドを呼ぶ。list_pathのファイルを引数に、irvineを起動する
        - あらかじめIrvineの設定を行っておくこと

## Irvineの設定
- キューフォルダにフォーカスを当ててIrvineを終了しておく。Irvine起動時にフォーカスの当たっているキューフォルダにurlリストが追加される
- ダウンロードが終わったらIrvineを終了する
    - [オプション設定]-[イベント]-[OnDeactivateQueue]に新規作成で以下のスクリプトを書き込む
    - [全て終了時にIrvineを終了]をチェックする

## list_pathのファイルフォーマット
- タブ区切りフォーマット
    - URL
    - 保存フォルダ
    - 別名で保存
    - 以降不明(17フィールド)

doneclose.dms:
```
/*
スクリプト初期化データ
guid={3FD7CA4D-BB58-4E4E-B1EF-E66AA72E9685}
caption=全て終了時にIrvineを終了
version=0
hint=
event=OnDeactivateQueue
match=
author=
synchronize=0
*/

function OnDeactivateQueue(irvine){
//すべてのダウンロード終了イベント
irvine.ExecuteAction('actFileClose');
}
```

## 参考
- Irvine公式
    - http://hp.vector.co.jp/authors/VA024591/
- Irvineマニュアル
    - http://hp.vector.co.jp/authors/VA024591/doc/manual.html
- IrvineまとめWiki
    - https://w.atwiki.jp/irvinewiki/
- Irvineの設定
    - https://w.atwiki.jp/irvinewiki/pages/32.html
- Irvine Uploader
    - https://u1.getuploader.com/irvn/
- Irvine Part36スレ
    - https://mevius.5ch.net/test/read.cgi/win/1545612410
"""
# standard library
import sys  # 終了時のエラー有無
import os  # ファイルパス分解
import copy
import subprocess
import inspect
from itertools import zip_longest

# 3rd party packages
from dataclasses import dataclass

# local source

# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class IrvineHelperValue:
    """Irvineのヘルパーオブジェクト"""
    exe_path: str = r'c:\Program1\irvine1_3_0\irvine.exe'.replace(os.sep, '/')
    list_path: str = r'./irvine_download_list.txt'

    def __init__(self, exe_path=exe_path, list_path=list_path):
        """完全コンストラクタパターン
        :param exe_path: str Irvine.exeのパス
        :param list_path: str Irvineでダウンロードするファイルリストのファイルパス
        """
        if not exe_path or not os.path.isfile(exe_path):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:exe_path=[{exe_path}]")
        if not list_path or not os.path.isfile(list_path):
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:list_path=[{list_path}]")
        if exe_path:
            object.__setattr__(self, "exe_path", exe_path.replace(os.sep, '/'))
        if list_path:
            object.__setattr__(self, "list_path", list_path)


class IrvineHelper:
    """Irvineのヘルパー"""
    value_object: IrvineHelperValue or list = None
    download_path: str = None
    download_file_name_list: list = ['']
    exe_path: str = IrvineHelperValue.exe_path
    list_path: str = IrvineHelperValue.list_path
    running: bool = False

    def __init__(self,
                 value_object: IrvineHelperValue or list = value_object,
                 download_path: str = download_path,
                 download_file_name_list: list = None,
                 exe_path: str = exe_path,
                 list_path: str = list_path,
                 ):
        """コンストラクタ
        :param value_object:
            IrvineHelperValue 値オブジェクト
            または、list IrvineでダウンロードするURLリスト
        :param download_path: str ダウンロードするフォルダパス
        :param download_file_name_list: list 保存するファイル名リスト
        :param exe_path: str Irvine.exeのパス
        :param list_path: str IrvineでダウンロードするURLリストが列挙されたファイルへのパス
        """
        if download_file_name_list is None:
            download_file_name_list = self.download_file_name_list
        if isinstance(value_object, IrvineHelperValue):
            value_object = copy.deepcopy(value_object)
            self.value_object = value_object
        elif isinstance(value_object, list):
            value_object = copy.deepcopy(value_object)
            download_file_name_list = copy.deepcopy(download_file_name_list)
            with open(list_path, 'w', encoding='utf-8') as work_file:
                buff = ''
                for absolute_path, file_name in zip_longest(value_object, download_file_name_list):
                    buff += absolute_path + '\t'
                    if download_path:
                        buff += download_path
                    buff += '\t'
                    if file_name:
                        buff += file_name
                    buff += '\t' * 17
                    buff += '\n'
                work_file.write(buff)
            self.value_object = IrvineHelperValue(exe_path, list_path)
        else:
            raise ValueError(f"{self.__class__.__name__}.{inspect.stack()[1].function}"
                             f"引数エラー:value_object=[{self.value_object}]")

    def download(self):
        """
        irvineを起動して、終了されるのを待つ
        :return:
        """
        cmd = self.value_object.exe_path
        cmd += ' '
        cmd += self.value_object.list_path
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.running = True
        proc.wait()
        self.running = False
