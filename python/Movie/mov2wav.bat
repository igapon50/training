@echo off
if "%1"=="" (
echo �G���[�A������mov�t�@�C������n���Ă�������
) else (
ffmpeg -i %1 -ac 1 -ar 44100 -acodec pcm_s16le %~n1.wav
)