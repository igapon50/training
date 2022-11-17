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
    exe_path: str = r'c:\Program1\irvine1_3_0\irvine.exe'.replace(os.sep, '/')
    list_path: str = r'./irvine_download_list.txt'

    def __init__(self, list_path=list_path, exe_path=exe_path):
        """
        完全コンストラクタパターン
        :param list_path: str Irvineでダウンロードするファイルリストのファイルパス
        :param exe_path: str Irvine.exeのパス
        """
        if list_path:
            object.__setattr__(self, "list_path", list_path)
        if exe_path:
            object.__setattr__(self, "exe_path", exe_path.replace(os.sep, '/'))


class IrvineHelper:
    """
    Irvineのヘルパー
    """
    list_path: str = IrvineHelperValue.list_path
    value_object: IrvineHelperValue = None
    running: bool = False

    def __init__(self, value_object=list_path, exe_path=None):
        """
        コンストラクタ
        :param value_object:
            IrvineHelperValue 値オブジェクト
            または、str IrvineでダウンロードするURLリストが列挙されたファイルへのパス
            または、list IrvineでダウンロードするURLリスト
        :param exe_path: str Irvine.exeのパス
        """
        if isinstance(value_object, IrvineHelperValue):
            self.value_object = value_object
        elif isinstance(value_object, str):
            if exe_path:
                self.value_object = IrvineHelperValue(value_object, exe_path.replace(os.sep, '/'))
            else:
                self.value_object = IrvineHelperValue(value_object)
        elif isinstance(value_object, list):
            with open(self.list_path, 'w', encoding='utf-8') as work_file:
                buff = ''
                for absolute_path in value_object:
                    buff += absolute_path + '\n'
                work_file.write(buff)
            if exe_path:
                self.value_object = IrvineHelperValue(self.list_path, exe_path.replace(os.sep, '/'))
            else:
                self.value_object = IrvineHelperValue(self.list_path)
        else:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:value_object=[{self.value_object}]")
        if not os.path.isfile(self.value_object.exe_path):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:exe_path=[{self.value_object.exe_path}]")
        if not os.path.isfile(self.value_object.list_path):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:list_path=[{self.value_object.list_path}]")

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
