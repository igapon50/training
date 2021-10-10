#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file xmlScraping.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/10/10
# @brief
# @details
# @warning 
# @note

# standard library
from urllib.parse import urlparse  # URLパーサー
from urllib.parse import urljoin  # URL結合

# 3rd party packages
import urllib3
import pickle
import sys
import copy
import bs4  # Beautiful Soup
import pyperclip  # クリップボード
from dataclasses import dataclass
from urllib3.util.retry import Retry

# local source
from const import *

sys.setrecursionlimit(10000)


##
# @brief Value Objects
# @details XmlScrapingクラスの値オブジェクト。
# @warning
# @note
@dataclass(frozen=True)
class XmlScrapingValue:
    target_url: str
    css_image_selector: str
    image_attr: str
    title: str
    image_list: list

    # 完全コンストラクタパターン
    def __init__(self,
                 target_url: 'str 処理対象サイトURL',
                 css_image_selector: 'str スクレイピングする際のCSSセレクタ',
                 image_attr: 'str スクレイピングする際の属性',
                 title: 'str 対象サイトタイトル',
                 image_list: 'list スクレイピングして得た属性のリスト'
                 ):
        if target_url is not None:
            object.__setattr__(self, "target_url", target_url)
        if css_image_selector is not None:
            object.__setattr__(self, "css_image_selector", css_image_selector)
        if image_attr is not None:
            object.__setattr__(self, "image_attr", image_attr)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(image_list):
            object.__setattr__(self, "image_list", image_list)


##
# @brief 指定のサイトを読み込んで、指定のCSSセレクタでパースして、XmlScrapingValueを構成する
# @details css_image_selectは、CSSセレクタを指定する。image_attrは、属性を指定する。
# @warning
# @note

