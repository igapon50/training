#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルリストのヘルパー
"""
import datetime
import zipfile  # zipファイル
from distutils.util import strtobool

from irvineHelper import *
from chromeDriverHelper import *
from webFileHelper import *


@dataclass(frozen=True)
class WebFileListHelperValue:
    """値オブジェクト"""
    web_file_list: list = None
    work_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'work').replace(os.sep, '/')
    archive_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'archive').replace(os.sep, '/')

    def __init__(self,
                 web_file_list: list = None,
                 work_path: str = work_path,
                 archive_path: str = archive_path,
                 ):
        """完全コンストラクタパターン"""
        if not web_file_list:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:web_file_list=None")
        for count, item in enumerate(web_file_list):
            if not isinstance(item, WebFileHelper):
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:web_file_listの{count}個目がWebFileHelperで無い")
        object.__setattr__(self, "web_file_list", web_file_list)
        object.__setattr__(self, "work_path", work_path)
        object.__setattr__(self, "archive_path", archive_path)


class WebFileListHelper:
    """webファイルリスト"""
    value_object: WebFileListHelperValue or list = None
    start_ext: str = WebFileHelper.start_ext
    download_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'download').replace(os.sep, '/')
    work_path: str = WebFileListHelperValue.work_path
    archive_path: str = WebFileListHelperValue.archive_path

    def __init__(self,
                 value_object: WebFileListHelperValue or list = value_object,
                 start_ext: str = start_ext,
                 download_path: str = download_path,
                 work_path: str = work_path,
                 archive_path: str = archive_path,
                 ):
        """値オブジェクトからの復元、
        または、Webファイルのヘルパー: list[WebFileHelper]と、ファイル名、拡張子名、各種pathより、値オブジェクトを作成する
        または、url: list[str]と、ファイル名、拡張子名、各種pathより、値オブジェクトを作成する
        """
        if value_object:
            if isinstance(value_object, WebFileListHelperValue):
                value_object = copy.deepcopy(value_object)
                self.value_object = value_object
            elif isinstance(value_object, list):
                if not download_path:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:download_path=None")
                if not work_path:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:work_path=None")
                if not archive_path:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:archive_path=None")
                value_object = copy.deepcopy(value_object)
                web_file_list = []
                isinstance_list = [isinstance(val, WebFileHelper) for val in value_object]
                isinstance_str = [isinstance(val, str) for val in value_object]
                if sum(isinstance_list):
                    if sum(isinstance_list) != len(isinstance_list):
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:value_objectの型list[WebFileHelper]ではない")
                    else:
                        web_file_list = value_object
                elif sum(isinstance_str):
                    if sum(isinstance_str) != len(isinstance_str):
                        raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                         f"引数エラー:value_objectの型list[str]ではない")
                    else:
                        # TODO: urlには、DataURIやURLが混ざってくる。URLには、ファイル名がない場合もある
                        for index, url in enumerate(value_object):
                            uri = UriHelper(url)
                            download_file_name = '{:04d}'.format(index)
                            __start_ext = start_ext
                            if not __start_ext:
                                __start_ext = uri.get_ext()
                            web_file = WebFileHelper(uri, download_file_name, __start_ext, download_path)
                            web_file_list.append(web_file)
                else:
                    raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                     f"引数エラー:value_objectの型")
                self.value_object = WebFileListHelperValue(web_file_list,
                                                           work_path,
                                                           archive_path)
            else:
                raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                                 f"引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name}"
                             f"引数エラー:value_object=None")

    def get_web_file_list(self):
        """webファイルリストを得る
        :return: list[WebFileHelper]
        """
        return copy.deepcopy(self.value_object.web_file_list)

    def get_path_list(self):
        """ファイルパスのリストを得る
        :return: list[str]
        """
        __paths = []
        for __web_file in self.get_web_file_list():
            __paths.append(__web_file.get_path())
        return copy.deepcopy(__paths)

    def get_url_list(self):
        """URLのリストを得る
        :return: list[str]
        """
        __urls = []
        for __web_file in self.get_web_file_list():
            __urls.append(__web_file.get_url())
        return copy.deepcopy(__urls)

    def get_only_url_of_file_not_exist(self):
        """ローカルにファイルがないURLだけのリストを得る
        :return: list[str]
        """
        __url_list = []
        for file in self.value_object.web_file_list:
            if not file.is_exist():
                __url_list.append(file.get_url())
        return copy.deepcopy(__url_list)

    def get_folder_path_from_1st_element(self):
        """ファイルリストの一つ目に登録されているフォルダーパスを得る
        :return: str
        """
        return copy.deepcopy(self.get_web_file_list()[0].get_download_path())

    def is_exist(self):
        """ファイルリストの全ファイルがローカルに存在する
        :return: bool 全てのファイルが存在すればTrueを返す
        """
        for __web_file in self.get_web_file_list():
            if not __web_file.is_exist():
                return False
        return True

    def download_requests(self):
        """requestsを用いて、ファイルリストをダウンロードする
        :return:
        """
        for __web_file in self.get_web_file_list():
            __web_file.download_requests()

    def download_irvine(self):
        """irvineを用いて、ファイルリストをダウンロードする
        :return:
        """
        __irvine = IrvineHelper(self.get_url_list())
        __irvine.download()

    def download_chrome_driver(self):
        """selenium chromeDriverを用いて、画像をデフォルトダウンロードフォルダにダウンロードして、指定のフォルダに移動する
        :return:
        """
        __driver = ChromeDriverHelper()
        for __url in self.get_url_list():
            __driver.download_image(__url)
        downloads_path = os.path.join(os.getenv("HOMEDRIVE"), os.getenv("HOMEPATH"), "downloads")
        __web_file_list = WebFileListHelper(self.get_url_list(), downloads_path)
        __web_file_list.move(self.get_folder_path_from_1st_element())

    def rename_url_ext_shift(self):
        """ファイルリストの各ファイルについて、ローカルに存在しないファイルの拡張子をシフトし、ファイルリストを更新する
        :return: None
        """
        for __count, __web_file_helper in enumerate(self.value_object.web_file_list):
            if not __web_file_helper.is_exist():
                __web_file_helper.rename_url_ext_shift()

    def rename_filenames(self):
        """ファイルリストの各ファイルについて、ローカルに存在するファイルのファイル名をナンバリングファイル名に変更し、ファイルリストを更新する
        :return: bool 成功/失敗=True/False
        """
        for __count, __web_file_helper in enumerate(self.value_object.web_file_list):
            if __web_file_helper.is_exist():
                if not __web_file_helper.rename_filename('{:04d}'.format(__count)):
                    return False
        return True

    def make_zip_file(self):
        """ファイルリストのファイルについて、一つの圧縮ファイルにする
        圧縮ファイルが既に存在する場合は変名してから圧縮する
        :return: bool 成功/失敗=True/False
        """
        if not self.is_exist():
            return False
        __zip_folder = self.get_folder_path_from_1st_element()
        if os.path.isfile(__zip_folder + '.zip'):
            __now_str = datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')
            os.rename(__zip_folder + '.zip', __zip_folder + f'{__now_str}.zip')
            print(f'圧縮ファイル{__zip_folder}.zipが既に存在したので{__zip_folder}{__now_str}.zipに変名しました')
        with zipfile.ZipFile(__zip_folder + '.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for __web_file_helper in self.get_web_file_list():
                zip_file.write(__web_file_helper.get_path())
        return True

    def rename_zip_file(self, zip_filename):
        """圧縮ファイルの名前を付けなおす
        :param zip_filename: str 付け直すファイル名(禁則文字は削除される)
        :return: bool 成功/失敗=True/False
        """
        __zip_folder = self.get_folder_path_from_1st_element()
        new_zip_filename = WebFileHelper.fixed_file_name(zip_filename)
        src_zip_path = __zip_folder + '.zip'
        dst_zip_path = new_zip_filename + '.zip'
        new_zip_path = os.path.join(__zip_folder, '..', dst_zip_path).replace(os.sep, '/')
        if os.path.isfile(new_zip_path):
            print(f'圧縮リネームファイル{new_zip_filename}.zipが既に存在しています')
            return False
        print(f'圧縮ファイル名を付け直します:{new_zip_filename}.zip')
        os.rename(src_zip_path, dst_zip_path)
        return True

    def delete_local_folder(self):
        """ファイルリストのローカルファイルをフォルダごと削除する
        :return: None
        """
        __zip_folder = self.get_folder_path_from_1st_element()
        print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
        shutil.rmtree(__zip_folder)
        if __zip_folder[len(__zip_folder) - 1] == '\\':
            os.mkdir(__zip_folder)
        else:
            os.mkdir(__zip_folder + '\\')

    def delete_local_files(self):
        """ファイルリストのファイルについて、ローカルから削除する
        :return: None
        """
        for __web_file in self.get_web_file_list():
            __web_file.delete_local_file()

    def move(self, new_path):
        """ファイルリストのローカルファイルを移動する
        :param new_path: 移動先のフォルダーパス
        :return:
        """
        if self.is_exist():
            for __web_file in self.get_web_file_list():
                __web_file.move(new_path)
        else:
            print('ローカルファイルが不足しているため、ファイルリストの移動を中止した')

    def update_value_object_by_deployment_url_list(self):
        if len(self.get_web_file_list()) != 1:
            return False
        __web_file = self.get_web_file_list()[0]
        url_list = __web_file.get_deployment_url_list()
        folder_path = self.get_folder_path_from_1st_element()
        __web_file_list = []
        for __url in url_list:
            __web_file_list.append(WebFileHelper(__url, folder_path))
        self.value_object = WebFileListHelperValue(__web_file_list)
        return True

