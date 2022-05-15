#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード
"""

import unittest
from tenki import *
from const import *


class TestSpreadsheet(unittest.TestCase):
    """ unitテスト
    """

    def setUp(self):
        print("setUp")
        json_keyfile_name = 'C:\\Git\\igapon50\\traning\\python\\Web_scraping\\tenki-347610-1bc0fec79f90.json'
        workbook_name = '天気予報'
        worksheet_name = '七尾市和倉町data'
        self.spreadsheet = Spreadsheet(json_keyfile_name,
                                  workbook_name,
                                  worksheet_name,
                                  )

    def tearDown(self):
        print("tearDown")

    def test_spreadsheet01(self):
        """
        読込からのインスタンス生成
        :return:
        """
        self.spreadsheet.save_text(RESULT_FILE_PATH + '1.txt')
        spreadsheet2 = copy.deepcopy(self.spreadsheet)
        self.spreadsheet.load_text(RESULT_FILE_PATH + '1.txt')
        self.assertEqual(self.spreadsheet, spreadsheet2)

    def test_spreadsheet02(self):
        """
        値オブジェクトからのインスタンス生成
        :return:
        """
        value_objects = self.spreadsheet.get_value_objects()
        spreadsheet2 = Spreadsheet(value_objects)
        self.assertEqual(self.spreadsheet, spreadsheet2)

    def test_spreadsheet03(self):
        """

        :return:
        """
        spreadsheet3 = Spreadsheet()
        spreadsheet3.load_text(RESULT_FILE_PATH + '3.txt')
        spreadsheet3.save_text(RESULT_FILE_PATH + '4.txt')

        spreadsheet3.write_list_columns([100, 200, 300, 50], (1, 1))
        spreadsheet3.write_list_columns([99, 98, 97, 96], (1, 3))
        spreadsheet3.write_list_rows([1, 2, 3, 4], (5, 5))
        spreadsheet3.write_list_rows([10, 20, 30, 40], (7, 5))
        tenki = {
            "days_item": ["04月17日(日)", "04月18日(月)", "04月19日(火)", "04月20日(水)", "04月21日(木)", "04月22日(金)", "04月23日(土)",
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

    def test_tenki01(self):
        css_root = "dd.forecast10days-actab"
        css_selectors = {"days_item": "div.days",
                         "time_item": "dd.time-item > span",
                         "forecast_item": "dd.forecast-item > p > img",
                         "prob_precip_item": "dd.prob-precip-item > span > span",
                         "precip_item": "dd.precip-item > span > span",
                         "temp_item": "dd.temp-item > script",
                         "wind_item_blow": "dd.wind-item > p > img",
                         "wind_item_speed": "dd.wind-item > p > span",
                         }
        attrs = {"days_item": "",
                 "time_item": "",
                 "forecast_item": "alt",
                 "prob_precip_item": "",
                 "precip_item": "",
                 "temp_item": "",
                 "wind_item_blow": "alt",
                 "wind_item_speed": "",
                 }
        tenki = Tenki("https://tenki.jp/forecast/4/20/5620/17202/10days.html",
                      css_root,
                      css_selectors,
                      attrs,
                      )
        tenki.save_text(RESULT_FILE_PATH + '1.txt')
        # 値オブジェクトを生成
        value_objects = tenki.get_value_objects()
        # 値オブジェクトでインスタンス作成
        tenki2 = Tenki(value_objects)
        # 保存や読込を繰り返す
        tenki2.save_text(RESULT_FILE_PATH + '2.txt')
        tenki2.load_text(RESULT_FILE_PATH + '2.txt')
        tenki2.save_text(RESULT_FILE_PATH + '3.txt')
        tenki3 = Tenki()
        tenki3.load_text(RESULT_FILE_PATH + '3.txt')
        tenki3.save_text(RESULT_FILE_PATH + '4.txt')

    def test_tenki02(self):
        tenki = Tenki()
        tenki.load_text(RESULT_FILE_PATH + '1.txt')
        json_keyfile_name = 'C:\\Git\\igapon50\\traning\\python\\Web_scraping\\tenki-347610-1bc0fec79f90.json'
        workbook_name = '天気予報'
        worksheet_name = '七尾市和倉町data'
        spreadsheet = Spreadsheet(json_keyfile_name,
                                  workbook_name,
                                  worksheet_name,
                                  )
        spreadsheet.save_text(RESULT_FILE_PATH + '2.txt')
        spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
        num = len(tenki.get_result_forecasts())
        spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))
        worksheet_name = '七尾市和倉町conv'
        spreadsheet = Spreadsheet(json_keyfile_name,
                                  workbook_name,
                                  worksheet_name,
                                  )
        spreadsheet.save_text(RESULT_FILE_PATH + '3.txt')
        tenki.special_func_temp()
        spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
        num = len(tenki.get_result_forecasts())
        spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))
        spreadsheet.save_text(RESULT_FILE_PATH + '4.txt')
        tenki.save_text(RESULT_FILE_PATH + '5.txt')

    def test_tenki03(self):
        tenki = Tenki()
        tenki.load_text(RESULT_FILE_PATH + '1.txt')
        tenki.special_func_temp()
        tenki.create_LINE_BOT_TOBA_format()


if __name__ == "__main__":
    unittest.main()
