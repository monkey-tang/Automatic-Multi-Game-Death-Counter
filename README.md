# Death Counter - Application Distribution Branch

## Branch Purpose
This branch contains the complete Death Counter application with all source files, documentation, and distribution materials.

## File and Folder Descriptions

### `1deathcounter/` (Folder)
**Description:** The main application directory containing all Death Counter source code, configuration files, documentation, and supporting scripts.

### `1deathcounter/1multi_game_death_counter.py`
**Description:** The core daemon script that monitors game screenshots and detects death counts. This runs in the background and tracks deaths across multiple Souls-like games.

### `1deathcounter/1death_counter_gui.py`
**Description:** The main GUI control interface for the Death Counter application. Provides a user-friendly interface to start/stop the daemon, view status, and control the death counter system.

### `1deathcounter/1README.md`
**Description:** Main application documentation with setup instructions, usage guide, and feature descriptions.

### `1deathcounter/1AUTO_SETUP_GUIDE.md`
**Description:** Step-by-step guide for automatic game detection and setup configuration.

### `1deathcounter/1BUILD_EXE.md`
**Description:** Instructions for building the standalone executable installer from source code.

### `1deathcounter/1DAEMON_CONTROLS.md`
**Description:** Documentation for controlling the death counter daemon, including start/stop commands and status monitoring.

### `1deathcounter/1HOW_TO_RUN_ACTIONS.md`
**Description:** Guide for running automated actions and integrations with the death counter system.

### `1deathcounter/1HOW_TO_TEST.md`
**Description:** Testing procedures and test scripts for verifying the death counter functionality.

### `1deathcounter/1HOW_TO_VERIFY_AUTO_DETECTION.md`
**Description:** Instructions for verifying and troubleshooting automatic game detection features.

### `1deathcounter/1MANUAL_SWITCH_GUIDE.md`
**Description:** Guide for manually switching between different games when automatic detection is not used.

### `1deathcounter/1STREAMERBOT_SETUP.md`
**Description:** Setup instructions for integrating the death counter with StreamerBot for streaming automation.

### `1deathcounter/1QUICK_START.txt` & `1deathcounter/1QUICK_AUTO_SETUP.txt`
**Description:** Quick reference guides for fast setup and getting started with the application.

### `1deathcounter/1START_DEATH_COUNTER.bat` & `1deathcounter/1STOP_DEATH_COUNTER.bat`
**Description:** Windows batch scripts for easily starting and stopping the death counter daemon.

### `1deathcounter/1StreamerBot_*.cs`
**Description:** C# scripts for StreamerBot integration:
- `1StreamerBot_GetDeathCount.cs` - Retrieves current death count
- `1StreamerBot_StartDeathCounter.cs` - Starts the death counter daemon
- `1StreamerBot_StopDeathCounter.cs` - Stops the death counter daemon
- `1StreamerBot_SwitchGame.cs` - Switches the active game being tracked
- `1StreamerBot_SwitchGameAndGetCount.cs` - Switches game and returns death count

### `1deathcounter/1Multi Game Death Detector.code-workspace`
**Description:** Visual Studio Code workspace configuration file for the project.

### `1deathcounter/1death_counter_*.txt` & `1deathcounter/1death_counter_*` (Files)
**Description:** Death count storage files for each game (Elden Ring, Dark Souls series, Sekiro, etc.). These files store the current death count for each game.

### `1deathcounter/1current_deaths.txt` & `1deathcounter/1current_game.txt`
**Description:** Current state files that track the active game and current death count.

### `1deathcounter/1daemon.lock`
**Description:** Lock file used to prevent multiple instances of the daemon from running simultaneously.

### `distribution/` (Folder)
**Description:** Contains the distribution-ready files for easy download. Includes the latest `.exe` installer and installation instructions.

### `distribution/DeathCounterInstaller.exe`
**Description:** The compiled Windows executable installer. This is a standalone installer that extracts and sets up the Death Counter application.

### `distribution/README.md`
**Description:** Installation and usage instructions for end users downloading the installer from the distribution folder.

### `.gitignore`
**Description:** Git configuration file that specifies which files and directories should be ignored by version control (e.g., build artifacts, temporary files, cache directories, lock files, state files).
