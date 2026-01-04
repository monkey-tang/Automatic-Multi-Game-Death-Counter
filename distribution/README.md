# Death Counter Installer

A standalone installer and launcher for the Multi-Game Death Counter application.

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

## Installation Steps

1. Run `DeathCounterInstaller.exe`
2. Click "Install/Update Files" to extract necessary files
3. If Python is missing, click "Install Python" (opens download page)
   - **Important**: Check "Add Python to PATH" during installation
4. If Tesseract OCR is missing, click "Install Tesseract" (opens download page)
5. Click "Install Dependencies" to install required Python packages
6. Click "Launch Death Counter" to start the application

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