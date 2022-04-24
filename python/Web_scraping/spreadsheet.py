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
from oauth2client.service_account import ServiceAccountCredentials

# local source
from const import *


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
    worksheet: gspread.spreadsheet.Spreadsheet = None

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
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_keyfile_name, scope)
        gc = gspread.authorize(credentials)
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

    json_keyfile_name = 'C:\\Git\\igapon50\\traning\\python\\Web_scraping\\tenki-347610-1bc0fec79f90.json'
    workbook_name = '天気予報'
    worksheet_name = '七尾市和倉町data'
    spreadsheet = Spreadsheet(json_keyfile_name,
                              workbook_name,
                              worksheet_name,
                              )
    spreadsheet.save_text(RESULT_FILE_PATH)
    # 値オブジェクトを生成
    value_objects = spreadsheet.get_value_objects()
    # 保存や読込を繰り返す
    # spreadsheet.save_pickle(RESULT_FILE_PATH + '1.pkl')
    # spreadsheet.load_pickle(RESULT_FILE_PATH + '1.pkl')
    # spreadsheet.save_text(RESULT_FILE_PATH + '1.txt')
    # 値オブジェクトでインスタンス作成
    spreadsheet2 = Spreadsheet(value_objects)
    # 保存や読込を繰り返す
    # spreadsheet2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    # spreadsheet2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    spreadsheet2.save_text(RESULT_FILE_PATH + '2.txt')
    spreadsheet2.load_text(RESULT_FILE_PATH + '2.txt')
    # spreadsheet2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    # spreadsheet2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    spreadsheet2.save_text(RESULT_FILE_PATH + '3.txt')
    spreadsheet3 = Spreadsheet()
    spreadsheet3.load_text(RESULT_FILE_PATH + '3.txt')
    spreadsheet3.save_text(RESULT_FILE_PATH + '4.txt')

    spreadsheet3.write_list_columns([100, 200, 300, 50], (1, 1))
    spreadsheet3.write_list_columns([99, 98, 97, 96], (1, 3))
    spreadsheet3.write_list_rows([1, 2, 3, 4], (5, 5))
    spreadsheet3.write_list_rows([10, 20, 30, 40], (7, 5))
    tenki = {"days_item": ["04月17日(日)", "04月18日(月)", "04月19日(火)", "04月20日(水)", "04月21日(木)", "04月22日(金)", "04月23日(土)",
                           "04月24日(日)", "04月25日(月)", "04月26日(火)", "04月27日(水)", "04月28日(木)", "04月29日(金)", "04月30日(土)"],
             "time_item": ["00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                           "00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                           "00", "06", "12", "18", "24", "00", "06", "12", "18", "24", "00", "06", "12", "18", "24",
                           "00", "06", "12", "18", "24", "00", "06", "12", "18", "24"],
             "forecast_item": ["晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "晴", "曇", "曇", "曇のち雨",
                               "雨", "雨のち曇", "曇のち晴", "晴", "晴", "晴", "晴", "曇", "曇", "曇", "曇", "曇のち晴", "晴", "晴", "晴",
                               "晴のち曇", "曇のち雨", "雨のち晴", "晴", "晴", "晴", "晴", "曇", "曇"],
             "prob_precip_item": ["0%", "10%", "10%", "10%", "10%", "10%", "0%", "0%", "0%", "0%", "0%", "0%", "0%",
                                  "20%", "40%", "40%", "70%", "90%", "70%", "40%", "20%", "20%", "20%", "20%", "50%",
                                  "50%", "50%", "40%", "30%", "10%", "20%", "20%", "30%", "60%", "60%", "0%", "0%",
                                  "0%", "20%", "40%", "40%"],
             "precip_item": ["0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜",
                             "0㎜", "1㎜", "12㎜", "1㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜",
                             "0㎜", "0㎜", "0㎜", "4㎜", "4㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜", "0㎜"],
             "wind_item_blow": ["南", "南", "南", "南南西", "南西", "南", "南南西", "南南西", "北東", "北東", "東北東", "南", "南", "南", "北東",
                                "南南東", "南南東", "南南東", "南", "南西", "東", "南南東", "南南東", "東北東", "北北東", "南南西", "南西", "南西",
                                "南西", "南西", "西南西", "西", "西", "東", "北東", "北北東", "西南西", "西南西", "南西", "南西", "南", "南西",
                                "南西", "西南西", "西北西", "西", "南西", "南西", "南西", "西南西", "西南西"],
             "wind_item_speed": ["2m/s", "1m/s", "1m/s", "1m/s", "3m/s", "1m/s", "1m/s", "1m/s", "2m/s", "2m/s", "1m/s",
                                 "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "2m/s", "1m/s", "2m/s", "2m/s",
                                 "2m/s", "1m/s", "2m/s", "2m/s", "3m/s", "3m/s", "4m/s", "5m/s", "3m/s", "1m/s", "1m/s",
                                 "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "1m/s", "4m/s", "4m/s", "5m/s",
                                 "4m/s", "2m/s", "2m/s", "2m/s", "2m/s", "2m/s", "3m/s"]}
    spreadsheet3.write_dict_columns(tenki, (10, 10))
    spreadsheet3.write_dict_rows(tenki, (10, 17))
