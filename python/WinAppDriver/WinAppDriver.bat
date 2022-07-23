"%ProgramFiles(x86)%\Windows Application Driver\WinAppDriver.exe"
goto end
for /f "tokens=4" %%a in ('route print ^| findstr "\<0.0.0.0"') do set IP=%%a&goto NEXT
:NEXT
start /min "WinAppDriver" "%ProgramFiles(x86)%\Windows Application Driver\WinAppDriver.exe" %IP% 4723/wd/hub
:end