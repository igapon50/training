@echo off
@REM 参考：https://qiita.com/yoshi-kin/items/e0a7336a288188913097
setlocal
cd /d %~dp0

@REM chromeのインストール場所から、バージョンの数字を調べる。インストール場所は環境による
dir /B /O-N "%PROGRAMFILES(X86)%/Google/Chrome/Application" | findstr "^[0-9]." > "chrome_version.txt"
@REM chromeバージョンのhead部分をテキストファイルに出力
for /f "tokens=1 delims=:." %%a in (chrome_version.txt) do echo %%a> chrome_version_h.txt
@REM テキストファイルからchromeバージョンのheadを変数に入れる
set /p version_head= 0<"chrome_version_h.txt"
pip install chromedriver-binary=="%version_head%.*"

echo ブラウザを起動する
"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe" -remote-debugging-port=9222 --user-data-dir="C:\Users\igapon\temp"
netstat -nao | find ":9222"