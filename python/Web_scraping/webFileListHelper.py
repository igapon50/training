#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルリストのヘルパー
"""

import datetime
import re  # 正規表現モジュール
import zipfile  # zipファイル
import shutil  # 高水準のファイル操作
from webFileHelper import *
from downloading import *


@dataclass(frozen=True)
class WebFileListHelperValue:
    """Webファイルリスト値オブジェクト
    """
    file_list: list

    def __init__(self, file_list):
        """完全コンストラクタパターン
        :param file_list: list webファイルリスト
        """
        if not file_list:
            raise ValueError(f"不正:引数file_listが無い")
        for count, item in enumerate(file_list):
            if not isinstance(item, WebFileHelper):
                raise ValueError(f"不正:引数file_listの{count}個目がWebFileHelperで無い")
        object.__setattr__(self, "file_list", file_list)


class WebFileListHelper:
    """webファイルのヘルパー
    """
    value_object: WebFileListHelperValue = None
    __web_file_list: list = []
    __root_path = os.path.dirname(os.path.abspath(__file__))
    __folder_path = os.path.join(__root_path, OUTPUT_FOLDER_PATH).replace(os.sep, '/')

    def __init__(self, value_object, folder_path=__folder_path):
        """コンストラクタ
        値オブジェクトからの復元、
        または、urlリストとfolder_pathより、値オブジェクトを作成する
        :param value_object: list 対象となるサイトURL、または、値オブジェクト
        :param folder_path: str フォルダのフルパス
        """
        if value_object:
            if isinstance(value_object, WebFileListHelperValue):
                self.value_object = value_object
            else:
                if isinstance(value_object, list):
                    if folder_path:
                        __urls = value_object
                        for __url in __urls:
                            self.__web_file_list.append(WebFileHelper(__url,
                                                                      folder_path,
                                                                      ))
                        self.value_object = WebFileListHelperValue(self.__web_file_list)

    def get_file_list(self):
        """ファイルリストを得る
        :return: list[WebFileHelper]
        """
        return copy.deepcopy(self.value_object.file_list)

    def get_folder_path_from_1st_element(self):
        """ファイルリストの一つ目に登録されているフォルダーパスを得る
        :return: str
        """
        return copy.deepcopy(self.get_file_list()[0].get_folder_path())

    def is_exist(self):
        """ファイルリストの全ファイルがローカルに存在する
        :return: bool 全てのファイルが存在すればTrueを返す
        """
        for __web_file in self.get_file_list():
            if not os.path.isfile(__web_file.get_path()):
                return False
        return True

    def rename_url_ext_shift(self):
        """ファイルリストの各ファイルについて、ローカルに存在しないファイルの拡張子をシフトし、ファイルリストを更新する
        :return: None
        """
        for __count, __web_file_helper in enumerate(self.value_object.file_list):
            if not os.path.isfile(__web_file_helper.get_path()):
                __web_file_helper.rename_url_ext_shift()

    def rename_filenames(self):
        """ファイルリストの各ファイルについて、ローカルに存在するファイルのファイル名をナンバリングファイル名に変更し、ファイルリストを更新する
        :return: None
        """
        for __count, __web_file_helper in enumerate(self.value_object.file_list):
            if os.path.isfile(__web_file_helper.get_path()):
                __web_file_helper.rename_filename('{:04d}'.format(__count))

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
            for __web_file_helper in self.get_file_list():
                zip_file.write(__web_file_helper.get_path())
        return True

    def rename_zip_file(self, zip_filename):
        """圧縮ファイルの名前を付けなおす
        :param zip_filename: str 付け直すファイル名(禁則文字は削除される)
        :return: bool 成功/失敗=True/False
        """
        __zip_folder = self.get_folder_path_from_1st_element()
        new_zip_filename = re.sub(r'[\\/:*?"<>|]+', '', zip_filename)
        if os.path.isfile(os.path.join(__zip_folder, '..', new_zip_filename + '.zip').replace(os.sep, '/')):
            print(f'圧縮リネームファイル{new_zip_filename}.zipが既に存在しています')
            return False
        print(f'圧縮ファイル名を付け直します:{new_zip_filename}.zip')
        os.rename(__zip_folder + '.zip', new_zip_filename + '.zip')
        return True

    def delete_images(self):
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


if __name__ == '__main__':  # インポート時には動かない
    main_url = None
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        main_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if paste_str:
            parse = urlparse(paste_str)
            if parse.scheme:
                main_url = paste_str
        # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()

    # テスト　若者 | かわいいフリー素材集 いらすとや
    image_url_list = [
        'https://1.bp.blogspot.com/-tzoOQwlaRac/X1LskKZtKEI/AAAAAAABa_M/'
        '89phuGIVDkYGY_uNKvFB6ZiNHxR7bQYcgCNcBGAsYHQ/'
        's180-c/fashion_dekora.png',
        'https://1.bp.blogspot.com/-gTf4sWnRdDw/X0B4RSQQLrI/AAAAAAABarI/'
        'MJ9DW90dSVwtMjuUoErxemnN4nPXBnXUwCNcBGAsYHQ/'
        's180-c/otaku_girl_fashion.png',
    ]
    fileDownloader = Downloading(image_url_list, OUTPUT_FOLDER_PATH)
    ret = fileDownloader.download()
    if not ret:
        print('ダウンロード失敗')
        sys.exit()
    web_file_list = WebFileListHelper(image_url_list)
    if not web_file_list.is_exist():
        print('ダウンロードファイルが存在しない')
        sys.exit()
    web_file_list.rename_filenames()
    if not web_file_list.is_exist():
        print('リネームファイルが存在しない')
        sys.exit()
    ret = web_file_list.make_zip_file()
    if not ret:
        print('zipファイル作成失敗')
        sys.exit()
    ret = web_file_list.rename_zip_file('若者 | かわいいフリー素材集 いらすとや')
    if not ret:
        print('zipファイルリネーム失敗')
        sys.exit()
    web_file_list.delete_images()

    for web_file_helper in web_file_list.value_object.file_list:
        print(web_file_helper.is_image())
        for __item in web_file_helper.ext_list:
            main_url = web_file_helper.get_url()
            main_folder_path = web_file_helper.get_folder_path()
            main_path = web_file_helper.get_path()
            main_filename = web_file_helper.get_filename()
            main_ext = web_file_helper.get_ext()
            print(main_url + ", " + main_folder_path)
            print(main_path + ", " + main_filename + ", " + main_ext)
            web_file_helper.rename_url_ext_shift()
    if not web_file_list.is_exist():
        print('ファイルが存在しない')
        sys.exit()
    print('ファイルが存在する')
