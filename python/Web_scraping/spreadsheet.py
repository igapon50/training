#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
google Spreadsheetを操作する

参考資料料
"""
import sys
import copy
import pyperclip
from urllib.parse import urlparse  # URLパーサー
from dataclasses import dataclass
import json
import gspread


@dataclass(frozen=True)
class SpreadsheetValue:
    """
    スプレッドシート値オブジェクト
    """
    json_keyfile_name: str
    workbook_name: str
    worksheet_name: str
    data: list

    def __init__(self, json_keyfile_name, workbook_name, worksheet_name, data):
        """
        完全コンストラクタパターン

        :param json_keyfile_name: str spreadsheetアクセス用シークレットキーファイル名
        :param workbook_name: str ブック名
        :param worksheet_name: str シート名
        :param data: list スプレッドシートの値リスト
        """
        if json_keyfile_name is not None:
            object.__setattr__(self, "json_keyfile_name", json_keyfile_name)
        if workbook_name is not None:
            object.__setattr__(self, "workbook_name", workbook_name)
        if worksheet_name is not None:
            object.__setattr__(self, "worksheet_name", worksheet_name)
        if data is not None:
            object.__setattr__(self, "data", data)


class Spreadsheet:
    """
    スプレッドシートのユーティリティ
        * スプレッドシートを読み書きする
        * SpreadsheetValueを生成する
        * SpreadsheetValueをファイルに保存したり読み込んだりする
    """
    spreadsheet_value: SpreadsheetValue = None
    json_keyfile_name: str = None
    workbook_name: str = None
    worksheet_name: str = None
    data: list = None
    workbook: gspread.Worksheet = None
    worksheet: gspread.Spreadsheet = None
    is_google_colabo: bool = False

    def __init__(self, target_value=None, workbook_name=None, worksheet_name=None):
        """
        コンストラクタ

        :param target_value: str 対象となるサイトURL、または、SpreadsheetValue 値オブジェクト
        :param workbook_name: str 対象となるブック名
        :param worksheet_name: str 対象となるシート名
        """
        if target_value is not None:
            if isinstance(target_value, SpreadsheetValue):
                spreadsheet_value = target_value
                self.spreadsheet_value = spreadsheet_value
                if spreadsheet_value.json_keyfile_name is not None:
                    self.json_keyfile_name = spreadsheet_value.json_keyfile_name
                    if spreadsheet_value.workbook_name is not None:
                        self.workbook_name = spreadsheet_value.workbook_name
                        if spreadsheet_value.worksheet_name is not None:
                            self.worksheet_name = spreadsheet_value.worksheet_name
                            if spreadsheet_value.data is not None:
                                self.data = spreadsheet_value.data
                            self.open()
            else:
                if isinstance(target_value, str):
                    self.json_keyfile_name = target_value
                    if workbook_name is not None:
                        self.workbook_name = workbook_name
                        if worksheet_name is not None:
                            self.worksheet_name = worksheet_name
                            self.open()
                            self.data = self.worksheet.get_all_values()
                            self.spreadsheet_value = SpreadsheetValue(self.json_keyfile_name,
                                                                      self.workbook_name,
                                                                      self.worksheet_name,
                                                                      self.data,
                                                                      )

    def open(self):
        """
        spreadsheetにアクセスして、spreadsheet_valueを更新する

        :return: bool 成功/失敗=True/False
        """
        if 'google.colab' in sys.modules:
            self.is_google_colabo = True
            from google.colab import auth
            from oauth2client.client import GoogleCredentials
            auth.authenticate_user()
            gc = gspread.authorize(GoogleCredentials.get_application_default())
            print("google_colab")
        else:
            from oauth2client.service_account import ServiceAccountCredentials
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_keyfile_name, scope)
            gc = gspread.authorize(credentials)
            print("Not google_colab")
        self.workbook = gc.open(self.workbook_name)
        self.worksheet = self.workbook.worksheet(self.worksheet_name)
        return True

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: crawling_value 値オブジェクト
        """
        return copy.deepcopy(self.spreadsheet_value)

    def get_result_data(self):
        """
        スプレッドシートの値リストを取得する

        :return: spreadsheet_value.data スプレッドシートの値リスト
        """
        return copy.deepcopy(self.spreadsheet_value.data)

    def create_save_text(self):
        """
        保存用文字列の作成

        :return: str 保存用文字列の作成
        """
        buff = self.json_keyfile_name + '\n'  # シークレットファイル名追加
        buff += self.workbook_name + '\n'  # ブック名追加
        buff += self.worksheet_name + '\n'  # シート名追加
        buff += json.dumps(self.data, ensure_ascii=False) + '\n'  # データ追加
        return buff

    def clip_copy(self):
        """
        クリップボードにコピーする

        :return: bool 成功/失敗=True/False
        """
        if self.spreadsheet_value is None:
            return False
        buff = self.create_save_text()
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True

    def save_text(self, save_path):
        """
        データをファイルに、以下の独自フォーマットで保存する
            * シークレットファイル名
            * ブック名
            * シート名
            * データ

        :param save_path: str セーブする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if self.spreadsheet_value is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.create_save_text()
            work_file.write(buff)  # ファイルへの保存
            return True

    def load_text(self, load_path):
        """
        独自フォーマットなファイルからデータを読み込み、スプレッドシートを開く

        :param load_path: str ロードする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            self.json_keyfile_name = buff[0].rstrip('\n')
            del buff[0]
            self.workbook_name = buff[0].rstrip('\n')
            del buff[0]
            self.worksheet_name = buff[0].rstrip('\n')
            del buff[0]
            self.data: list = json.loads(buff[0].rstrip('\n'))
            self.spreadsheet_value = SpreadsheetValue(self.json_keyfile_name,
                                                      self.workbook_name,
                                                      self.worksheet_name,
                                                      self.data,
                                                      )
            self.open()
            return True

    def clear_worksheet(self):
        self.worksheet.clear()

    def write_dict_columns(self,
                           value_dict,
                           offset=(1, 1),
                           ):
        """
        辞書を、スプレッドシートのデータとして列方向で書き込む

        :param value_dict: dict 書き込むデータ(キーも書き込む)
        :param offset: tuple (row, col)オフセット
        :return: 書き込んだセル数
        """
        row, col = offset
        num = 0
        for key, col_list in value_dict.items():
            value_list = copy.deepcopy(col_list)
            value_list.insert(0, key)
            num += self.write_list_columns(value_list, (row, col))
            col += 1
        return num

    def write_dict_rows(self,
                        value_dict,
                        offset=(1, 1),
                        ):
        """
        辞書を、スプレッドシートのデータとして行方向で書き込む(キーも書き込む)

        :param value_dict: dict 書き込むデータ
        :param offset: tuple (row, col)オフセット
        :return: 書き込んだセル数
        """
        row, col = offset
        num = 0
        for key, row_list in value_dict.items():
            value_list = copy.deepcopy(row_list)
            value_list.insert(0, key)
            num += self.write_list_rows(value_list, (row, col))
            row += 1
        return num

    def write_list_columns(self,
                           value_list,
                           offset=(1, 1),
                           ):
        """
        リストを、スプレッドシートの列データとして書き込む

        :param value_list: list 書き込むデータ
        :param offset: tuple (row, col)オフセット
        :return: 書き込んだセル数
        """
        row, col = offset
        num = len(value_list)
        cell_str = gspread.utils.rowcol_to_a1(row, col) + ":" + gspread.utils.rowcol_to_a1(row + num, col)
        cell_list = self.worksheet.range(cell_str)
        for (cell, value) in zip(cell_list, value_list):
            cell.value = value
        self.worksheet.update_cells(cell_list, value_input_option="USER_ENTERED")
        return num

    def write_list_rows(self,
                        value_list,
                        offset=(1, 1),
                        ):
        """
        リストを、スプレッドシートの行データとして書き込む

        :param value_list: list 書き込むデータ
        :param offset: tuple (row, col)オフセット
        :return: 書き込んだセル数
        """
        row, col = offset
        num = len(value_list)
        cell_str = gspread.utils.rowcol_to_a1(row, col) + ":" + gspread.utils.rowcol_to_a1(row, col + num)
        cell_list = self.worksheet.range(cell_str)
        for (cell, value) in zip(cell_list, value_list):
            cell.value = value
        self.worksheet.update_cells(cell_list, value_input_option="USER_ENTERED")
        return num


if __name__ == '__main__':  # インポート時には動かない
    target_url = ""
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.対象のURL
        target_url = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if 0 < len(paste_str):
            parse = urlparse(paste_str)
            if 0 < len(parse.scheme):
                target_url = paste_str
    # クリップボードが空なら、デフォルトURLを用いる
    else:
        print('引数が不正です。')
        sys.exit()
    print(target_url)
