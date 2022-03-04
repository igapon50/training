@echo off
python urlDeployment.py %1 %2
PAUSE
echo ダウンロードが終わったら、irvineを終了してください。
c:\Program1\irvine1_3_0\irvine.exe ./result_list.txt
PAUSE
.\folder01Rename.bat
PAUSE
.\makezip.bat
