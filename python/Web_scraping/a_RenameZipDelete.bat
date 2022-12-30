@echo off
REM folder01フォルダー内のファイルについて、ファイル名の先頭に連番3桁を挿入する
call .\folder01Rename.bat
REM folder01フォルダーを圧縮して、folder01フォルダー内のファイルを削除する
call .\makezip.bat