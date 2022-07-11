#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
サイトURLより、サイト内のサイトURLリストを取得する
サイトURLより、タイトルを取得する
サイトURLより、サイト末尾のimageURLを取得する

参考ブログ
https://yaspage.com/python-memo-selenium/
参考リファレンス
https://www.seleniumqref.com/api/webdriver_gyaku.html
https://www.selenium.dev/ja/documentation/webdriver/getting_started/

"""
import time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

xpath_actions = {"website": "//div/a/img",
                 "title": "//div/div/div/h2",
                 "last-image": "(//a/img)[last()]",
                 }
exec_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
driver_path = r'C:\Git\igapon50\traning\python\selenium\driver\chromedriver.exe'
profile_path = r''
url = "https://www.yahoo.co.jp/"


def func1():
    """通常版、対策されたサイトだと表示できない
    """
    options = Options()
    service = Service(driver_path)
    with Chrome(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()


def func2():
    """
    https://stackoverflow.com/questions/57122151/exclude-switches-in-firefox-webdriver-options
    set_preferenceが機能していないらしい
    https://stackoverflow.com/questions/69571950/deprecationwarning-firefox-profile-has-been-deprecated-please-pass-in-an-optio
    """
    options = Options()
    # options.add_experimental_option('profile', profile_path)
    # フリープロキシサーバー検索
    # https://www.freeproxylists.net/ja/?c=US&pt=&pr=HTTP&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0
    # PROXY_HOST = "103.152.112.172"
    # PROXY_PORT = "80"
    # options.add_experimental_option("network.proxy.type", 1)
    # options.add_experimental_option("network.proxy.http", PROXY_HOST)
    # options.add_experimental_option("network.proxy.http_port", int(PROXY_PORT))
    # options.add_experimental_option("dom.webdriver.enabled", False)
    # options.add_experimental_option('devtools.jsonview.enabled', False)
    PROXY = "<103.152.112.172:80>"
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "proxyType": "MANUAL",
    }
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(driver_path)
    with Chrome(service=service, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()


def func3():
    """既に開いているchromeを操作する
    https://qiita.com/mimuro_syunya/items/2464cd2404b67ea5da56
    """
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    with Chrome(executable_path=driver_path, options=options) as driver:
        driver.get(url)
        time.sleep(10)
        print(driver.current_url)
        print(driver.title)
        print("====== source =======================")
        print(driver.page_source)
        driver.quit()


func1()
# func2()
# func3()
