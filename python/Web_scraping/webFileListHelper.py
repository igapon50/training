#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルリストのヘルパー
"""
from webFileHelper import *
from downloading import *


@dataclass(frozen=True)
class WebFileListHelperValue:
    """値オブジェクト"""
    web_file_list: list = None
    folder_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FOLDER_PATH).replace(os.sep, '/')

    def __init__(self, web_file_list):
        """完全コンストラクタパターン
        :param web_file_list: list webファイルリスト
        """
        if not web_file_list:
            raise ValueError(f"{self.__class__}引数エラー:web_file_list=None")
        for count, item in enumerate(web_file_list):
            if not isinstance(item, WebFileHelper):
                raise ValueError(f"{self.__class__}引数エラー:web_file_listの{count}個目がWebFileHelperで無い")
        object.__setattr__(self, "web_file_list", web_file_list)


class WebFileListHelper:
    """webファイルリスト"""
    value_object: WebFileListHelperValue = None
    folder_path: str = WebFileListHelperValue.folder_path

    def __init__(self, value_object=None, folder_path=folder_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlリストとfolder_pathより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param folder_path: str フォルダのフルパス
        """
        if value_object:
            if isinstance(value_object, WebFileListHelperValue):
                self.value_object = value_object
            elif isinstance(value_object, list):
                if folder_path:
                    __web_file_list = []
                    for __url in value_object:
                        __web_file_list.append(WebFileHelper(__url, folder_path))
                    self.value_object = WebFileListHelperValue(__web_file_list)
                else:
                    raise ValueError(f"{self.__class__}引数エラー:folder_path=None")
            else:
                raise ValueError(f"{self.__class__}引数エラー:value_objectの型")
        else:
            raise ValueError(f"{self.__class__}引数エラー:value_object=None")

    def get_web_file_list(self):
        """ファイルリストを得る
        :return: list[WebFileHelper]
        """
        return copy.deepcopy(self.value_object.web_file_list)

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
        return copy.deepcopy(self.get_web_file_list()[0].get_folder_path())

    def is_exist(self):
        """ファイルリストの全ファイルがローカルに存在する
        :return: bool 全てのファイルが存在すればTrueを返す
        """
        for __web_file in self.get_web_file_list():
            if not __web_file.is_exist():
                return False
        return True

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

    def delete_images_folder(self):
        """ファイルリストのファイルについて、ローカルから削除する
        :return: None
        """
        __zip_folder = self.get_folder_path_from_1st_element()
        print('ファイル削除します(フォルダごと削除して、フォルダを作り直します)')
        shutil.rmtree(__zip_folder)
        if __zip_folder[len(__zip_folder) - 1] == '\\':
            os.mkdir(__zip_folder)
        else:
            os.mkdir(__zip_folder + '\\')

    def delete_images(self):
        """ファイルリストのファイルについて、ローカルから削除する
        :return: None
        """
        for __web_file in self.get_web_file_list():
            if os.path.isfile(__web_file.get_path()):
                os.remove(__web_file.get_path())
