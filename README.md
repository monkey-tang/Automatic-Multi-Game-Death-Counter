# Death Counter Installer

## Latest Update
Fixed Start Daemon button with Python detection and script path fallback.

## File and Folder Descriptions

### `DeathCounterInstaller.exe`
**Description:** The full application/executable installer for the Death Counter system. This is a complete, standalone installer that handles the entire setup process with step-by-step guidance. 

**What it does:**
- **Extracts all necessary files** (daemon scripts, GUI, configuration files)
- **Checks system requirements** (Python, Tesseract OCR installation status)
- **Guides through installation steps** with clear buttons and status indicators
- **Installs Python dependencies** automatically (mss, pillow, opencv-python, numpy, psutil, pytesseract)
- **Integrates with Streamer.bot** by providing the action file for import
- **Launches the Death Counter GUI** when setup is complete

**Installation workflow:**
1. Run `DeathCounterInstaller.exe`
2. Click "Install/Update Files" to extract all application files
3. Click "Install Python" (if needed) - opens download page
4. Click "Install Tesseract" (if needed) - opens download page  
5. Click "Install Dependencies" to install required Python packages
6. Click "Streamer.bot Download" to get Streamer.bot
7. Click "Import to Streamer.bot" and import the action file
8. Click "Confirm Import" to enable the launch button
9. Click "Launch Death Counter" to start the application

This executable is the **only file needed** to set up the entire Death Counter system on any Windows machine - it's completely self-contained and includes everything required for installation and operation.

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
