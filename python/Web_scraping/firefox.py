#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
サイトURLより、サイト内のサイトURLリストを取得する
サイトURLより、タイトルを取得する
サイトURLより、サイト末尾のimageURLを取得する

参考ブログ
https://yaspage.com/python-memo-selenium/

"""
import time
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

xpath_actions = {"website": "//div/a/img",
                 "title": "//div/div/div/h2",
                 "last-image": "(//a/img)[last()]",
                 }
exec_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
driver_path = r'C:\Git\igapon50\traning\python\Web_scraping\driver\geckodriver.exe'
# profile_path = r'C:\Users\igapon\AppData\Roaming\Mozilla\Firefox\Profiles\rw01hmar.default'
profile_path = r'C:\Users\igapon\AppData\Roaming\Mozilla\Firefox\Profiles\h0rtj9e9.default-release'
url = "https://www.yahoo.co.jp/"


def func1():
    """通常版、対策されたサイトだと表示できない
    """
    options = Options()
    options.set_preference('profile', profile_path)
    service = Service(driver_path)
    with Firefox(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()


def func2():
    """set_preferenceが機能していないらしい
    https://stackoverflow.com/questions/69571950/deprecationwarning-firefox-profile-has-been-deprecated-please-pass-in-an-optio
    """
    options = Options()
    options.set_preference('profile', profile_path)
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    # フリープロキシサーバー検索
    # https://www.freeproxylists.net/ja/?c=US&pt=&pr=HTTP&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0
    # PROXY_HOST = "103.152.112.172"
    # PROXY_PORT = "80"
    # profile.set_preference("network.proxy.type", 1)
    # profile.set_preference("network.proxy.http", PROXY_HOST)
    # profile.set_preference("network.proxy.http_port", int(PROXY_PORT))
    # profile.add_experimental_option('devtools.jsonview.enabled', False)
    service = Service(driver_path)
    with Firefox(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()


def func3():
    """FireFoxは操作できない
    機能するが、すでに開いている別のインスタンスがある場合、firefoxを開かないらしい
    https://stackoverflow.com/questions/71474700/unable-to-load-existing-firefox-profile-with-selenium-4s-option-set-preference
    :return:
    """
    options = Options()
    # options.add_argument('-profile')
    # options.add_argument(profile_path)
    # options.add_argument('--width=600')
    # options.add_argument('--height=500')
    options.add_argument(f'--user-data-dir={profile_path}')
    service = Service(exec_path)
    # service = Service(driver_path)
    with Firefox(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()
    exit()


# func1()
# func2()
# func3()
