# training

<!-- # Short Description -->

各種トレーニング

<!-- # Badges -->

[![Github issues](https://img.shields.io/github/issues/igapon50/training)](https://github.com/igapon50/training/issues)
[![Github forks](https://img.shields.io/github/forks/igapon50/training)](https://github.com/igapon50/training/network/members)
[![Github stars](https://img.shields.io/github/stars/igapon50/training)](https://github.com/igapon50/training/stargazers)
[![Github top language](https://img.shields.io/github/languages/top/igapon50/training)](https://github.com/igapon50/training/)
[![Github license](https://img.shields.io/github/license/igapon50/training)](https://github.com/igapon50/training/)

# Contributors

- [igapon50](https://github.com/igapon50)

<!-- CREATED_BY_LEADYOU_README_GENERATOR -->

# 開発環境
PyCharm(統合開発環境)
- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押し(管理者として実行)、以下のコマンドを実行する
```commandline:title
choco install pycharm-community
```
- 日本語化のために[Pleiadesプラグインをダウンロード](http://mergedoc.osdn.jp/)
- zipを解凍してsetup.exeを起動
- 日本語化するアプリケーションとして"C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2020.3.3\bin\pycharm64.exe"を選択

Doxygen(Doxygen形式)

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押し(管理者として実行)、以下のコマンドを実行する
```commandline:title
choco install doxygen.install
```

### 参考(開発環境)
- [PyCharmインストール（Windows編）](https://startappdevfrom35.com/pycharminstallforwindows/)
- [pycharmの日本語化](https://qiita.com/y-sato19/items/46bc0f8c8f91f51564e0)
- [Git リポジトリをセットアップする](https://pleiades.io/help/pycharm/set-up-a-git-repository.html)
- [Doxygen.jp](http://www.doxygen.jp/)
- [Doxygen リファレンスメモ](https://cercopes-z.com/Doxygen/)

## python/Web_scraping
スクレイピングで、画像URLリストを作り、その画像をダウンロードして、ファイル名をナンバリングして、zipファイルにアーカイブする。
- imgdl：クリップボードからURLを読み込み、スクレイピングして、画像URLリストを作り、その画像をダウンロードして、ファイル名をナンバリングして、zipファイルに保存する
- HTML2zip：画像のダウンロード処理だけ行わない他はimgdlと同じ(ダウンロードは外部ツールを使う)
- HTML2imglist：クリップボードからURLを読み込み、スクレイピングして、画像URLリストを作り、クリップボードとファイルに保存する
- imglist2clip：ファイルから読み込み、クリップボードにコピーする
- imglist2zip：ファイルから読み込み、ファイル名をナンバリングして、zipファイルに保存する
- makezip：ダウンロードフォルダ(folder01)以下を、zipファイルに保存する
- folder01Rename：folder01以下のファイルについて、ファイル名の先頭に連番3桁を挿入する

### 参考(Web_scraping)
- [note.nkmk.me Python関連記事まとめ](https://note.nkmk.me/python-post-summary/)
- [querySelectorAll CSSセレクタ](https://developer.mozilla.org/ja/docs/Web/API/Element/querySelectorAll)
- [Python URL操作](https://villhell.com/2019/07/30/python-url/)
- [README作成補助](https://qiita.com/Kyome/items/2112e9d1871ec0a367ea?utm_source=Qiita%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&utm_campaign=615586dc3e-Qiita_newsletter_425_08_26_2020_COPY_02&utm_medium=email&utm_term=0_e44feaa081-615586dc3e-33718969)
- [Irvine](http://hp.vector.co.jp/authors/VA024591/doc/manual.html)


## python/AWS_S3
AWS S3バケットへのデータバックアップとリストアする
- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押し(管理者として実行)、以下のコマンドを実行する
```commandline:title
python.exe -m pip install --upgrade pip
pip install boto3
pip install awscli
```

### 参考(AWS_S3)
- [Boto3 Docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html#)
  ([S3.ServiceResource](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#service-resource)
  /[S3.Bucket](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket)
  /[S3.Object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object)
  )
- [Windows のデータを Amazon S3 へバックアップする](https://codebookshelf.com/2017/06/windows-%E3%81%AE%E3%83%87%E3%83%BC%E3%82%BF%E3%82%92-amazon-s3-%E3%81%B8%E3%83%90%E3%83%83%E3%82%AF%E3%82%A2%E3%83%83%E3%83%97%E3%81%99%E3%82%8B/)
- [boto3を使ってS3をごにょごにょする](https://qiita.com/is_ryo/items/e16527db5800854cd95f)
- [Boto3 で S3 のオブジェクトを操作する（高レベルAPIと低レベルAPI）](https://qiita.com/sokutou-metsu/items/5ba7531117224ee5e8af)
- [Boto3でS3のリスト出力をするときは、list_objects_v2ではなくBucket().objects.filterを使おう](https://qiita.com/elyunim26/items/a513226b76b3cb8928c2)
- [AWS SDK for Python (Boto3) で S3 のオブジェクトの所有者情報を取得する際に気をつけること](https://blog.serverworks.co.jp/boto3-python-s3-object)
