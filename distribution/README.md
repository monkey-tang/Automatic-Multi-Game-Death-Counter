# Death Counter Installer

**Complete Standalone Setup Application** - The full Windows executable file that sets up everything needed for the Multi-Game Death Counter with clear, step-by-step instructions and guided installation.

This single `.exe` file is all you need - it contains everything required to set up and run the entire Death Counter system, including file extraction, dependency installation, Python setup, Tesseract OCR setup, Streamer.bot integration, and application launch.

## Quick Start

1. **Download** `DeathCounterInstaller.exe`
2. **Run** the installer
3. Follow the on-screen instructions to:
   - Install/Update files
   - Install Python (if needed)
   - Install Tesseract OCR (if needed)
   - Install dependencies
   - Launch the Death Counter

## Requirements

- **Windows 10/11**
- **Python 3.8+** (will be detected or you can install via the installer)
- **Tesseract OCR** (download link provided in installer)

## Features

- ✅ Automatic Python detection (checks PATH and common locations)
- ✅ One-click installation of dependencies
- ✅ Easy game switching
- ✅ Multi-game support (Elden Ring, Dark Souls, Sekiro, etc.)
- ✅ Automatic death detection via OCR
- ✅ StreamerBot integration ready

## Step-by-Step Installation Guide

1. **Run** `DeathCounterInstaller.exe` (double-click to launch)
2. **Click "Install/Update Files"** → Extracts all application files to `C:\1deathcounter`
3. **Click "Install Python"** (if needed) → Opens Python download page
   - **Important**: Check "Add Python to PATH" during installation
4. **Click "Install Tesseract"** (if needed) → Opens Tesseract OCR download page
5. **Click "Install Dependencies"** → Installs all required Python packages (mss, pillow, opencv-python, pytesseract, numpy, psutil)
6. **Click "Streamer.bot Download"** (optional) → Opens Streamer.bot download page
7. **Click "Import to Streamer.bot"** (optional) → Opens Streamer.bot import dialog for action file
8. **Click "✓ Confirm Import"** (if using Streamer.bot) → Enables the launch button
9. **Click "Launch Death Counter"** → Starts the Death Counter GUI application

The installer guides you through each step with clear buttons and status indicators. No manual configuration or additional downloads required - everything is handled automatically.

## Troubleshooting

### "Python not found in PATH"
- Make sure Python is installed and added to PATH
- Or install Python using the "Install Python" button in the installer
- Restart the installer after installing Python

### "Tesseract OCR not found"
- Install Tesseract OCR using the "Install Tesseract" button
- Default install path: `C:\Program Files\Tesseract-OCR\`
- Restart the installer after installation

### Application won't launch
- Ensure all dependencies are installed
- Check that Python is accessible
- Verify files were extracted successfully

## Support

For issues, questions, or contributions, please visit:
https://github.com/monkey-tang/deathcounter

## License

See the main repository for license information.



## Latest Update
Fixed Start Daemon button with Python detection and script path fallback.