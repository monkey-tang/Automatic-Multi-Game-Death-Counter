@echo off
REM Script to easily change monitor ID for games
cd /d "%~dp0"
python change_monitor_id.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
