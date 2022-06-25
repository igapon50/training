#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
サイトURLより、サイト内のサイトURLリストを取得する
サイトURLより、タイトルを取得する
サイトURLより、サイト末尾のimageURLを取得する

参考ブログ
https://yaspage.com/python-memo-selenium/

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# サイトURL
url = "https://www.yahoo.co.jp/"
# xpathと操作辞書
xpath_actions = {"website": "//div/a/img",
                 "title": "//div/div/div/h2",
                 "last-image": "(//a/img)[last()]",
                 }
op = Options()
# op.add_argument('--headless')
# Firefoxを操作
with webdriver.Firefox(
        executable_path="C:/Git/igapon50/traning/python/selenium/geckodriver-v0.31.0-win64/geckodriver.exe", option=op
) as driver:
    # フルパスを指定
    driver.get(url)
    # ここで「Checking your browser before accessing XXX」になる場合はjavascriptが無効だとだめらしい
    # https://blog.halpas.com/archives/12207
    print(driver.current_url)
    driver.quit()

# url_list = driver.find_element(By.XPATH, xpath_actions["website"]).get_attribute('href')
# for item in url_list:
#     driver.get(item)
#     print(driver.current_url)
#     print(driver.find_element(By.XPATH, xpath_actions["title"]).text())
#     print(driver.find_element(By.XPATH, xpath_actions["last-image"]).get_attribute('href'))
# # ブラウザを終了する
# driver.quit()
