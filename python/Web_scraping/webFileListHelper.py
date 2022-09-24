#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""webファイルリストのヘルパー
"""
from webFileHelper import *


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

    def get_web_file_list_helper(self):
        return copy.deepcopy(self.__web_file_list)

    def is_exist(self):
        """ファイルリストの全ファイルがローカルに存在する
        :return: bool 全てのファイルが存在すればTrueを返す
        """
        for __web_file in self.value_object.file_list:
            if not os.path.isfile(__web_file.get_path()):
                return False
        return True

    def rename_url_ext_shift(self):
        """ファイルリストの各ファイルについて、ローカルに存在しないファイルの拡張子をシフトする
        :return:
        """
        for __count, __web_file_helper in enumerate(self.value_object.file_list):
            if not os.path.isfile(__web_file_helper.get_path()):
                WebFileHelper(__web_file_helper).rename_url_ext_shift()
    # downloading.pyから以下を移植する
    # ファイルリストのファイル名を付け直す rename_images
    # 圧縮ファイルを作る make_zip_file
    # 圧縮ファイルのファイル名を付け直す rename_zip_file
    # ファイルリストのファイル削除(フォルダ削除) rename_file_clear


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
    web_file_list = WebFileListHelper(image_url_list)
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
    if web_file_list.is_exist():
        print('全てのファイルが存在する')
    else:
        print('ファイルが存在しない')
