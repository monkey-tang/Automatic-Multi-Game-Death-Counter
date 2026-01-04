@echo off
REM Start Death Counter Daemon
REM This batch file starts the death counter daemon
REM Window will be positioned in top right corner

cd /d "%~dp0"

REM Position this console window to top right before starting
powershell -Command "$host.UI.RawUI.WindowPosition = New-Object System.Management.Automation.Host.Coordinates ((Get-Host).UI.RawUI.BufferSize.Width - 800), 0"

python multi_game_death_counter.py

pause

