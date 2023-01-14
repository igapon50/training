#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルのヘルパー
"""
import os

# 3rd party packages
import requests  # HTTP通信
import shutil

from uriHelper import *


@dataclass(frozen=True)
class WebFileHelperValue:
    """webファイルヘルパー値オブジェクト"""
    url: UriHelper = None
    download_file_name: str = None
    start_ext: str = '.jpg'
    download_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'download').replace(os.sep, '/')

    def __init__(self,
                 url: UriHelper = url,
                 download_file_name: str = download_file_name,
                 start_ext: str = start_ext,
                 download_path: str = download_path,
                 ):
        """完全コンストラクタパターン"""
        if not url:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:url=None")
        if not download_file_name:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:download_file_name=None")
        if not start_ext:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:start_ext=None")
        if not download_path:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:download_path=None")
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "download_file_name", download_file_name)
        object.__setattr__(self, "start_ext", start_ext)
        object.__setattr__(self, "download_path", download_path.replace(os.sep, '/'))


class WebFileHelper:
    """webファイルのヘルパー"""
    value_object: WebFileHelperValue or UriHelper or str = None
    download_file_name: str = None
    start_ext: str = WebFileHelperValue.start_ext
    download_path: str = WebFileHelperValue.download_path

    # ext_list: list = ['.jpg', '.png', '.jpeg', '.webp', '.svg', '.svgz', '.gif', '.tif', '.tiff', '.psd', '.bmp']
    ext_list: list = [WebFileHelperValue.start_ext, '.png', '.gif']  # これを画像とする
    ext_dict: dict = {ext_list[0]: ext_list,
                      ext_list[1]: [ext_list[1], ext_list[0], ext_list[2]],
                      ext_list[2]: [ext_list[2], ext_list[0], ext_list[1]],
                      }

    def __init__(self,
                 value_object: WebFileHelperValue or UriHelper or str = value_object,
                 download_file_name: str = download_file_name,
                 start_ext: str = start_ext,
                 download_path: str = download_path,
                 ):
        """値オブジェクトからの復元、
        または、urlとfolder_pathより、値オブジェクトを作成する
        """
        if value_object:
            if isinstance(value_object, WebFileHelperValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
            elif isinstance(value_object, UriHelper):
                uri = copy.deepcopy(value_object)
                if not download_file_name:
                    if uri.is_enable_filename():
                        download_file_name = uri.get_filename()
                    else:
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:download_file_name=None")
                if not start_ext:
                    if uri.is_enable_filename():
                        start_ext = uri.get_ext()
                    else:
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:start_ext=None")
                if not download_path:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:download_path=None")
                self.value_object = WebFileHelperValue(uri, download_file_name, start_ext, download_path)
            elif isinstance(value_object, str):
                url = value_object
                uri = UriHelper(url)
                if not download_file_name:
                    if uri.is_enable_filename():
                        download_file_name = uri.get_filename()
                    else:
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:download_file_name=None")
                if not start_ext:
                    if uri.is_enable_filename():
                        start_ext = uri.get_ext()
                    else:
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:start_ext=None")
                if not download_path:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:download_path=None")
                self.value_object = WebFileHelperValue(uri, download_file_name, start_ext, download_path)
            else:
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:value_object=None")

    @staticmethod
    def fixed_path(file_path: str) -> str:
        """フォルダ名の禁止文字を全角文字に置き換える
        :param file_path: str 置き換えたいフォルダパス
        :return: str 置き換え後のフォルダパス
        """
        __file_path = copy.deepcopy(file_path)
        __file_path = __file_path.replace(':', '：')
        __file_path = __file_path.replace('*', '＊')
        __file_path = __file_path.replace('?', '？')
        __file_path = __file_path.replace('"', '”')
        __file_path = __file_path.replace('<', '＜')
        __file_path = __file_path.replace('>', '＞')
        __file_path = __file_path.replace('|', '｜')
        return __file_path

    @staticmethod
    def fixed_file_name(file_name: str) -> str:
        """ファイル名の禁止文字を全角文字に置き換える
        :param file_name: str 置き換えたいファイル名
        :return: str 置き換え後のファイル名
        """
        __file_name = copy.deepcopy(file_name)
        __file_name = __file_name.replace(os.sep, '￥')
        __file_name = __file_name.replace('/', '／')
        return WebFileHelper.fixed_path(__file_name)

    @staticmethod
    def is_jpeg_data_uri(url):
        """Data URIのjpeg画像かつbase64であればTrue
        :return: bool
        """
        if urlparse(url).scheme == 'data':
            uri = DataURI(url)
            if uri.mimetype in ['image/jpeg']:  # 'image/png']:
                if uri.is_base64:
                    return True
        return False

    def is_image(self):
        """画像か判定する(ext_listにある拡張子か調べる)
        :return: bool
        """
        __parse = urlparse(self.get_url())
        for __ext in self.ext_list:
            offset = len(__ext)
            if __parse.path[-offset:].lower() == __ext:
                return True
        return False

    def is_exist(self):
        """ファイルがローカルに存在すればTrueを返す
        urlでダウンロードしたファイル、変名した後のファイルをチェックする
        :return: bool
        """
        if os.path.isfile(self.get_path()):
            # 変名後のファイルがある
            return True
        url = self.value_object.url
        if url.is_enable_filename():
            file_path = os.path.join(self.download_path, url.get_filename() + url.get_ext())
            if os.path.isfile(file_path):
                return True
        return False

    def get_value_object(self):
        """valueオブジェクトを得る
        """
        return copy.deepcopy(self.value_object)

    def get_url(self):
        """URLを得る
        :return: str URL
        """
        return copy.deepcopy(self.value_object.url.get_uri())

    def get_download_path(self):
        """ダウンロードパスを得る
        :return: str download_path
        """
        return copy.deepcopy(self.value_object.download_path)

    def get_download_file_name(self):
        """ダウンロードファイル名を得る
        :return: str download_file_name
        """
        return copy.deepcopy(self.value_object.download_file_name)

    def get_start_ext(self):
        """開始時の拡張子を得る
        :return: str ファイルの拡張子(ドットを含む)
        """
        return copy.deepcopy(self.value_object.start_ext)

    def get_path(self):
        """現在のフルパスを得る
        :return: str ファイルのフルパス(セパレータはスラッシュ)
        """
        return copy.deepcopy(os.path.join(self.get_download_path(),
                                          self.get_filename() + self.get_ext(),
                                          ).replace(os.sep, '/'))

    def get_filename(self):
        """現在のファイル名を得る
        :return: str ファイル名(拡張子除く)
        """
        download_file_name = self.get_download_file_name()
        if not download_file_name:
            download_file_name = self.value_object.url.get_filename()
        return copy.deepcopy(download_file_name)

    def get_ext(self):
        """現在の拡張子を得る
        :return: str ファイルの拡張子(ドットを含む)
        """
        ext = self.value_object.url.get_ext()
        return copy.deepcopy(ext)

    def rename_url_ext_shift(self):
        """urlの画像拡張子を、ext_listの次の拡張子にシフトする
        現在の拡張子はext_listの何番目か調べて、次の拡張子にurlを変更して、値オブジェクトを作り直す
        :return:
        """
        if not self.is_image():
            print('画像じゃないので処理をスキップ')
        else:
            __index = self.ext_dict[self.get_start_ext()].index(self.get_ext())
            __index = (__index + 1) % len(self.ext_dict[self.get_start_ext()])
            __ext = self.ext_dict[self.get_start_ext()][__index]
            # [::-1] 配列を逆順にする
            __url = self.get_url()[::-1].replace(self.get_ext()[::-1], __ext[::-1])[::-1]
            self.value_object = WebFileHelperValue(UriHelper(__url),
                                                   self.get_filename(),
                                                   self.get_start_ext(),
                                                   self.get_download_path(),
                                                   )

    def download_requests(self):
        """requestsを用いて、ファイルをダウンロードする
        :return: bool 成功/失敗=True/False
        """
        # フォルダーがなければ作成する
        if not os.path.isdir(self.get_download_path()):
            os.makedirs(self.get_download_path())
        try:
            if not self.is_exist():
                images = self.get_image_content_by_requests()
                with open(self.get_path(), "wb") as img_file:
                    img_file.write(images)
            else:
                print('Skip ' + self.get_path())
        except KeyboardInterrupt:
            print("キーボード割込み")
        except Exception as err:
            print(self.get_url() + ' ', end='')  # 改行なし
            print(err)
            return False
        return True

    def get_image_content_by_requests(self, timeout=30):
        """requestsを用いて、imageのコンテンツを取得する。
        サーバー落ちているとリダイレクトでエラー画像になることがあるのでリダイレクトFalse
        :param timeout: int タイムアウト時間[s]
        :return: bytes 読み込んだimageのバイナリデータ
        """
        response = requests.get(self.get_url(), allow_redirects=False, timeout=timeout)
        if response.status_code != requests.codes.ok:
            e = Exception("HTTP status: " + str(response.status_code))  # + " " + file_url + " " + response.url)
            raise e
        content_type = response.headers["content-type"]
        if 'image' not in content_type:
            e = Exception("Content-Type: " + content_type)  # + " " + file_url + " " + response.url)
            raise e
        return response.content

    def rename_filename(self, new_file_name):
        """dst_filenameに設定して、ローカルにあるファイルのファイル名も変更する
        TODO: dst_file_nameにセットするときは、download_file_nameでvalue_objectを作り直すべきか
        :param new_file_name: str 変更する新しいファイル名
        :return: bool True/False=変更(した/しなかった)
        """
        if not self.is_exist():
            print('ファイルがローカルにないので処理をスキップします')
            return False
        else:
            dst_path = os.path.join(self.get_download_path(), new_file_name + self.get_ext())
            if os.path.isfile(dst_path):
                print(f'リネームファイル[{dst_path}]が存在しています')
                return False
            os.rename(self.get_path(), dst_path)
            self.download_file_name = new_file_name
            self.value_object = WebFileHelperValue(UriHelper(self.get_url()),
                                                   self.get_filename(),
                                                   self.get_start_ext(),
                                                   self.get_download_path(),
                                                   )
        return True

    def delete_local_file(self):
        """ローカルのファイルを削除する
        :return: None
        """
        if os.path.isfile(self.get_path()):
            os.remove(self.get_path())
        url = self.value_object.url
        if url.is_enable_filename():
            file_path = os.path.join(self.download_path, url.get_filename() + url.get_ext())
            if os.path.isfile(file_path):
                os.remove(file_path)

    def move(self, new_path):
        """ファイルを移動する(get_download_path()は変わらない)
        :param new_path: 移動先のフォルダーパス
        :return:
        """
        if self.is_exist():
            # TODO: 移動先のフォルダに同名のファイルが存在する場合の対応
            # TODO: new_pathが存在しない場合
            shutil.move(self.get_path(), new_path)
        else:
            print('ローカルファイルが不足しているため、ファイルの移動を中止した')

    def get_deployment_url_list(self):
        """ナンバリングされたURLであれば、数字部分を末尾とした、URL展開してURLリスト=url_listを作る
        TODO: ナンバリングのチェック、1000以上ならエラーにするなど
        :return: list 展開した画像URLリスト
        """
        __parse = urlparse(self.get_url())
        # pathを/前後で分ける
        __path_before_name = __parse.path[:__parse.path.rfind('/') + 1]
        __path_after_name = __parse.path[__parse.path.rfind('/') + 1:]
        print(__path_before_name)
        print(__path_after_name)
        # path_after_nameを.前後で分ける
        __base_name = __path_after_name[:__path_after_name.rfind('.')]
        __extend_name = __path_after_name[__path_after_name.rfind('.'):]
        print(__base_name)
        print(__extend_name)
        if not __base_name.isdecimal():
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"エラー:urlがナンバリングされていない[{__base_name}]")
        __count = int(__base_name)
        url_list = []
        for d_count in range(__count):
            url_list.append(urlunparse((__parse.scheme,
                                        __parse.netloc,
                                        __path_before_name + str(d_count + 1) + __extend_name,
                                        __parse.params,
                                        __parse.query,
                                        __parse.fragment)))
        return url_list
