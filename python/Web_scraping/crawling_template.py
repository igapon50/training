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
                      '//div/div/div/h2',  # //*[@id="info"]/h2
                      lambda el: el.text),
                     ],
        'title_en': [(By.XPATH,
                      '//div/div/div/h1',  # //*[@id="info"]/h1
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
        chrome_driver = ChromeDriverHelper(page_url, page_selectors)
        items = chrome_driver.get_items()

        title = crawling.take_out(items, 'title_jp')
        title_sub = crawling.take_out(items, 'title_en')
        languages = crawling.take_out(items, 'languages')
        if not title:
            if not title_sub:
                # タイトルが得られない時は、タイトルを日時文字列にする
                now = datetime.datetime.now()
                title = f'{now:%Y%m%d_%H%M%S}'
            else:
                title = title_sub
        title = chrome_driver.fixed_file_name(title)
        url_title = chrome_driver.fixed_file_name(page_url)
        target_file_name = f'{title}：{url_title}.html'
        print(title, title_sub, languages)
        if languages and languages == 'japanese' and not os.path.exists(target_file_name):
            image_items = chrome_driver.scraping(image_selectors)
            image_urls = crawling.take_out(image_items, 'image_urls')
            last_image_url = crawling.take_out(image_items, 'image_url')
            if not last_image_url:
                raise ValueError(f"エラー:last_image_urlが不正[{last_image_url}]")
            print(last_image_url, image_urls)
            fileDownloader = WebFileListHelper([last_image_url])
            # 末尾画像のナンバーから全ての画像URLを推測して展開する
            fileDownloader.update_value_object_by_deployment_url_list()
            url_list = fileDownloader.get_url_list()
            print(url_list)

            fileDownloader.download_irvine()
            for count in enumerate(WebFileHelper.ext_list):
                if fileDownloader.is_exist():
                    break
                # ダウンロードに失敗しているときは、失敗しているファイルの拡張子を変えてダウンロードしなおす
                fileDownloader.rename_url_ext_shift()
                fileDownloader.download_irvine()
            # if not fileDownloader.rename_filenames():
            #     sys.exit()
            if not fileDownloader.make_zip_file():
                sys.exit()
            if not fileDownloader.rename_zip_file(title):
                if not fileDownloader.rename_zip_file(f'{title}：{url_title}'):
                    sys.exit()
            fileDownloader.delete_local_files()
            # 成功したらチェック用ファイルを残す
            chrome_driver.save_source(target_file_name)
        # page_urlsからexclusion_urlsにURLを移して保存する
        crawling.move_url_from_page_urls_to_exclusion_urls(page_url)
        crawling.save_text()
    print('crawling-end')
