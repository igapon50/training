#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WinAppDriver APIと互換性のない現在のリリースではなく、
Appium-Python-Client==0.24およびselenium==3.5.0を使用していることを確認してください。
pip list
pip install Appium-Python-Client==0.24
pip install selenium==3.5.0
"""
import time
import subprocess

from appium import webdriver
from selenium.webdriver.common.keys import Keys


# cmd = r'c:\Program1\irvine1_3_0\irvine.exe ./result_list.txt'
cmd = r'c:\Program1\irvine1_3_0\irvine.exe'
# proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
desired_caps = {}
# 起動する場合
desired_caps["app"] = cmd
# desired_caps["appTopLevelWindow"] =
# desired_caps["appArguments"] = "./result_list.txt"
# desired_caps["appWorkingDir"] = r"C:\MyTestFolder" + "\\"

driver = webdriver.Remote(
    command_executor='http://127.0.0.1:4723',
    desired_capabilities=desired_caps)

# app = driver.find_element_by_class_name('#32769')
# elem = app.FindElementByXPath('//Pane[@ClassName="TCanvasPanel"]')
# print(elem.text)
time.sleep(1)
# app.find_element_by_accessibility_id('閉じる').click()
driver.quit()
