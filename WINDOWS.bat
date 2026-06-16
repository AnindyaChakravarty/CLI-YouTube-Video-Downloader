@echo off
setlocal
cd /d "%~dp0"

title YouTube Downloader Launcher

if not exist "%~dp0run.ps1" (
    echo ERROR: run.ps1 was not found beside start.bat.
    echo.
    pause
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Launcher stopped with error code %EXIT_CODE%.
    echo Check the messages above.
    echo.
    pause
)

exit /b %EXIT_CODE%