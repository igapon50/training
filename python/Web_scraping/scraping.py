#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スクレイピングユーティリティ
    * サイトURLと、selectorsを指定して、スクレイピングする
"""
# standard library
# 3rd party packages
import pickle
import sys
import copy
import pyperclip  # クリップボード
from dataclasses import dataclass
import json
from selenium.webdriver.common.by import By
# local source

# 最大再起回数を1万回にする
sys.setrecursionlimit(10000)


@dataclass(frozen=True)
class ScrapingValue:
    """値オブジェクト"""
    site_url: str = None
    selectors: dict = None

    def __init__(self, site_url, selectors):
        """完全コンストラクタパターン
        :param site_url: list 処理対象サイトURL
        :param selectors: list スクレイピングする際のXPATH
        """
        if not site_url:
            raise ValueError(f"{self.__class__}引数エラー:site_url=None")
        if not selectors:
            raise ValueError(f"{self.__class__}引数エラー:selectors=None")
        if not isinstance(site_url, str):
            raise ValueError(f"{self.__class__}引数エラー:site_urlがstrではない")
        if not isinstance(selectors, dict):
            raise ValueError(f"{self.__class__}引数エラー:selectorsがdictではない")
        object.__setattr__(self, "site_url", site_url)
        object.__setattr__(self, "selectors", selectors)


class Scraping:
    """スクレイピングのユーティリティ"""
    value_object: ScrapingValue = None

    def __init__(self, value_object=None, selectors=None):
        if value_object:
            if isinstance(value_object, ScrapingValue):
                self.value_object = value_object
            elif isinstance(value_object, str):
                if selectors:
                    self.value_object = ScrapingValue(value_object, selectors)
                else:
                    raise ValueError(f"{self.__class__}引数エラー:selectors=None")
            else:
                raise ValueError(f"{self.__class__}引数エラー:selectorsがstrではない")
        else:
            raise ValueError(f"{self.__class__}引数エラー:value_object=None")

    def get_value_objects(self):
        """値オブジェクトを取得する"""
        return copy.deepcopy(self.value_object)

    def create_save_text(self):
        """保存用文字列の作成
        :return: str 保存用文字列の作成
        """
        buff = json.dumps(self.value_object.site_url, ensure_ascii=False) + '\n'  # サイトURL追加
        buff += json.dumps(self.value_object.selectors, ensure_ascii=False) + '\n'  # セレクタ追加
        return buff

    def clip_copy(self):
        """クローリング結果をクリップボードにコピーする
        :return: bool 成功/失敗=True/False
        """
        if not self.value_object:
            return False
        buff = self.create_save_text()
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True

    def save_text(self, save_path):
        """データをファイルに、以下の独自フォーマットで保存する
            * サイトURL
            * セレクタ
        :param save_path: str セーブする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if not self.value_object:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.create_save_text()
            work_file.write(buff)
            return True

    def load_text(self, load_path):
        """独自フォーマットなファイルからデータを読み込む
        :param load_path: str ロードする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            __site_url = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            __selectors = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.value_object = ScrapingValue(__site_url, __selectors,)
            return True

    def save_pickle(self, save_path):
        """シリアライズしてpickleファイルに保存する
        :param save_path: str セーブするpickleファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if not save_path:
            return False
        with open(save_path, 'wb') as work_file:
            pickle.dump(self.value_object, work_file)
            return True

    def load_pickle(self, load_path):
        """pickleファイルを読み込み、デシリアライズする
        :param load_path: str ロードするpickleファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if not load_path:
            return False
        with open(load_path, 'rb') as work_file:
            self.value_object = pickle.load(work_file)
            return True
