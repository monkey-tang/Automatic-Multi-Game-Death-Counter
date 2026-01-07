# Death Counter - Multi-Game Death Counter Installer

## Latest Version: v1.5

**DeathCounterInstaller.exe** - Complete standalone Windows installer with automatic Japanese language pack download for Sekiro support.

## Quick Start

1. Download **DeathCounterInstaller.exe**
2. Run the installer (double-click)
3. Follow the on-screen instructions to complete setup
4. Launch the Death Counter GUI

## Features

- **Automatic Setup**: Extracts all necessary files and dependencies
- **System Checks**: Verifies Python, Tesseract OCR, and dependencies
- **Auto-Download**: Automatically downloads Japanese language packs for Sekiro support
- **Streamer.bot Integration**: Easy import of Streamer.bot actions
- **Multi-Game Support**: Works with Elden Ring, Dark Souls series, Sekiro, and more
- **Multi-Resolution Support**: Works on any screen resolution (720p, 1080p, 1440p, 4K, ultrawide)

## Installation Steps

1. Click **"Install/Update Files"** → Extracts all application files
2. Click **"Install Python"** (if needed) → Opens Python download page
3. Click **"Install Tesseract"** (if needed) → Opens Tesseract download page  
4. Click **"Install Dependencies"** → Installs all required Python packages
5. Click **"Streamer.bot Download"** (if needed) → Opens Streamer.bot download page
6. Click **"Import to Streamer.bot"** → Opens Streamer.bot import dialog
7. Click **"✓ Confirm Import"** → Enables the launch button
8. Click **"Launch Death Counter"** → Starts the Death Counter GUI application

## Repository Structure

### Main Branch (Current)
- **DeathCounterInstaller.exe** - Latest installer (v1.5)
- **README.md** - This file
- **death counter source/** - All source code and scripts

### Source Files
All source code, scripts, and configuration files are located in the **`death counter source/`** folder:
- `1multi_game_death_counter.py` - Main daemon script
- `1death_counter_gui.py` - GUI application
- `1games_config.json` - Game configuration
- `DeathCounter_Installer_Standalone.py` - Installer source code
- `build_single_file.py` - Build script
- `reset_death_counter.py` - Reset script
- `test_daemon_start.py` - Test script
- Streamer.bot action files (`.cs` files)
- Batch files and utilities

### Old Versions
Previous installer versions (v1.1 - v1.6) are available in the **`old-versions`** branch.

## System Requirements

- Windows 10/11
- Python 3.8-3.13 (auto-detected or installable via installer)
- Tesseract OCR (auto-downloadable via installer)
- Internet connection (for initial setup and Japanese pack download)

## Supported Games

- Elden Ring
- Dark Souls Remastered
- Dark Souls II
- Dark Souls III
- Sekiro: Shadows Die Twice (with Japanese character support)

## Troubleshooting

If you encounter issues:
1. Ensure you're running the installer as Administrator
2. Check that Python and Tesseract OCR are properly installed
3. Verify internet connection for Japanese pack auto-download
4. Check the log output in the installer for specific error messages

## License

See repository for license information.
