#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使う前に定義を修正すること。
page_root_urlに、クローリングするページのURLを指定する。
例. 1ページクローリングして、スクレイピングしたURLリストに対して、巡回ダウンロードする
> python crawling_template.py 1
例. 10ページクローリングして、スクレイピングしたURLリストに対して、巡回ダウンロードする
> python crawling_template.py 10
"""
import copy

from crawling import *


if __name__ == '__main__':  # インポート時には動かない
    page_root_url = ''  # TODO: ページ番号を除いたURLを指定する
    start_page_number = 1
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.クローリングするページ数
        page_number = int(sys.argv[1])
        print('引数一つ', sys.argv[0], page_number)
    elif 1 == len(sys.argv):
        # 引数がなければ、デフォルト10ページ
        page_number = 10
    else:
        print('引数が不正です。')
        sys.exit()
    end_page_number = page_number
    site_url_list = [page_root_url + str(x) for x in range(start_page_number, end_page_number + 1)]
    site_selectors = {
        'page_urls': [
            (By.XPATH,
             '//body/div[2]/div/div/a',
             lambda el: el.get_attribute("href")
             ),
        ]
    }
    page_selectors = {
        'title_jp': [(By.XPATH,
                      '//div/div/div/h2',
                      lambda el: el.text),
                     ],
        'title_en': [(By.XPATH,
                      '//div/div/div/h1',
                      lambda el: el.text),
                     ],
        'languages': [(By.XPATH,
                       '//div/div/section/div[6]/span/a/span[1]',
                       lambda el: el.text),
                      ],
    }
    image_selectors = {
        'image_url': [(By.XPATH,
                       '(//*[@id="thumbnail-container"]/div/div/a)[last()]',
                       lambda el: el.get_attribute("href")),
                      (By.XPATH,
                       '//*[@id="image-container"]/a/img',
                       lambda el: el.get_attribute("src")),
                      ],
        # 'image_urls': [(By.XPATH,
        #                 '//*[@id="thumbnail-container"]/div/div/a',
        #                 lambda el: el.get_attribute("href")),
        #                (By.XPATH,
        #                 '//*[@id="image-container"]/a/img',
        #                 lambda el: el.get_attribute("src")),
        #                ],
    }
    crawling = None
    for site_url in site_url_list:
        crawling = Crawling(site_url, site_selectors)
    if 'image_url' in image_selectors:
        crawling.crawling_url_deployment(page_selectors, image_selectors)
    if 'image_urls' in image_selectors:
        crawling.crawling_urls(page_selectors, image_selectors)
    print('crawling-end')
