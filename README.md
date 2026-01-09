# Death Counter - Multi-Game Death Counter Installer

## Latest Version: v1.5

**DeathCounterInstaller.exe** - Complete standalone Windows installer with automatic Japanese language pack download for Sekiro support. Includes Python version compatibility checking (requires Python 3.8-3.13).

## Quick Start

1. Download **DeathCounterInstaller.exe**
2. Run the installer (double-click)
3. Follow the on-screen instructions to complete setup
4. Launch the Death Counter GUI

## Features

- **Automatic Setup**: Extracts all necessary files and dependencies
- **System Checks**: Verifies Python version (3.8-3.13), Tesseract OCR, and dependencies
- **Python Version Warning**: Alerts users if their Python version is incompatible
- **Auto-Download**: Automatically downloads Japanese language packs for Sekiro support
- **Streamer.bot Integration**: Easy import of Streamer.bot actions
- **Multi-Game Support**: Works with Elden Ring, Dark Souls series, Sekiro, and more
- **Multi-Resolution Support**: Works on any screen resolution (720p, 1080p, 1440p, 4K, ultrawide)
- **Windowed Mode Support**: Automatically detects and handles fullscreen, borderless, and windowed game modes
- **Multi-Monitor Support**: Handles games spanning multiple displays

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

### Main Branch Files

- **DeathCounterInstaller.exe** - Latest installer executable (v1.5). This is the main file users should download. Uses Git LFS for large file storage. Includes Python version compatibility checking and automatic Japanese language pack download for Sekiro support.

- **README.md** - This documentation file. Contains installation instructions, feature descriptions, repository structure, and troubleshooting information.

- **.gitattributes** - Git LFS configuration file. It tells Git which large files (e.g., `*.exe`) should be tracked by Git Large File Storage instead of directly in the Git repository. This prevents repository bloat and allows for easier management of large binaries.

- **.gitignore** - Git ignore rules. This file specifies intentionally untracked files that Git should ignore (e.g., temporary files, build artifacts, local configurations). It helps keep the repository clean and focused on source code.

- **cleanup_github_repo.ps1** - Utility PowerShell script used to organize the repository structure, remove old files, and copy the desired folder layout from a local reference folder. Helps maintain consistency between local development and GitHub repository.

- **create_release.ps1** - PowerShell script for creating GitHub releases. Can be used to automate the process of creating a new release with the installer executable as a downloadable asset.

### Folders

#### All Contents/
Contains all the main application files and resources needed to run the Death Counter. These are the files extracted by the `DeathCounterInstaller.exe` and are essential for the daemon and GUI to function. Includes:
- `multi_game_death_counter.py` - Main daemon script that performs screen capture, OCR detection, and death counting
- `death_counter_gui.py` - GUI application for controlling the daemon and viewing death statistics
- `games_config.json` - Configuration file defining game-specific settings (capture regions, keywords, process names)
- `switch_game_manual.py` - Script for manually switching between games
- `change_monitor_id.py` - Utility for changing monitor detection settings
- `capture_debug_once.py` - Debug utility for capturing a single screen region for testing
- `reset_death_counter.py` - Script to reset death counts to zero
- `test_daemon_start.py` - Test script to diagnose daemon startup issues
- `deathcounteraction.cs` - Streamer.bot action file for integration
- Batch files (`.bat`) for starting, stopping, and managing the daemon
- Other utility scripts and configuration files

#### Debug.Test/
Contains debug and testing utilities. These files are used for troubleshooting, testing OCR accuracy, and diagnosing issues with the death counter daemon. Useful for developers and advanced users who need to debug detection problems.

#### Edit/
Contains development scripts and source files used to build and maintain the installer. This folder is primarily for developers who want to modify or rebuild the installer. Includes:
- `build_single_file.py` - Build script that packages all application files into a single installer script. This script embeds all necessary files (Python scripts, configs, batch files) into `DeathCounter_Installer_Standalone.py`.
- `DeathCounter_Installer_Standalone.py` - The standalone installer script generated by `build_single_file.py`. This is the Python script version of the installer before it's compiled into an `.exe` using PyInstaller.
- Source copies of application files (for reference during build process)
- Other development utilities and scripts

## How It Works

The Death Counter uses Optical Character Recognition (OCR) to detect "YOU DIED" messages on screen:

1. **Screen Capture**: Continuously captures a specific region of the screen where death messages appear
2. **Image Processing**: Preprocesses the captured image (upscaling, sharpening, color masking) for better OCR accuracy
3. **OCR Detection**: Uses Tesseract OCR to detect death-related keywords ("YOU DIED", "死", etc.)
4. **Game Detection**: Automatically detects which game is running based on process names
5. **Death Counting**: Increments the death counter for the detected game
6. **Multi-Mode Support**: Automatically adapts to fullscreen, borderless, and windowed game modes
7. **Multi-Monitor Support**: Handles games spanning multiple displays

## System Requirements

- Windows 10/11
- Python 3.8-3.13 (auto-detected or installable via installer). The installer will warn if an incompatible Python version is detected.
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

1. **Python Version**: Ensure you have Python 3.8-3.13 installed. The installer will show a warning if your Python version is incompatible.
2. **Administrator Rights**: Ensure you're running the installer as Administrator (may be needed for Japanese pack installation)
3. **Tesseract OCR**: Check that Tesseract OCR is properly installed and accessible
4. **Internet Connection**: Verify internet connection for Japanese pack auto-download
5. **Log Files**: Check the log output in the installer for specific error messages
6. **Debug Tools**: Use files in `Debug.Test/` folder for troubleshooting OCR and detection issues

## Building the Installer

To rebuild the installer from source:

1. Ensure all source files are in the `Edit/` folder
2. Run `build_single_file.py` to create `DeathCounter_Installer_Standalone.py`
3. Use PyInstaller to compile: `pyinstaller --onefile --windowed --collect-all tkinter --name DeathCounterInstaller DeathCounter_Installer_Standalone.py`
4. The compiled `.exe` will be in the `dist/` folder

## License

See repository for license information.
