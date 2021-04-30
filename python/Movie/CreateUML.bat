@echo off
if "%1"=="" (
java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar C:\ProgramData\chocolatey\bin\dot.exe *.pu
) else (
java -jar C:\ProgramData\chocolatey\lib\plantuml\tools\plantuml.jar C:\ProgramData\chocolatey\bin\dot.exe %1
)
