@echo off
REM ファイル名の先頭に連番3桁を挿入する
pushd folder01

setlocal enabledelayedexpansion
set prefix=
set pad=3
set num=0
for %%F in (*) do (
 rem このバッチファイル自身を対象に含めない
 if not %%F==%~nx0 (
  set padnum=00000000!num!
  set extention=%%~xF
  ren %%F !padnum:~-%pad%!!prefix!_%%F
  echo %%F → !padnum:~-%pad%!!prefix!_%%F
  set /a num+=1
 )
)
endlocal

popd
goto :EOF
