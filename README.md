# Death Counter Installer

## Latest Update
Fixed Start Daemon button with Python detection and script path fallback.

## File and Folder Descriptions

### `DeathCounterInstaller.exe`
**Description:** The complete standalone Windows executable installer application. This is the full application file that sets up everything needed for the Multi-Game Death Counter with clear, step-by-step instructions and guided installation.

**Complete Setup Application Features:**
1. **Extracts/Updates Files**: Automatically places all necessary scripts and configuration files into `C:\1deathcounter`
2. **Checks System Requirements**: Verifies Python and Tesseract OCR installations
3. **Installs Python (Optional)**: Provides download button if Python is not found
4. **Installs Tesseract OCR (Optional)**: Provides download button if Tesseract is not found
5. **Installs Python Dependencies**: Automatically installs all required packages (mss, pillow, opencv-python, pytesseract, numpy, psutil) with verification
6. **Downloads Streamer.bot (Optional)**: Opens the Streamer.bot download page
7. **Imports Streamer.bot Action**: Guides you to import the `deathcounteraction.cs` file into Streamer.bot
8. **Confirms Import**: Enables the "Launch" button after Streamer.bot import is confirmed
9. **Launches Death Counter GUI**: Starts the main graphical interface for the Death Counter application

**Step-by-Step Installation Workflow:**
1. Run `DeathCounterInstaller.exe` (double-click to launch)
2. Click **"Install/Update Files"** → Extracts all application files
3. Click **"Install Python"** (if needed) → Opens Python download page
4. Click **"Install Tesseract"** (if needed) → Opens Tesseract download page  
5. Click **"Install Dependencies"** → Installs all required Python packages
6. Click **"Streamer.bot Download"** → Opens Streamer.bot download page
7. Click **"Import to Streamer.bot"** → Opens Streamer.bot import dialog
8. Click **"✓ Confirm Import"** → Enables the launch button
9. Click **"Launch Death Counter"** → Starts the Death Counter GUI application

This single executable file contains everything needed to set up and run the entire Death Counter system on any Windows machine. No additional downloads or manual configuration required - it's a complete, self-contained setup application with step-by-step guidance.

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
