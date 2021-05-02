#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
# @file downloadS3.py
# @version 1.0.0
# @author Ryosuke Igarashi(HN:igapon)
# @date 2021/05/02
# @brief AWS S3の指定バケットのファイル群をローカルにダウンロードする
# @details 
# @warning 
# @note 

# local source
from const import *
from func import *

if __name__ == '__main__':  # インポート時には動かない
    # 引数チェック
    if 2 == len(sys.argv):
        # Pythonに以下の2つ引数を渡す想定
        # 0は固定でスクリプト名
        # 1.書き込むファイルパス
        write_filepath = sys.argv[1]
    elif 1 == len(sys.argv):
        # 引数がなければデフォルト
        # 0は固定でスクリプト名
        write_filepath = RESULT_FILE_PATH
    else:
        print('引数が不正です。')
        print(msg_error_exit)
        sys.exit(False)

    # bucketに接続する
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
    # bucketの情報を取得する
    bucket_dic = {'Book/test.txt': 100}
    ret = get_bucket_filelist(bucket, BUCKET_FILELIST_PATH, bucket_dic)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # ローカルの情報を取得する
    local_dic = {'Book\\test.txt': 100}
    ret = get_local_filelist(OUTPUT_FOLDER_PATH, TARGET_FILELIST_PATH, local_dic)
    if not ret:
        print(msg_error_exit)
        sys.exit(ret)

    # 情報を比較してdownloadするファイルリストを作成する
    # ファイルリストに従いdownloadする
    sys.exit(ret)
