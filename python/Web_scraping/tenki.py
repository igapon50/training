#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
requestsでスクレイピングできないページのスクレイピング

参考資料料
https://gammasoft.jp/blog/how-to-download-web-page-created-javascript/
https://docs.python-requests.org/projects/requests-html/en/latest/
https://commte.net/7628

requests-htmlのGitHub
https://github.com/kennethreitz/requests-html
"""
from requests_html import HTMLSession
from spreadsheet import *


def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


@dataclass(frozen=True)
class TenkiValue:
    """
    クローリング値オブジェクト
    """
    target_url: str
    css_root: str
    css_selectors: dict
    attrs: dict
    title: str
    forecasts: dict
    counters: dict

    def __init__(self, target_url, css_root, css_selectors, attrs, title, forecasts, counters):
        """
        完全コンストラクタパターン

        :param target_url: str 処理対象サイトURL
        :param css_root: str スクレイピングする際のルートCSSセレクタ
        :param css_selectors: dict スクレイピングする際のCSSセレクタ辞書
        :param attrs: dict スクレイピングする際の属性辞書
        :param title: str 対象サイトタイトル
        :param forecasts: dict スクレイピングして得た属性のリスト
        :param counters: dict スクレイピングして得た属性のリストの個数リスト
        """
        if target_url is not None:
            object.__setattr__(self, "target_url", target_url)
        if css_root is not None:
            object.__setattr__(self, "css_root", css_root)
        if css_selectors is not None:
            object.__setattr__(self, "css_selectors", css_selectors)
        if attrs is not None:
            object.__setattr__(self, "attrs", attrs)
        if title is not None:
            object.__setattr__(self, "title", title)
        if 0 < len(forecasts):
            object.__setattr__(self, "forecasts", forecasts)
        if 0 < len(counters):
            object.__setattr__(self, "counters", counters)


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
    css_root: str = None
    css_selectors: dict = None
    attrs: dict = None

    def __init__(self, target_value=None, css_root=None, css_selectors=None, attrs=None):
        """
        コンストラクタ

        :param target_value: str 対象となるサイトURL、または、TenkiValue 値オブジェクト
        :param css_root: str スクレイピングする際のルートCSSセレクタ
        :param css_selectors: dict スクレイピングする際のCSSセレクタ
        :param attrs: dict スクレイピングする際の属性
        """
        if target_value is not None:
            if isinstance(target_value, TenkiValue):
                tenki_value = target_value
                self.tenki_value = tenki_value
                if tenki_value.target_url is not None:
                    self.target_url = tenki_value.target_url
                if tenki_value.css_root is not None:
                    self.css_root = tenki_value.css_root
                if tenki_value.css_selectors is not None:
                    self.css_selectors = tenki_value.css_selectors
                if tenki_value.attrs is not None:
                    self.attrs = tenki_value.attrs
            else:
                if isinstance(target_value, str):
                    self.target_url = target_value
                    if css_root is not None:
                        self.css_root = css_root
                        if css_selectors is not None:
                            self.css_selectors = css_selectors
                            if attrs is not None:
                                self.attrs = attrs
                                self.request()

    def special_func_temp(self):
        """
        特別製
        :return:
        """
        temp_item_forecasts = []
        temp_item_counters = []
        count = 0
        left_find = 'data: ['
        sp_key = 'temp-item'
        # 初日の予報なしに対応
        for value in self.tenki_value.counters[sp_key]:
            if value:
                break
            else:
                temp_item_counters.append(value)
        # スクリプトの中から気温を探して登録しなおす
        for value in self.tenki_value.forecasts[sp_key]:
            left = value.find(left_find) + len(left_find)
            right = left + value[left:].find(']')
            new_list = value[left:right].split(',')
            for item in new_list:
                if is_num(item):
                    temp_item_forecasts.append(str(item) + "℃")
                    count += 1
            temp_item_counters.append(count)
        # 末日の予報なしに対応
        pre = -1
        for value in self.tenki_value.counters[sp_key]:
            if value == pre:
                temp_item_counters.append(count)
            pre = value
        self.tenki_value.forecasts[sp_key] = temp_item_forecasts
        self.tenki_value.counters[sp_key] = temp_item_counters

    def get_value_objects(self):
        """
        値オブジェクトを取得する

        :return: TenkiValue 値オブジェクト
        """
        return copy.deepcopy(self.tenki_value)

    def get_result_forecasts(self):
        """
        クローリング結果を取得する

        :return: dict クローリング結果
        """
        return copy.deepcopy(self.tenki_value.forecasts)

    def get_result_counters(self):
        """
        クローリング結果を取得する

        :return: dict クローリング結果
        """
        return copy.deepcopy(self.tenki_value.counters)

    def get_title(self):
        """
        対象サイトタイトルを取得する

        :return: str 対象サイトタイトル
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
        counters = {}
        session = HTMLSession()
        response = session.get(self.target_url)
        # ブラウザエンジンでHTMLを生成させる
        response.html.render(script=script, reload=False, timeout=0, sleep=10)
        # スクレイピング
        title = response.html.find("html > head > title", first=True).text

        for key in self.css_selectors:
            forecasts[key] = []
            counters[key] = []
        target_rows = response.html.find(self.css_root)
        if target_rows:
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
                    counters[key].append(len(forecasts[key]))
        self.tenki_value = TenkiValue(self.target_url,
                                      self.css_root,
                                      self.css_selectors,
                                      self.attrs,
                                      title,
                                      forecasts,
                                      counters,
                                      )

    def create_save_text(self):
        """
        保存用文字列の作成

        :return: str 保存用文字列の作成
        """
        buff = self.tenki_value.target_url + '\n'  # サイトURL追加
        buff += self.tenki_value.css_root + '\n'  # ルートcssセレクタ追加
        buff += json.dumps(self.tenki_value.css_selectors, ensure_ascii=False) + '\n'  # cssセレクタ追加
        buff += json.dumps(self.tenki_value.attrs, ensure_ascii=False) + '\n'  # 属性追加
        buff += self.tenki_value.title + '\n'  # タイトル追加
        buff += json.dumps(self.tenki_value.forecasts, ensure_ascii=False) + '\n'  # 画像URL追加
        buff += json.dumps(self.tenki_value.counters, ensure_ascii=False) + '\n'  # 画像URL追加
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
            * ルートCSSセレクタ
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
            self.css_root = buff[0].rstrip('\n')
            del buff[0]
            self.css_selectors = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            self.attrs = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            title = buff[0].rstrip('\n')
            del buff[0]
            forecasts: dict = json.loads(buff[0].rstrip('\n'))
            del buff[0]
            counters: dict = json.loads(buff[0].rstrip('\n'))
            self.tenki_value = TenkiValue(self.target_url,
                                          self.css_root,
                                          self.css_selectors,
                                          self.attrs,
                                          title,
                                          forecasts,
                                          counters,
                                          )
            return True


