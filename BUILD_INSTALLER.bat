@echo off
REM Build Installer EXE for Death Counter
REM This creates a single installer EXE that handles everything

echo ========================================
echo Building Death Counter Installer
echo ========================================
echo.

cd /d "%~dp0"

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Building Installer executable...
echo.

REM Build the installer as a windowed application (no console)
REM Include all necessary files as data files
pyinstaller --onefile --windowed --name "DeathCounterInstaller" ^
    --add-data "multi_game_death_counter.py;." ^
    --add-data "death_counter_gui.py;." ^
    --add-data "death_counter_settings.py;." ^
    --add-data "log_monitor.py;." ^
    --add-data "memory_scanner.py;." ^
    --add-data "games_config.json;." ^
    --add-data "reset_death_counter.py;." ^
    --add-data "switch_game_manual.py;." ^
    --add-data "capture_debug_once.py;." ^
    --add-data "change_monitor_id.py;." ^
    --add-data "requirements.txt;." ^
    --add-data "README.md;." ^
    --add-data "FUZZY_MATCHING_GUIDE.md;." ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    --noconfirm ^
    --clean ^
    installer.py

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Installer created:
echo   - dist\DeathCounterInstaller.exe
echo.
echo This single EXE installer will:
echo   - Extract all files to chosen directory
echo   - Install Python dependencies
echo   - Create shortcuts
echo   - Set up configuration files
echo.
pause
