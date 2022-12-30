#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Google Home

参考ブログ
https://ppdr.softether.net/python-google-home-2021

参考Qiita
https://qiita.com/rukihena/items/8af9b8baed49542c033d#2022413-%E8%BF%BD%E8%A8%98

GitHub
pychromecast
https://github.com/home-assistant-libs/pychromecast
ｇTTS
https://github.com/pndurette/gTTS
"""
import pychromecast
from gtts import gTTS
import time
import sys


def get_speaker(ip_addr=None, name=None):
    if ip_addr:
        return pychromecast.Chromecast(str(ip_addr))
    speakers = pychromecast.get_chromecasts()
    if len(speakers) == 0:
        print('No devices are found')
        raise Exception
    if name:
        return next(s for s in speakers if s.device.friendly_name == name)
    return next(speakers)


def speak(text, speaker, lang='ja'):
    try:
        tts = gTTS(text=text, lang=lang)
        urls = tts.get_urls()
        if not speaker.is_idle:
            print("Killing current running app")
            speaker.quit_app()
            time.sleep(5)
        speaker.wait()
        speaker.media_controller.play_media(urls[0], 'audit/mp3')
        speaker.media_controller.block_until_active()
    except Exception as error:
        print(str(error))
        raise Exception


# LAN内に存在するcastデバイスの一覧を取得
# chromecasts = pychromecast.get_chromecasts()
services, cast = pychromecast.get_chromecasts()
# if browser.count == 0:
#     print("Google Homeが見つかりませんω")
#     exit()
# モデル名で探す
# googleHome = next(cc for cc in browser if cc.device.model_name == 'Google Home Mini')
# 名前で探す
chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["ダイニング ルーム"])
# chromecasts, browser = pychromecast.get_listed_chromecasts()
# googleHome = chromecasts[0]
# googleHome.wait()
# googleHome = next(cc for cc in chromecasts if cc.device.friendly_name == 'Living room/Dining room')
# castデバイスが見つからない場合、終了
# if browser.count == 0:
#     print("Google Homeが見つかりません")
#     sys.exit()
googleHome = browser[0]
text = '''
しゅくだい、したか、せんり
'''
# speak(text, speaker)
tts = gTTS(text=text, lang='ja')
urls = tts.get_urls()
# 最初に見つかったもの(同名のデバイスが複数あった場合)
if not googleHome.is_idle:
    print("Killing current running app")
    googleHome.quit_app()
    time.sleep(5)
googleHome.wait()
googleHome.media_controller.play_media(urls[0], 'audit/mp3')
googleHome.media_controller.block_until_active()
