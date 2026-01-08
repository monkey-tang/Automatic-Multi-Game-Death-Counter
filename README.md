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
- **Windowed Mode Support**: Automatically detects and supports fullscreen, windowed, and borderless window modes
- **Multi-Monitor Support**: Handles games spanning across multiple displays

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

- **DeathCounterInstaller.exe** - Latest installer executable (v1.5). This is the main file users should download. Uses Git LFS for large file storage.
- **README.md** - This documentation file (you are here)
- **.gitattributes** - Git LFS configuration for tracking large files
- **.gitignore** - Git ignore rules for the repository
- **cleanup_github_repo.ps1** - Utility script used to organize the repository structure

### Folders

#### All Contents/
Contains all the main application files and resources needed to run the Death Counter:

**Core Application Files:**
- `multi_game_death_counter.py` - Main daemon script that runs in the background, detects game windows, captures screen regions, and performs OCR to count deaths
- `death_counter_gui.py` - GUI application for controlling the daemon and displaying death counts
- `games_config.json` - Configuration file containing game-specific settings (capture regions, keywords, Tesseract settings)

**Batch Files (Utilities):**
- `START_DEATH_COUNTER.bat` - Starts the death counter daemon
- `STOP_DEATH_COUNTER.bat` - Stops the death counter daemon
- `CAPTURE_DEBUG.bat` - Captures a debug screenshot for troubleshooting
- `CHANGE_MONITOR_ID.bat` - Utility to change which monitor the counter monitors
- `RESET_DEATH_COUNTER.bat` - Resets all death counts to zero
- `install_dependencies.bat` - Installs required Python packages

**Python Scripts:**
- `switch_game_manual.py` - Manual game switching utility
- `change_monitor_id.py` - Script to change monitor ID for capture
- `capture_debug_once.py` - One-time debug capture script
- `reset_death_counter.py` - Script to reset death counts
- `test_daemon_start.py` - Test script to diagnose daemon startup issues

**Configuration & Data Files:**
- `deathcounteraction.cs` - Streamer.bot action file for integration
- `death_state.json` - Current state file (tracks active game, deaths, etc.)
- `current_deaths.txt` - Current session death count
- `current_game.txt` - Currently detected game
- `death_counter.txt` - Main death counter output file
- `death_counter_Elden_Ring.txt` - Elden Ring specific death count
- `total_deaths.txt` - Total death count across all games

**Lock & Status Files:**
- `daemon.lock` - Lock file to prevent multiple daemon instances
- `daemon.ready` - Status file indicating daemon is ready
- `daemon_startup_error.txt` - Error log from daemon startup

**Log Files:**
- `debug.log` - Debug logging output
- `gui_debug.log` - GUI debug logging

**Debug Images:**
- `debug_capture.png` - Processed debug screenshot
- `debug_capture_raw.png` - Raw debug screenshot

#### Debug.Test/
Contains debugging and testing utilities:

- `CAPTURE_DEBUG.bat` - Debug capture batch file
- `capture_debug_once.py` - One-time debug capture script
- `test_daemon_start.py` - Daemon startup test script
- `debug_capture.png` - Debug screenshot output
- `debug_capture_raw.png` - Raw debug screenshot output

#### Edit/
Contains utility scripts for editing and managing the death counter:

**Batch Files:**
- `START_DEATH_COUNTER.bat` - Start daemon utility
- `STOP_DEATH_COUNTER.bat` - Stop daemon utility
- `CHANGE_MONITOR_ID.bat` - Change monitor ID utility
- `RESET_DEATH_COUNTER.bat` - Reset death counts utility

**Python Scripts:**
- `build_single_file.py` - Build script that creates the standalone installer by embedding all files into a single Python script, which is then compiled into DeathCounterInstaller.exe using PyInstaller
- `change_monitor_id.py` - Script to change monitor ID
- `reset_death_counter.py` - Script to reset death counts
- `switch_game_manual.py` - Manual game switching script

## System Requirements

- Windows 10/11
- Python 3.8-3.13 (auto-detected or installable via installer)
- Tesseract OCR (auto-downloadable via installer)
- Internet connection (for initial setup and Japanese pack download)

## Supported Games

- **Elden Ring** - Full support with automatic detection
- **Dark Souls Remastered** - Full support with automatic detection
- **Dark Souls II** - Full support with automatic detection
- **Dark Souls III** - Full support with automatic detection
- **Sekiro: Shadows Die Twice** - Full support with Japanese character recognition (requires Japanese language pack, auto-downloaded by installer)

## Window Modes Supported

The death counter automatically detects and supports:
- **Fullscreen Mode** - Traditional fullscreen gameplay
- **Windowed Mode** - Resizable windowed gameplay with automatic position tracking
- **Borderless Windowed Mode** - Borderless fullscreen window mode

The counter also handles:
- **Multi-Monitor Setups** - Automatically detects when games span across multiple displays
- **Dynamic Window Movement** - Tracks window position changes in real-time
- **Resolution Scaling** - Works with any resolution by converting coordinates to percentage-based regions

## How It Works

1. **Game Detection**: The daemon (`multi_game_death_counter.py`) continuously monitors running processes to detect supported games
2. **Window Detection**: Once a game is detected, it finds the game window and determines its position and size
3. **Screen Capture**: Captures a specific region of the screen where death text appears (configured per game in `games_config.json`)
4. **OCR Processing**: Uses Tesseract OCR to read text from the captured region, with game-specific preprocessing (color masking, thresholding, upscaling)
5. **Death Detection**: Analyzes OCR results for death-related keywords, with false positive prevention (consecutive hits, cooldowns, keyword exclusion)
6. **State Management**: Updates death counts and writes to text files for Streamer.bot integration
7. **Streamer.bot Integration**: Streamer.bot reads the death count files and can trigger actions based on death events

## Troubleshooting

If you encounter issues:

1. **Installer Issues:**
   - Ensure you're running the installer as Administrator
   - Check that Python and Tesseract OCR are properly installed
   - Verify internet connection for Japanese pack auto-download
   - Check the log output in the installer for specific error messages

2. **Daemon Not Starting:**
   - Check `daemon_startup_error.txt` for error messages
   - Run `test_daemon_start.py` to diagnose startup issues
   - Verify Python dependencies are installed: `pip install mss pillow pytesseract opencv-python numpy psutil`

3. **Death Detection Not Working:**
   - Use `CAPTURE_DEBUG.bat` to capture a debug screenshot
   - Check `debug.log` for OCR results and detection attempts
   - Verify the game window is visible and not minimized
   - Ensure the capture region in `games_config.json` matches your resolution

4. **Windowed Mode Issues:**
   - The daemon automatically detects windowed mode and tracks window position
   - If detection fails, try moving the game window slightly to trigger position update
   - Check `debug.log` for window detection status messages

5. **Multi-Monitor Issues:**
   - The daemon automatically detects when a window spans multiple monitors
   - Use `CHANGE_MONITOR_ID.bat` if you need to manually specify a monitor
   - Check `debug.log` for monitor detection messages

## Building the Installer

To rebuild the installer from source:

1. Ensure all source files are in the `All Contents` folder
2. Run `Edit/build_single_file.py` to create `DeathCounter_Installer_Standalone.py`
3. Use PyInstaller to compile: `pyinstaller --onefile --windowed --name DeathCounterInstaller DeathCounter_Installer_Standalone.py`
4. The resulting `DeathCounterInstaller.exe` will be in the `dist` folder

## License

See repository for license information.