class XmlScraping:
    xmlScrapingValue: XmlScrapingValue = None
    target_url: str = None
    css_image_selector: str = None
    image_attr: str = None

    # コンストラクタ
    def __init__(self,
                 target_url: 'str 対象となるサイトURL' = None,
                 css_image_selector: 'str スクレイピングする際のCSSセレクタ' = None,
                 image_attr: 'str スクレイピングする際の属性' = None,
                 xml_scraping_value:  'XmlScrapingValue 値オブジェクト' = None,
                 ):
        if xml_scraping_value is not None:
            self.xmlScrapingValue = xml_scraping_value
            if xml_scraping_value.target_url is not None:
                self.target_url = xml_scraping_value.target_url
            if xml_scraping_value.css_image_selector is not None:
                self.css_image_selector = xml_scraping_value.css_image_selector
            if xml_scraping_value.image_attr is not None:
                self.image_attr = xml_scraping_value.image_attr
        else:
            if target_url is not None:
                self.target_url = target_url
                # targetUrlを指定したら、誰か解析してcssImageSelector作ってくれないかな。
                if css_image_selector is not None:
                    self.css_image_selector = css_image_selector
                    if image_attr is not None:
                        self.image_attr = image_attr
                        self.request()

    # 値オブジェクトを取得する
    def get_value_objects(self
                          ) -> 'XmlScrapingValue 値オブジェクト':
        return copy.deepcopy(self.xmlScrapingValue)

    # 画像URLリストを取得する
    def get_image_list(self
                       ) -> 'XmlScrapingValue.image_list 画像URLリスト':
        return copy.deepcopy(self.xmlScrapingValue.image_list)

    # 対象サイトタイトルを取得する
    def get_title(self
                  ) -> 'XmlScrapingValue.title 対象サイトタイトル':
        return self.xmlScrapingValue.title

    # target_urlに接続して、image_attrでスクレイピングして、titleとimage_listを更新する
    def request(self
                ) -> 'bool 成功/失敗=True/False':
        retries = Retry(connect=5, read=2, redirect=5)
        http = urllib3.PoolManager(retries=retries)
        res = http.request('GET', self.target_url, timeout=10, headers=HEADERS_DIC)
        soup = bs4.BeautifulSoup(res.data, 'html.parser')
        title = str(soup.title.string)
        image_list: list = []
        for img in soup.select(self.css_image_selector):
            absolute_path = str(img[self.image_attr])
            parse_path = urlparse(absolute_path)
            if 0 == len(parse_path.scheme):  # 絶対パスかチェックする
                absolute_path = urljoin(self.target_url, absolute_path)
            image_list.append(absolute_path)
        self.xmlScrapingValue = XmlScrapingValue(
            self.target_url,
            self.css_image_selector,
            self.image_attr,
            title,
            image_list)
        return True

    # 独自フォーマットでファイルに保存する
    def save_text(self,
                  save_path: 'str セーブするファイルのパス'
                  ) -> 'bool 成功/失敗=True/False':
        if self.xmlScrapingValue is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.xmlScrapingValue.target_url + '\n'  # サイトURL追加
            buff += self.xmlScrapingValue.css_image_selector + '\n'  # cssセレクタ追加
            buff += self.xmlScrapingValue.image_attr + '\n'  # 属性追加
            buff += self.xmlScrapingValue.title + '\n'  # タイトル追加
            for absolute_path in self.xmlScrapingValue.image_list:
                buff += absolute_path + '\n'  # 画像URL追加
            work_file.write(buff)  # ファイルへの保存
            return True

    # ファイルから独自フォーマットを読み込む
    def load_text(self,
                  load_path: 'str ロードするファイルのパス'
                  ) -> 'bool 成功/失敗=True/False':
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            self.target_url = buff[0].rstrip('\n')
            del buff[0]
            self.css_image_selector = buff[0].rstrip('\n')
            del buff[0]
            self.image_attr = buff[0].rstrip('\n')
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            image_list: list = []
            for line in buff:
                image_list.append(line.rstrip('\n'))
            self.xmlScrapingValue = XmlScrapingValue(
                self.target_url,
                self.css_image_selector,
                self.image_attr,
                title,
                image_list)
            return True

    # pickleでシリアライズしてファイルに保存する
    def save_pickle(self,
                    save_path: 'str セーブするファイルのパス'
                    ) -> 'bool 成功/失敗=True/False':
        if save_path is None:
            return False
        with open(save_path, 'wb') as work_file:
            pickle.dump(self.xmlScrapingValue, work_file)
            return True

    # ファイルから読み込み、pickleでデシリアライズする
    def load_pickle(self,
                    load_path: 'str ロードするファイルのパス'
                    ) -> 'bool 成功/失敗=True/False':
        if load_path is None:
            return False
        with open(load_path, 'rb') as work_file:
            self.xmlScrapingValue = pickle.load(work_file)
            return True

    # xmlScrapingをクリップボードにコピー
    def clip_copy(self
                  ) -> 'bool 成功/失敗=True/False':
        if self.xmlScrapingValue is None:
            return False
        buff = self.xmlScrapingValue.target_url + '\n'  # サイトURL追加
        buff += self.xmlScrapingValue.css_image_selector + '\n'  # cssセレクタ追加
        buff += self.xmlScrapingValue.image_attr + '\n'  # 属性追加
        buff += self.xmlScrapingValue.title + '\n'  # タイトル追加
        for absolute_path in self.xmlScrapingValue.image_list:
            buff += absolute_path + '\n'  # 画像URL追加
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True


# 検証コード
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
    xmlScraping = XmlScraping(target_url, img_css_select, img_attr)  # 'img.vimg[src*="jpg"]'
    xmlScraping.save_text(RESULT_FILE_PATH)
    value_objects = xmlScraping.get_value_objects()
    xmlScraping.save_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.load_pickle(RESULT_FILE_PATH + '1.pkl')
    xmlScraping.save_text(RESULT_FILE_PATH + '1.txt')
    xmlScraping2 = XmlScraping(None, None, None, value_objects)
    xmlScraping2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    xmlScraping2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    xmlScraping2.save_text(RESULT_FILE_PATH + '2.txt')
    xmlScraping2.load_text(RESULT_FILE_PATH + '2.txt')
    xmlScraping2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    xmlScraping2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    xmlScraping2.save_text(RESULT_FILE_PATH + '3.txt')
