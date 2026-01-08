@echo off
REM Reset Death Counter
REM This batch file resets all death counts to 0

cd /d "%~dp0"
python reset_death_counter.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)

