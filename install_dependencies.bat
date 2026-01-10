@echo off
REM Install Python Dependencies for Death Counter
REM This batch file installs all required Python packages

echo Installing dependencies for Death Counter...
echo.

cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install mss pillow pytesseract opencv-python numpy psutil watchdog

echo.
echo Installation complete!
echo.
echo Note: You also need to install Tesseract OCR separately:
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo Default path: C:\Program Files\Tesseract-OCR\tesseract.exe
echo.
echo Optional dependencies installed:
echo   - watchdog: Required for log file monitoring (Method 2)
echo   - Memory scanning (Method 3) uses Windows APIs, no extra dependencies needed
echo.
pause
