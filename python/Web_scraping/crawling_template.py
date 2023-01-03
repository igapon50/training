#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

from crawling import *


# 検証コード
if __name__ == '__main__':  # インポート時には動かない
    page_root_url = ''  # TODO: ページ番号を除いたURLを指定する
    start_page_number = 1
    end_page_number = 20
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