if __name__ == '__main__':  # インポート時には動かない
    target_url = "https://tenki.jp/forecast/4/20/5620/17202/10days.html"
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

    css_root = "dd.forecast10days-actab"
    css_selectors = {"days_item": "div.days",
                     "time_item": "dd.time-item > span",
                     "forecast_item": "dd.forecast-item > p > img",
                     "prob_precip_item": "dd.prob-precip-item > span > span",
                     "precip_item": "dd.precip-item > span > span",
                     "temp-item": "dd.temp-item > script",
                     "wind_item_blow": "dd.wind-item > p > img",
                     "wind_item_speed": "dd.wind-item > p > span",
                     }
    attrs = {"days_item": "",
             "time_item": "",
             "forecast_item": "alt",
             "prob_precip_item": "",
             "precip_item": "",
             "temp-item": "",
             "wind_item_blow": "alt",
             "wind_item_speed": "",
             }
    tenki = Tenki("https://tenki.jp/forecast/4/20/5620/17202/10days.html",
                  css_root,
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
    tenki3 = Tenki()
    tenki.load_text(RESULT_FILE_PATH + '3.txt')
    tenki2.save_text(RESULT_FILE_PATH + '4.txt')

    json_keyfile_name = 'C:\\Git\\igapon50\\traning\\python\\Web_scraping\\tenki-347610-1bc0fec79f90.json'
    workbook_name = '天気予報'
    worksheet_name = '七尾市和倉町data'
    spreadsheet = Spreadsheet(json_keyfile_name,
                              workbook_name,
                              worksheet_name,
                              )
    spreadsheet.save_text(RESULT_FILE_PATH + '5.txt')
    spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
    num = len(tenki.get_result_forecasts())
    spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))

    json_keyfile_name = 'C:\\Git\\igapon50\\traning\\python\\Web_scraping\\tenki-347610-1bc0fec79f90.json'
    workbook_name = '天気予報'
    worksheet_name = '七尾市和倉町conv'
    spreadsheet = Spreadsheet(json_keyfile_name,
                              workbook_name,
                              worksheet_name,
                              )
    spreadsheet.save_text(RESULT_FILE_PATH + '6.txt')
    tenki.special_func_temp()
    spreadsheet.write_dict_columns(tenki.get_result_forecasts(), (1, 1))
    num = len(tenki.get_result_forecasts())
    spreadsheet.write_dict_columns(tenki.get_result_counters(), (1, 1 + num))
    spreadsheet.save_text(RESULT_FILE_PATH + '7.txt')
    tenki.save_text(RESULT_FILE_PATH + '8.txt')
