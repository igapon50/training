@echo off
REM �t�@�C�����̐擪�ɘA��3����}������
pushd folder01

setlocal enabledelayedexpansion
set prefix=
set pad=3
set num=0
for %%F in (*) do (
 rem ���̃o�b�`�t�@�C�����g��ΏۂɊ܂߂Ȃ�
 if not %%F==%~nx0 (
  set padnum=00000000!num!
  set extention=%%~xF
  ren %%F !padnum:~-%pad%!!prefix!_%%F
  echo %%F �� !padnum:~-%pad%!!prefix!_%%F
  set /a num+=1
 )
)
endlocal

popd
goto :EOF
