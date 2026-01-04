# Death Counter Installer

## Latest Update
Fixed Start Daemon button with Python detection and script path fallback.

## File and Folder Descriptions

### `DeathCounterInstaller.exe`
**Description:** The main Windows executable installer. This is a standalone installer that extracts and sets up the Death Counter application on your system. Simply run this file to install the application.

### `DeathCounter_Installer_Standalone.py`
**Description:** The Python source code for the standalone installer. This script contains all necessary files embedded as base64-encoded strings and creates a self-extracting installer. Used to build the `.exe` file.

### `1death_counter_gui.py`
**Description:** The main GUI control interface for the Death Counter application. This provides a user-friendly interface to start/stop the daemon, view status, and control the death counter system.

### `distribution/` (Folder)
**Description:** Contains the distribution-ready files for easy download. Includes the latest `.exe` installer and installation instructions.

### `distribution/DeathCounterInstaller.exe`
**Description:** Copy of the latest installer executable, placed in the distribution folder for convenient access.

### `distribution/README.md`
**Description:** Installation and usage instructions for end users downloading the installer from the distribution folder.

### `.gitignore`
**Description:** Git configuration file that specifies which files and directories should be ignored by version control (e.g., build artifacts, temporary files, cache directories).
