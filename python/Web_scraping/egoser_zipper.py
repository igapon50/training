#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chromeDriverHelper import *
from crawling import *


if __name__ == '__main__':  # インポート時には動かない
    my_name = None
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.エゴサ対象の名前
        my_name = sys.argv[1]
        print('引数一つ', sys.argv[0], my_name)
    elif 1 == len(sys.argv):
        # 引数がなければ、クリップボードからURLを得る
        paste_str = pyperclip.paste()
        if paste_str:
            my_name = paste_str
        print('引数なし', sys.argv[0], paste_str)
    else:
        print('引数が不正です。')
        sys.exit()
    site_url = f'https://www.google.com/search?q={my_name}'
    site_selectors = {
        'page_urls': [
            (By.XPATH,
             '//*[@id="hdtb-msb"]/div[1]/div/div[2]/a',
             lambda el: el.get_attribute("href")
             ),
        ]
    }
    page_selectors = {
        'title_jp': [(By.XPATH,
                      '//*[@id="REsRA"]',
                      lambda el: el.get_attribute("value")),
                     ],
        'title_en': [(By.XPATH,
                      '//*[@id="REsRA"]',
                      lambda el: el.get_attribute("value")),
                     ],
        'image_urls': [(By.XPATH,
                       '//*[@id="islrg"]/div[1]/div/a[1]/div[1]/img',
                        lambda el: el.get_attribute("src")),
                       ],
    }
    crawling = Crawling(site_url, site_selectors, 'egoser_zipper.txt')
    crawling_items = crawling.get_crawling_items()
    page_urls = []
    if 'page_urls' in crawling_items:
        page_urls = crawling_items['page_urls']
    for page_url in page_urls:
        print(page_url)
        if crawling.is_url_included_exclusion_list(page_url):
            crawling.move_url_from_page_urls_to_exclusion_urls(page_url)
            crawling.save_text()
            continue
        items = crawling.scraping(page_url, page_selectors)
        image_urls = crawling.take_out(items, 'image_urls')[0:20]  # 先頭の20個は、DataURIで表示される
        title = Crawling.validate_title(items, 'title_jp', 'title_en')
        url_title = ChromeDriverHelper.fixed_file_name(page_url)
        # フォルダがなかったらフォルダを作る
        os.makedirs(WebFileListHelper.work_path, exist_ok=True)
        target_file_name = os.path.join(WebFileListHelper.work_path, f'{title}：{url_title}.html')
        print(title)
        if not os.path.exists(target_file_name):
            if image_urls:
                print(image_urls)
                web_file_list = WebFileListHelper(image_urls)
                crawling.download_chrome_driver(web_file_list)
                if not web_file_list.make_zip_file():
                    sys.exit()
                if not web_file_list.rename_zip_file(title):
                    if not web_file_list.rename_zip_file(f'{title}：{url_title}'):
                        sys.exit()
                web_file_list.delete_local_files()
                # 成功したらチェック用ファイルを残す
                ChromeDriverHelper().save_source(target_file_name)
            # page_urlsからexclusion_urlsにURLを移して保存する
        crawling.move_url_from_page_urls_to_exclusion_urls(page_url)
        crawling.save_text()
    print('crawling-end')
