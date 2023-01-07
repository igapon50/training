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
## Chocolaty

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
@powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin
```


### 参考

- [chocolatey基本情報まとめ](https://qiita.com/NaoyaOura/items/1081884068fe3ea79570)


## PyCharm(統合開発環境)

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
choco install pycharm-community
```

- 途中選択肢が出る場合は、すべてy + Enterする。
- 日本語化のために[Pleiadesプラグインをダウンロード](http://mergedoc.osdn.jp/)
- zipを解凍してsetup.exeを起動
- 日本語化するアプリケーションとして"C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2020.3.3\bin\pycharm64.exe"を選択


### 参考

- [PyCharmインストール（Windows編）](https://startappdevfrom35.com/pycharminstallforwindows/)
- [pycharmの日本語化](https://qiita.com/y-sato19/items/46bc0f8c8f91f51564e0)
- [Git リポジトリをセットアップする](https://pleiades.io/help/pycharm/set-up-a-git-repository.html)


## Doxygen(Doxygen形式)

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
choco install doxygen.install
```

- 途中選択肢が出る場合は、すべてy + Enterする。


### 参考

- [Doxygen.jp](http://www.doxygen.jp/)
- [Doxygen リファレンスメモ](https://cercopes-z.com/Doxygen/)


## PlantUML(java除く)

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
choco install plantuml
choco install graphviz
```

- 途中選択肢が出る場合は、すべてy + Enterする。
- 以下のBATファイルで、拡張子puのファイルからUML図を作成する

```commandline:
@echo off
if "%1"=="" (
java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar C:\ProgramData\chocolatey\bin\dot.exe *.pu
) else (
java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar C:\ProgramData\chocolatey\bin\dot.exe %1
)
```

### 参考

- [PlantUML使い方メモ](https://qiita.com/opengl-8080/items/98c510b8ca060bdd2ea3)


## Selenium

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
pip install chromedriver-binary
pip install selenium
pip install webdriver-manager
```


### 参考

- [【Selenium】ChromeDriverを自動更新するPythonライブラリが便利](https://yuki.world/python-selenium-chromedriver-auto-update/)
- [【Python/Selenium】ChromeDriverバージョンエラー対処法](https://yuki.world/python-chrome-driver-version-error/)


## python/AWS_S3
AWS S3バケットへのデータバックアップとリストアする

- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
pip install boto3
pip install awscli
```

### 参考(AWS_S3)

- [Windows のデータを Amazon S3 へバックアップする](https://codebookshelf.com/2017/06/windows-%E3%81%AE%E3%83%87%E3%83%BC%E3%82%BF%E3%82%92-amazon-s3-%E3%81%B8%E3%83%90%E3%83%83%E3%82%AF%E3%82%A2%E3%83%83%E3%83%97%E3%81%99%E3%82%8B/)


## Python/Movie
- Windowsキーを押す
- 検索ボックスに「cmd」と入力
- Ctrl + Shift + Enterを押す(管理者として実行)
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
choco install ffmpeg
```

- 途中選択肢が出る場合は、すべてy + Enterする。
- 以下のコマンドを実行する

```commandline:cmd.exe（管理者として実行）
pip install soundfile
pip install numpy
```


### 参考

- [Pythonでのwavファイル操作](https://qiita.com/Dsuke-K/items/2ad4945a81644db1e9ff)
- [PythonでYouTube用動画のカットとテロップ挿入を自動化してみた！](https://kajimublog.com/python-video-cut/)


# python/Web_scraping
クローリングして、スクレイピングして、画像URLリストを作り、その画像をまとめてダウンロードして、ファイル名をナンバリングして、zipファイルにアーカイブする。

使い方はユニットテスト（例えば、test_crawling.py）を参照のこと

- chromeDriverHelper: selenium chromeドライバーのヘルパークラス
- crawling: クローリングヘルパークラス
  - web巡回して、スクレイピングして、ファイルダウンロードして、zipファイルにまとめる
- egoser_zipper: google 画像検索して、先頭20サムネイル画像をzipにまとめる
- irvineHelper: Irvineを操作するヘルパークラス
- uriHelper: URLのヘルパークラス
  - URLのパス、ファイル名、拡張子、DataURIのデータ、ファイルの存在確認など
- webFileHelper: webファイルのヘルパークラス
  - URLから、ダウンロードしたり、ファイル名変更したり、存在確認したり、削除したりする
- webFileListHelper: webファイルリストのヘルパークラス
  - URLリストから、webFileHelperのリストを作って、操作する。まとめてだウンロードしたり、zipファイルにする

以下は古い

- imgdl：クリップボードからURLを読み込み、urllib.requestでWeb情報を取得し、スクレイピングして、画像URLリストを作り、その画像をダウンロードして、ファイル名をナンバリングして、zipファイルに保存する
- HTML2zip：画像のダウンロード処理だけ行わない他はimgdlと同じ(ダウンロードは外部ツールを使う)
- HTML2imglist：クリップボードからURLを読み込み、スクレイピングして、画像URLリストを作り、クリップボードとファイルに保存する
- imglist2clip：ファイルから読み込み、クリップボードにコピーする
- imglist2zip：ファイルから読み込み、ファイル名をナンバリングして、zipファイルに保存する
- makezip：ダウンロードフォルダ(folder01)以下を、zipファイルに保存する
- folder01Rename：folder01以下のファイルについて、ファイル名の先頭に連番3桁を挿入する


### 参考

- [note.nkmk.me Python関連記事まとめ](https://note.nkmk.me/python-post-summary/)
- [querySelectorAll CSSセレクタ](https://developer.mozilla.org/ja/docs/Web/API/Element/querySelectorAll)
- [Python URL操作](https://villhell.com/2019/07/30/python-url/)
- [README作成補助](https://qiita.com/Kyome/items/2112e9d1871ec0a367ea?utm_source=Qiita%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&utm_campaign=615586dc3e-Qiita_newsletter_425_08_26_2020_COPY_02&utm_medium=email&utm_term=0_e44feaa081-615586dc3e-33718969)
- [Irvine](http://hp.vector.co.jp/authors/VA024591/doc/manual.html)


# python/selenium
[python/Web_scraping](https://github.com/igapon50/training/tree/develop#pythonweb_scraping)
では、Web情報の取得にurllib.requestを使用したが、ここではseleniumを使用する

- imgdl：クリップボードからURLを読み込み、FireFoxでWeb情報を取得し、スクレイピングして、画像URLリストを作り、その画像をダウンロードして、ファイル名をナンバリングして、zipファイルに保存する


### 参考

- [【完全版】PythonとSeleniumでブラウザを自動操作(クローリング／スクレイピング)するチートシート](https://tanuhack.com/selenium/)
- [PythonでSeleniumを操作する](https://kurozumi.github.io/selenium-python/index.html)
- [Selenium クリックリファレンスAPI(逆引き)](https://www.seleniumqref.com/api/webdriver_gyaku.html)


# python/AWS_S3
aws s3 syncコマンドは、とりあえずおいといて、AWS S3のバケットと、ローカルフォルダを同期したり操作する。削除は反映できないけど。

- listall：S3バケットとローカルフォルダのオブジェクト情報を取得して、結果ファイルに書き出す
- uploadS3：S3バケットとローカルフォルダのオブジェクト情報を取得して、localよりbucketの日付が古いファイルをアップロードする


### 参考

- [Boto3 Docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html#)
  ([S3.ServiceResource](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#service-resource)
  /[S3.Bucket](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket)
  /[S3.Object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object)
  )
- [boto3を使ってS3をごにょごにょする](https://qiita.com/is_ryo/items/e16527db5800854cd95f)
- [Boto3 で S3 のオブジェクトを操作する（高レベルAPIと低レベルAPI）](https://qiita.com/sokutou-metsu/items/5ba7531117224ee5e8af)
- [Boto3でS3のリスト出力をするときは、list_objects_v2ではなくBucket().objects.filterを使おう](https://qiita.com/elyunim26/items/a513226b76b3cb8928c2)
- [AWS SDK for Python (Boto3) で S3 のオブジェクトの所有者情報を取得する際に気をつけること](https://blog.serverworks.co.jp/boto3-python-s3-object)


# python/Movie
動画から無音部分をカットするために、有音部分を切り出す

- movieCutter：指定したmovファイルから、有音部分のmovを切り出す


### 参考

- [PythonでYouTube用動画のカットとテロップ挿入を自動化してみた！](https://kajimublog.com/python-video-cut/)
