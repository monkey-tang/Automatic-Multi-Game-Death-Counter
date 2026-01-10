# Multi-Game Soulsborne Death Counter Installer

## Overview

Two installer versions are available:

### Online Installer (`DeathCounterInstaller-online.exe`)
- **Location:** `online-exe/` folder
- **Size:** ~10MB
- **Requires:** Internet connection for dependency installation
- **Best for:** Most users who have internet access

### Offline Installer (`DeathCounterInstaller-offline.exe`)
- **Location:** `offline-exe/` folder
- **Size:** ~71MB
- **Requires:** No internet (all dependencies bundled)
- **Best for:** Offline environments or when you want a self-contained installer

Both installers are single EXE files that handle everything automatically:

1. **Extracts all files** to your chosen installation directory
2. **Installs Python dependencies** automatically (if Python is found)
3. **Creates desktop shortcut** for easy access
4. **Sets up configuration files** with default settings
5. **Checks for Tesseract OCR** and provides installation instructions if missing

## Building the Installers

### Building the Online Installer

```bash
BUILD_INSTALLER.bat
```

This creates `dist\DeathCounterInstaller-online.exe` (~10MB) - requires internet for pip install.

### Building the Offline Installer

```bash
BUILD_INSTALLER_OFFLINE.bat
```

This creates `dist\DeathCounterInstaller-offline.exe` (~71MB) - all dependencies bundled, works offline.

**Note:** The offline installer build requires all dependencies to be installed in your Python environment first.

## What the Installer Includes

### Python Files (Extracted to installation directory)
- `multi_game_death_counter.py` - Main daemon
- `death_counter_gui.py` - GUI application
- `death_counter_settings.py` - Settings GUI
- `log_monitor.py` - Log file monitoring
- `memory_scanner.py` - Memory scanning
- All utility scripts

### Configuration Files
- `games_config.json` - Game configurations
- `requirements.txt` - Python dependencies list

### Batch Files (Created during installation)
- `START_DEATH_COUNTER.bat` - Start daemon
- `STOP_DEATH_COUNTER.bat` - Stop daemon
- `RESET_DEATH_COUNTER.bat` - Reset death counts
- `CAPTURE_DEBUG.bat` - Capture debug images
- `CHANGE_MONITOR_ID.bat` - Change monitor settings

## Installer Features

### GUI Interface
- Select installation directory (defaults to Desktop\DeathCounter)
- Options to:
  - Create desktop shortcut
  - Install Python dependencies automatically
  - Check for Tesseract OCR
- Progress bar and detailed log
- Error handling and user-friendly messages

### Requirements Checking
- Checks for Python 3.8-3.12
- Verifies Python is in PATH or finds it in common locations
- Installs dependencies from `requirements.txt`
- Checks for Tesseract OCR installation

### Post-Installation
- Creates `death_state.json` if it doesn't exist
- Creates desktop shortcut (if requested)
- Provides clear instructions on how to start the application

## User Experience

1. **Run `DeathCounterInstaller.exe`**
2. **Choose installation directory** (or use default)
3. **Select options** (shortcut, auto-install dependencies, etc.)
4. **Click "Install"**
5. **Wait for installation** (progress shown in real-time)
6. **Done!** - Files extracted and ready to use

## What Happens After Installation

Users can then:
- Double-click the desktop shortcut to open the GUI
- Or run `START_DEATH_COUNTER.bat` to start the daemon
- Or run `python death_counter_gui.py` from the installation directory

## Notes

- The installer requires Python to be installed (it will check)
- Tesseract OCR must be installed separately (installer will check and warn)
- All dependencies will be installed automatically if the option is selected
- The installer creates a complete, working installation in one step

## Technical Details

- Built with PyInstaller as a single-file executable
- Uses tkinter for GUI (no external GUI dependencies)
- Extracts files from PyInstaller's temporary bundle (_MEIPASS)
- Handles both script mode (development) and EXE mode (production)
- Gracefully handles missing optional dependencies (like pywin32 for shortcuts)
