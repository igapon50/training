#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""uriのヘルパー
https://pypi.org/project/python-datauri/
https://github.com/fcurella/python-datauri/tree/py3

参考：
https://qiita.com/TsubasaSato/items/908d4f5c241091ecbf9b
"""
import copy
import sys

# 3rd party packages
from urllib.parse import *  # URLパーサー
from dataclasses import dataclass
from datauri import DataURI


@dataclass(frozen=True)
class UriHelperValue:
    """Uriヘルパー値オブジェクト"""
    uri: str = None

    def __init__(self,
                 uri: str = uri,
                 ):
        """完全コンストラクタパターン"""
        if not uri:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:uri=None")
        if not self.is_uri_only(uri):
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:uriがURIではない[{uri}]")
        object.__setattr__(self, "uri", uri)

    @staticmethod
    def is_uri_only(string: str) -> bool:
        return len(urlparse(string).scheme) > 0


class UriHelper:
    """Uriのヘルパー"""
    value_object: UriHelperValue or str = None

    def __init__(self,
                 value_object: UriHelperValue or str = value_object,
                 ):
        """値オブジェクトからの復元、
        または、uriより、値オブジェクトを作成する
        :param value_object: list 対象となるURI、または、値オブジェクト
        """
        if value_object:
            if isinstance(value_object, UriHelperValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
            elif isinstance(value_object, str):
                uri = value_object
                self.value_object = UriHelperValue(uri)
            else:
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:value_object=None")

    @staticmethod
    def is_data_uri(url: str) -> bool:
        """Data URIのjpeg画像かつbase64であればTrue
        :return: bool
        """
        if urlparse(url).scheme == 'data':
            uri = DataURI(url)
            if len(uri.mimetype) > 0:
                return True
        return False

    @staticmethod
    def is_jpeg_data_uri(url: str) -> bool:
        """Data URIのjpeg画像かつbase64であればTrue
        :return: bool
        """
        if urlparse(url).scheme == 'data':
            uri = DataURI(url)
            if uri.mimetype in ['image/jpeg']:
                if uri.is_base64:
                    return True
        return False

    @staticmethod
    def is_png_data_uri(url: str) -> bool:
        """Data URIのpng画像かつbase64であればTrue
        :return: bool
        """
        if urlparse(url).scheme == 'data':
            uri = DataURI(url)
            if uri.mimetype in ['image/png']:
                if uri.is_base64:
                    return True
        return False

    def get_uri(self):
        """URIを得る
        :return: str URI
        """
        return copy.deepcopy(self.value_object.uri)

    def get_data_uri(self):
        return DataURI(self.get_uri())

    def get_data(self):
        uri = self.get_data_uri()
        return uri.data

    def save_data_uri(self, target_file):
        with open(target_file, "wb") as image_file:
            image_file.write(self.get_data())

    def is_enable_filename(self):
        """ファイル名が使用可能ならTrue
        TODO: 改良の余地あり
        :return:
        """
        if self.is_data_uri(self.get_uri()):
            return False
        if not self.get_filename():
            return False
        if not self.get_ext():
            return False
        return True

    def get_filename(self):
        """ファイル名を得る
        :return: str ファイル名(拡張子除く)
        """
        if self.is_jpeg_data_uri(self.get_uri()):
            return None
        else:
            # TODO: URIにファイル名ない時もある
            __parse = urlparse(self.get_uri())
            __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
            __base_name = __path_after_name[:__path_after_name.rfind('.')]
            return copy.deepcopy(__base_name)

    def get_ext(self):
        """拡張子を得る
        :return: str ファイルの拡張子(ドットを含む)
        """
        if self.is_jpeg_data_uri(self.get_uri()):
            return '.jpg'
        if self.is_png_data_uri(self.get_uri()):
            return '.png'
        else:
            # TODO: URIに拡張子ない時もある
            __parse = urlparse(self.get_uri())
            __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
            __extend_name = __path_after_name[__path_after_name.rfind('.'):]
            return copy.deepcopy(__extend_name)
