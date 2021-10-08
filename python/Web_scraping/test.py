#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file imgdl.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/01/26
# @brief Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる。
# @details Webサイトから画像のURLリストを作り、ダウンロードしてzipファイルにまとめる。
# @warning 
# @note 

# local source
from const import *
from func import *

import pickle
from dataclasses import dataclass
import sys
import copy

sys.setrecursionlimit(10000)


##
# @brief Value Objects
# @details タイトルと画像リストを持つXmlScrapingクラスの値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class XmlScrapingValue:
    target_url: str
    css_image_selector: str
    title: str
    imageList: list

    def __init__(self, target_url: str, css_image_selector: str, title: str, image_list: list):
        if target_url is not None:
            object.__setattr__(self, "target_url", target_url)
        if css_image_selector is not None:
            object.__setattr__(self, "css_image_selector", css_image_selector)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(image_list):
            object.__setattr__(self, "imageList", image_list)


##
# @brief 指定のサイトを読み込んで、指定のCSSセレクタでパースして、XmlScrapingValueを構成する
# @details img_css_selectは、CSSセレクタを指定する。
# @warning
# @note

class XmlScraping:
    xmlScrapingValue: XmlScrapingValue = None
    target_url: str
    css_image_selector: str

    def __init__(self, target_url: str, css_image_selector: str):
        if target_url is not None:
            self.target_url = target_url
        if css_image_selector is not None:
            self.css_image_selector = css_image_selector

    # def __init__(self, xml_scraping_value: XmlScrapingValue):
    #     if xml_scraping_value is not None:
    #         self.xmlScrapingValue = xml_scraping_value
    #         if xml_scraping_value.target_url is not None:
    #             self.targetUrl = xml_scraping_value.target_url
    #         if xml_scraping_value.css_image_selector is not None:
    #             self.css_image_selector = xml_scraping_value.css_image_selector

    # # targetUrlを指定すると、解析してcssImageSelector作る
    # def __init__(self, target_url: str):
    #     if target_url is not None:
    #         self.target_url = target_url
        # 解析してcssImageSelector作ってくれないかな。

    def get_value_objects(self):
        return copy.deepcopy(self.xmlScrapingValue)

    def request(self):
        retries = Retry(connect=5, read=2, redirect=5)
        http = urllib3.PoolManager(retries=retries)
        res = http.request('GET', self.target_url, timeout=10, headers=HEADERS_DIC)
        soup = bs4.BeautifulSoup(res.data, 'html.parser')
        title = str(soup.title.string)
        image_list: list = []
        for img in soup.select(self.css_image_selector):
            absolute_path = str(img[img_attr])
            parse_path = urlparse(absolute_path)
            if 0 == len(parse_path.scheme):  # 絶対パスかチェックする
                absolute_path = urljoin(self.target_url, absolute_path)
            image_list.append(absolute_path)
        self.xmlScrapingValue = XmlScrapingValue(self.target_url, self.css_image_selector, title, image_list)
        return True

    def save_text(self, save_path: str):
        if self.xmlScrapingValue is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.target_url + '\n'  # クリップボード用変数にサイトURL追加
            buff += self.css_image_selector + '\n'  # クリップボード用変数にcssセレクタ追加
            buff += self.xmlScrapingValue.title + '\n'  # クリップボード用変数にタイトル追加
            for absolute_path in self.xmlScrapingValue.imageList:
                buff += absolute_path + '\n'  # クリップボード用変数に画像URL追加
            work_file.write(buff)  # ファイルへの保存
            return True

    def save_pickle(self, save_path: str):
        if self.xmlScrapingValue is None:
            return False
        with open(save_path, 'wb') as work_file:
            pickle.dump(self.xmlScrapingValue, work_file)
            return True

    def load_pickle(self, load_path: str):
        with open(load_path, 'rb') as work_file:
            self.xmlScrapingValue = pickle.load(work_file)
            return True


if __name__ == '__main__':  # インポート時には動かない
    imglist_filepath = RESULT_FILE_PATH
    target_url = DEFAULT_TARGET_URL
    folder_path = OUTPUT_FOLDER_PATH
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
        print(msg_error_exit)
        sys.exit()
    print(target_url)
    xmlScraping = XmlScraping(target_url, img_css_select)
    xmlScraping.request()
    xmlScraping.save_text(RESULT_FILE_PATH)
    value_objects = xmlScraping.get_value_objects()
    xmlScraping.save_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.load_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.save_text(RESULT_FILE_PATH + '1.txt')
    # xmlScraping2 = XmlScraping(value_objects)
    # xmlScraping2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    # xmlScraping2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    # xmlScraping2.save_text(RESULT_FILE_PATH + '2.txt')
