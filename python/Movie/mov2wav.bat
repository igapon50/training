@echo off
if "%1"=="" (
echo エラー、引数にmovファイル名を渡してください
) else (
ffmpeg -i %1 -ac 1 -ar 44100 -acodec pcm_s16le %~n1.wav
)