@echo off
REM Script to capture debug images
cd /d "%~dp0"
python capture_debug_once.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
