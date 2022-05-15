@echo off
REM ファイル名の先頭に連番3桁を挿入する
pushd folder01
setlocal enabledelayedexpansion
set prefix=
set pad=3
for %%F in (*) do (
 rem このバッチファイル自身を対象に含めない
 if not %%F==%~nx0 (
  set padnum=00000000%%~nF
  set extention=%%~xF
  ren %%F !padnum:~-%pad%!!prefix!_%%F
  echo %%F → !padnum:~-%pad%!!prefix!_%%F
 )
)
endlocal
popd
REM goto :EOF
