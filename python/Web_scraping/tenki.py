#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
検証コード

https://docs.python-requests.org/projects/requests-html/en/latest/
https://commte.net/7628
"""
from requests_html import HTMLSession
from crawling import *
import json


@dataclass(frozen=True)
class TenkiValue:
    """
    クローリング値オブジェクト
    """
    target_url: str
    css_selectors: dict
    attrs: dict
    title: str
    forecasts: dict

    def __init__(self, target_url, css_selectors, attrs, title, forecasts):
        """
        完全コンストラクタパターン

        :param target_url: str 処理対象サイトURL
        :param css_selectors: dict スクレイピングする際のCSSセレクタ辞書
        :param attrs: dict スクレイピングする際の属性辞書
        :param title: str 対象サイトタイトル
        :param forecasts: dict スクレイピングして得た属性のリスト
        """
        if target_url is not None:
            object.__setattr__(self, "target_url", target_url)
        if css_selectors is not None:
            object.__setattr__(self, "css_selectors", css_selectors)
        if attrs is not None:
            object.__setattr__(self, "attrs", attrs)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(forecasts):
            object.__setattr__(self, "forecasts", forecasts)


class Tenki:
    """
    クローリングのユーティリティ
        * 指定のサイトを読み込む
        * 指定のCSSセレクタ(css_selectors)と属性でクローリング(attrs)する
        * クローリング結果でTenkiValueを生成する
        * TenkiValueをファイルに保存したり読み込んだりできる
    """
    tenki_value: TenkiValue = None
    target_url: str = None
    css_selectors: dict = None
    attrs: dict = None

    def __init__(self, target_value=None, css_selectors=None, attrs=None):
        """
        コンストラクタ

        :param target_value: str 対象となるサイトURL、または、TenkiValue 値オブジェクト
        :param css_selectors: dict スクレイピングする際のCSSセレクタ
        :param attrs: dict スクレイピングする際の属性
        """
        if target_value is not None:
            if isinstance(target_value, TenkiValue):
                tenki_value = target_value
                self.tenki_value = tenki_value
                if tenki_value.target_url is not None:
                    self.target_url = tenki_value.target_url
                if tenki_value.css_selectors is not None:
                    self.css_selectors = tenki_value.css_selectors
                if tenki_value.attrs is not None:
                    self.attrs = tenki_value.attrs
            else:
                if isinstance(target_value, str):
                    self.target_url = target_value
                    if css_selectors is not None:
                        self.css_selectors = css_selectors
                        if attrs is not None:
                            self.attrs = attrs
                            self.request()

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: crawling_value 値オブジェクト
        """
        return copy.deepcopy(self.tenki_value)

    def get_forecast_list(self):
        """
        クローリング結果を取得する

        :return: tenki_value.forecast_list クローリング結果
        """
        return copy.deepcopy(self.tenki_value.forecasts)

    def get_title(self):
        """
        対象サイトタイトルを取得する

        :return: crawling_value.title 対象サイトタイトル
        """
        return self.tenki_value.title

    def request(self):
        """
        target_urlに接続して、スクレイピングして、tenki_valueを更新する

        :return: bool 成功/失敗=True/False
        """
        script = """
            () => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.clientHeight,
                    deviceScaleFactor: window.devicePixelRatio,
                }
            }
        """
        forecasts = {}
        session = HTMLSession()
        r = session.get(self.target_url)
        # ブラウザエンジンでHTMLを生成させる
        val = r.html.render(script=script, reload=False)
        # スクレイピング
        title = r.html.find("html > head > title", first=True).text

        for key in self.css_selectors:
            forecasts[key] = []
        target_rows = r.html.find(target_root_css)
        if target_rows:
            # todo 既に経過した時間は表示されない、開始点と終了店が違うので調整が必要
            for row in target_rows:
                for key in self.css_selectors:
                    buffer = row.find(self.css_selectors[key])
                    if not self.attrs[key] == "":
                        for buf in buffer:
                            alt = buf.attrs[self.attrs[key]]
                            if alt:
                                forecasts[key].append(alt)
                    else:
                        for buf in buffer:
                            forecasts[key].append(buf.text)
        self.tenki_value = TenkiValue(self.target_url,
                                      self.css_selectors,
                                      self.attrs,
                                      title,
                                      forecasts,
                                      )

    def create_save_text(self):
        """
        保存用文字列の作成

        :return: str 保存用文字列の作成
        """
        buff = self.tenki_value.target_url + '\n'  # サイトURL追加
        buff += json.dumps(self.tenki_value.css_selectors, ensure_ascii=False) + '\n'  # cssセレクタ追加
        buff += json.dumps(self.tenki_value.attrs, ensure_ascii=False) + '\n'  # 属性追加
        buff += self.tenki_value.title + '\n'  # タイトル追加
        buff += json.dumps(self.tenki_value.forecasts, ensure_ascii=False) + '\n'  # 画像URL追加
        return buff

    def clip_copy(self):
        """
        クローリング結果をクリップボードにコピーする

        :return: bool 成功/失敗=True/False
        """
        if self.tenki_value is None:
            return False
        buff = self.create_save_text()
        pyperclip.copy(buff)  # クリップボードへのコピー
        return True

    def save_text(self, save_path):
        """
        データをファイルに、以下の独自フォーマットで保存する
            * 処理対象サイトURL
            * CSSセレクタ
            * 属性
            * タイトル
            * クローリング結果

        :param save_path: str セーブする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        if self.tenki_value is None:
            return False
        with open(save_path, 'w', encoding='utf-8') as work_file:
            buff = self.create_save_text()
            work_file.write(buff)  # ファイルへの保存
            return True

    def load_text(self, load_path):
        """
        独自フォーマットなファイルからデータを読み込む

        :param load_path: str ロードする独自フォーマットなファイルのパス
        :return: bool 成功/失敗=True/False
        """
        with open(load_path, 'r', encoding='utf-8') as work_file:
            buff = work_file.readlines()
            self.target_url = buff[0].rstrip('\n')
            del buff[0]
            self.css_selectors = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.attrs = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            forecasts: dict = json.loads(buff[0].rstrip('\n'))
            self.tenki_value = TenkiValue(self.target_url,
                                          self.css_selectors,
                                          self.attrs,
                                          title,
                                          forecasts,
                                          )
            return True


if __name__ == '__main__':  # インポート時には動かない
    target_url = "https://tenki.jp/forecast/4/20/5620/17202/10days.html"
    target_root_css = "dd.forecast10days-actab"
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

    css_selectors = {"days_item": "div.days",
                     "time_item": "dd.time-item > span",
                     "forecast_item": "dd.forecast-item > p > img",
                     "prob_precip_item": "dd.prob-precip-item > span > span",
                     "precip_item": "dd.precip-item > span > span",
                     "wind_item_blow": "dd.wind-item > p > img",
                     "wind_item_speed": "dd.wind-item > p > span",
                     }
    attrs = {"days_item": "",
             "time_item": "",
             "forecast_item": "alt",
             "prob_precip_item": "",
             "precip_item": "",
             "wind_item_blow": "alt",
             "wind_item_speed": "",
             }
    tenki = Tenki("https://tenki.jp/forecast/4/20/5620/17202/10days.html",
                  css_selectors,
                  attrs,
                  )
    tenki.save_text(RESULT_FILE_PATH)
    # 値オブジェクトを生成
    value_objects = tenki.get_value_objects()
    # 保存や読込を繰り返す
    # tenki.save_pickle(RESULT_FILE_PATH + '1.pkl')
    # tenki.load_pickle(RESULT_FILE_PATH + '1.pkl')
    # tenki.save_text(RESULT_FILE_PATH + '1.txt')
    # 値オブジェクトでインスタンス作成
    tenki2 = Tenki(value_objects)
    # 保存や読込を繰り返す
    # tenki2.save_pickle(RESULT_FILE_PATH + '2.pkl')
    # tenki2.load_pickle(RESULT_FILE_PATH + '2.pkl')
    tenki2.save_text(RESULT_FILE_PATH + '2.txt')
    tenki2.load_text(RESULT_FILE_PATH + '2.txt')
    # tenki2.save_pickle(RESULT_FILE_PATH + '3.pkl')
    # tenki2.load_pickle(RESULT_FILE_PATH + '3.pkl')
    tenki2.save_text(RESULT_FILE_PATH + '3.txt')
