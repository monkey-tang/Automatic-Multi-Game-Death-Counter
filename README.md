# Death Counter v2 - Automatic Multi-Game Death Tracker

A fully automatic, reliable death counter for Dark Souls, Elden Ring, Sekiro, and other games. Supports **three detection methods**: OCR (Optical Character Recognition), Log File Monitoring, and Process Memory Scanning.

## 🎮 Supported Games

- **Elden Ring**
- **Dark Souls 3**
- **Dark Souls Remastered**
- **Dark Souls II: Scholar of the First Sin**
- **Sekiro: Shadows Die Twice**

*More games can be added by configuring them in `games_config.json`*

## ✨ Features

### 🔍 Multi-Method Detection
- **OCR Detection** - Reads on-screen "YOU DIED" text using Tesseract OCR
- **Log File Monitoring** - Watches game log files for death-related entries
- **Process Memory Scanning** - Scans game process memory for death indicators

### 🎯 Smart Detection
- **Automatic Game Detection** - Automatically detects which game is running
- **Streak-Based Confirmation** - Requires multiple consecutive detections to confirm death (reduces false positives)
- **Cooldown Mechanism** - Prevents counting the same death multiple times
- **Fuzzy OCR Matching** - Handles OCR misreadings (e.g., "Y0UD13D" instead of "YOUDIED")

### 🖥️ User Interface
- **GUI Application** - Easy-to-use Tkinter interface
- **Settings GUI** - Configure all settings with buttons and checkboxes
- **Real-time Status** - See current game, death counts, and daemon status
- **Desktop Shortcut** - Quick access to the GUI

### 📊 Statistics & Output
- **Per-Game Death Counts** - Track deaths for each game separately
- **Total Death Count** - Overall death count across all games
- **Text Files** - Death counts written to text files for OBS/Streamer.bot integration
- **Current Game Display** - Shows which game is currently being tracked

### ⚙️ Advanced Features
- **Multi-Monitor Support** - Works with multiple monitors
- **Window Detection** - Adapts to fullscreen, borderless, and windowed modes
- **Configurable Regions** - Customize OCR capture regions for each game
- **Debug Tools** - Capture debug images, change monitor settings, reset counts

## 🚀 Quick Start

### Option 1: Using the Installer (Recommended)

1. **Run `DeathCounterInstaller.exe`**
2. **Choose installation directory** (default: Desktop\DeathCounter)
3. **Select options:**
   - ✅ Create desktop shortcut
   - ✅ Install Python dependencies automatically
   - ✅ Check for Tesseract OCR
4. **Click "Install"**
5. **Wait for installation to complete**
6. **Double-click the desktop shortcut** or run `START_DEATH_COUNTER.bat`

### Option 2: Manual Installation

1. **Install Python 3.8-3.12** from [python.org](https://www.python.org/)
2. **Install Tesseract OCR** from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the GUI:**
   ```bash
   python death_counter_gui.py
   ```
5. **Start the daemon** from the GUI or run:
   ```bash
   python multi_game_death_counter.py
   ```

## 📖 Detailed Usage

### Starting the Application

#### Using the GUI (Recommended)
1. **Launch the GUI:**
   - Double-click the desktop shortcut, OR
   - Run `python death_counter_gui.py`, OR
   - Run `START_DEATH_COUNTER.bat` (also starts daemon)

2. **Click "Start Daemon"** - The daemon will begin monitoring for deaths

3. **Launch your game** - The daemon will automatically detect which game is running

4. **Play and die** - Deaths are automatically counted!

#### Using Command Line
```bash
# Start daemon directly
python multi_game_death_counter.py

# Start GUI
python death_counter_gui.py
```

### GUI Features

#### Main Window
- **Game Selection** - Click to cycle through games or select from dropdown
- **Death Count Display** - Shows current game deaths and total deaths
- **Daemon Status** - Green/Red indicator for daemon running status
- **Start/Stop Buttons** - Control the daemon
- **Settings Button** - Open settings configuration window

#### Settings Window
- **Detection Methods** - Toggle OCR, Log Monitoring, Memory Scanning
- **OCR Settings** - Fuzzy matching toggle
- **Performance Settings** - Tick rate, consecutive hits, cooldown, monitor index
- **Game Selection** - Set default game
- **Status Indicators** - See which methods are active
- **Save/Reset** - Apply changes or reset to defaults
- **Restart Warning** - Notifies when daemon restart is needed

### Configuration

#### games_config.json Structure

```json
{
  "settings": {
    "tick_seconds": 0.3,
    "debug_every_ticks": 30,
    "consecutive_hits": 2,
    "cooldown_seconds": 5.0,
    "monitor_index": 1,
    "detection_methods": {
      "ocr": true,
      "log_monitoring": false,
      "memory_scanning": false
    },
    "fuzzy_ocr_matching": true
  },
  "games": {
    "Elden Ring": {
      "region": { "left": 520, "top": 470, "width": 880, "height": 200 },
      "keywords": ["YOUDIED", "YOUDIE", "Y0UDIED", "YOUD13D"],
      "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
      "monitor_index": 2,
      "process_names": ["eldenring.exe"],
      "log_files": [],
      "log_patterns": [],
      "memory_patterns": []
    }
  },
  "current_game": "Elden Ring"
}
```

#### Key Settings Explained

- **tick_seconds**: How often to check for deaths (default: 0.3 seconds)
- **consecutive_hits**: Number of consecutive detections required (default: 2)
- **cooldown_seconds**: Time before another death can be counted (default: 5.0 seconds)
- **monitor_index**: Which monitor to capture (1 = primary, 2 = secondary, etc.)
- **fuzzy_ocr_matching**: Enable fuzzy matching for OCR misreadings (default: true)

#### Per-Game Settings

- **region**: Screen region to capture for OCR (left, top, width, height in pixels)
- **keywords**: Death-related keywords to search for
- **tesseract_config**: Tesseract OCR configuration string
- **process_names**: Executable names to detect game (e.g., ["eldenring.exe"])
- **log_files**: List of log file paths to monitor (for log monitoring method)
- **log_patterns**: Regex patterns to match in log files
- **memory_patterns**: Byte patterns to search in memory (for memory scanning)

## 🔍 Detection Methods

### Method 1: OCR (Optical Character Recognition)

**How it works:**
1. Captures a specific screen region (where "YOU DIED" appears)
2. Preprocesses the image (HSV filtering, thresholding, upscaling)
3. Runs OCR using Tesseract to extract text
4. Checks for death-related keywords
5. Confirms with streak-based detection

**Pros:**
- Works with any game that displays "YOU DIED" text
- No game-specific memory addresses needed
- Non-invasive (doesn't modify game files or memory)

**Cons:**
- Requires clear text on screen
- Slower than other methods
- May have false positives/negatives

**Configuration:**
- Adjust `region` to capture the right screen area
- Add keyword variations (including OCR misreadings like "Y0UD13D")
- Enable fuzzy matching for better OCR handling

### Method 2: Log File Monitoring

**How it works:**
1. Monitors specified log files for new entries
2. Matches log lines against regex patterns
3. Triggers death detection when pattern matches

**Pros:**
- Very reliable (if game logs deaths)
- Fast (file system events)
- No screen capture needed

**Cons:**
- Requires game to log deaths
- Needs log file paths and patterns configured
- May not work with all games

**Configuration:**
Add to game config:
```json
"log_files": ["C:\\Game\\logs\\game.log"],
"log_patterns": ["YOU DIED", "died", "death"]
```

### Method 3: Process Memory Scanning

**How it works:**
1. Attaches to game process
2. Scans process memory for known patterns/values
3. Detects when death-related memory values change

**Pros:**
- Very fast
- Very reliable (direct memory access)
- No screen capture needed

**Cons:**
- Requires game-specific memory addresses/patterns
- May trigger antivirus warnings
- Needs reverse engineering for each game
- Windows-only

**Configuration:**
Add to game config:
```json
"memory_patterns": ["48 65 6C 6C 6F"],  // Hex patterns
"memory_addresses": ["0x12345678"]       // Specific addresses (if known)
```

## 🎛️ Fuzzy OCR Matching

Fuzzy matching handles common OCR misreadings where letters look like numbers:
- O ↔ 0 (zero)
- I ↔ 1 (one)
- E ↔ 3 (three)
- A ↔ 4 (four)
- S ↔ 5 (five)
- G ↔ 6 (six)
- T ↔ 7 (seven)
- B ↔ 8 (eight)
- Z ↔ 2 (two)

**Example:** OCR reads "Y0UD13D" → Fuzzy matching detects it as "YOUDIED"

**Toggle fuzzy matching:**
1. Open Settings GUI (click "Settings" button)
2. Toggle "Fuzzy OCR Matching" checkbox
3. Click "Save"
4. Restart daemon for changes to take effect

Or edit `games_config.json`:
```json
"fuzzy_ocr_matching": false  // Set to false to disable
```

See `FUZZY_MATCHING_GUIDE.md` for more details.

## 📁 Output Files

The daemon creates several text files for integration with OBS, Streamer.bot, etc.:

- **`death_counter.txt`** - Current game death count
- **`death_counter_<GameName>.txt`** - Per-game death counts (e.g., `death_counter_Elden_Ring.txt`)
- **`total_deaths.txt`** - Total deaths across all games
- **`current_game.txt`** - Name of currently detected game
- **`current_deaths.txt`** - Death count for current game

**Example usage in OBS:**
1. Add Text (GDI+) source
2. Check "Read from file"
3. Browse to `death_counter.txt`
4. Style as desired

## 🛠️ Utility Scripts

### Batch Files (Created by Installer)

- **`START_DEATH_COUNTER.bat`** - Start the daemon
- **`STOP_DEATH_COUNTER.bat`** - Stop the daemon
- **`RESET_DEATH_COUNTER.bat`** - Reset all death counts to zero
- **`CAPTURE_DEBUG.bat`** - Capture debug images for OCR testing
- **`CHANGE_MONITOR_ID.bat`** - Change monitor index for capture

### Python Scripts

- **`reset_death_counter.py`** - Reset death counts
- **`switch_game_manual.py`** - Manually switch active game
- **`capture_debug_once.py`** - One-time debug image capture
- **`change_monitor_id.py`** - Interactive monitor selection

## ⚙️ Troubleshooting

### Daemon Won't Start

**Check:**
1. Python is installed and in PATH: `python --version`
2. Tesseract OCR is installed: Check `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Dependencies installed: `pip install -r requirements.txt`
4. Check `debug.log` for error messages
5. Check `daemon_startup_error.txt` if GUI shows startup errors

### No Deaths Detected

**Solutions:**
1. **OCR Method:**
   - Adjust capture region in `games_config.json`
   - Add more keyword variations (including OCR misreadings)
   - Enable fuzzy matching
   - Check `debug_capture.png` to see what's being captured
   - Increase `consecutive_hits` if getting false positives

2. **Log Monitoring:**
   - Verify log file paths are correct
   - Check log file permissions (readable)
   - Verify regex patterns match log format
   - Check if game actually logs deaths

3. **Memory Scanning:**
   - Verify game process name is correct
   - Check if memory patterns are correct
   - Ensure you have permissions to read process memory
   - May need to run as administrator

### Wrong Game Detected

**Solutions:**
1. Check `process_names` in `games_config.json` match actual executable name
2. Use Task Manager to see exact process name
3. Multiple games running? Close the ones you don't want tracked

### False Positives (Counting Non-Deaths)

**Solutions:**
1. Increase `consecutive_hits` (requires more confirmations)
2. Increase `cooldown_seconds` (prevents rapid re-counting)
3. Adjust OCR region to exclude UI elements
4. Refine keyword list (remove ambiguous words)

### GUI Won't Open

**Solutions:**
1. Check if daemon is already running: `tasklist | findstr python`
2. Check `gui_debug.log` for errors
3. Verify tkinter is installed: `python -m tkinter`
4. Try running as administrator

### Performance Issues

**Solutions:**
1. Increase `tick_seconds` (check less frequently)
2. Disable unused detection methods
3. Disable fuzzy matching if OCR is reliable
4. Use log monitoring or memory scanning instead of OCR (faster)

## 📋 Requirements

### System Requirements
- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.8, 3.9, 3.10, 3.11, or 3.12
- **RAM:** 2GB minimum (4GB recommended)
- **Display:** Any resolution (multi-monitor supported)

### Required Software
- **Python 3.8-3.12** - [Download](https://www.python.org/downloads/)
- **Tesseract OCR** - [Download](https://github.com/UB-Mannheim/tesseract/wiki)
  - Install to default path: `C:\Program Files\Tesseract-OCR\`
  - Or add to PATH

### Python Dependencies
Install with: `pip install -r requirements.txt`

- `pytesseract` - OCR engine wrapper
- `mss` - Fast screen capture
- `opencv-python` - Image processing
- `Pillow` - Image manipulation
- `psutil` - Process management
- `watchdog` - File system monitoring (optional, for log monitoring)

## 🗂️ Project Structure

```
DEATHCOUNTER v2/
├── multi_game_death_counter.py    # Main daemon script
├── death_counter_gui.py            # GUI application
├── death_counter_settings.py       # Settings GUI
├── log_monitor.py                  # Log file monitoring module
├── memory_scanner.py               # Memory scanning module
├── games_config.json               # Configuration file
├── requirements.txt                # Python dependencies
├── reset_death_counter.py          # Reset utility
├── switch_game_manual.py           # Game switcher utility
├── capture_debug_once.py           # Debug image capture
├── change_monitor_id.py            # Monitor selector
├── installer.py                    # Installer application
├── BUILD_INSTALLER.bat             # Build installer script
├── README.md                       # This file
├── FUZZY_MATCHING_GUIDE.md         # Fuzzy matching guide
└── INSTALLER_README.md             # Installer documentation
```

## 🔧 Advanced Configuration

### Adding a New Game

1. **Add game configuration to `games_config.json`:**

```json
"My Game": {
  "region": { "left": 0, "top": 0, "width": 1920, "height": 1080 },
  "keywords": ["YOUDIED", "DIED", "DEATH"],
  "tesseract_config": "--oem 3 --psm 7",
  "monitor_index": 1,
  "process_names": ["mygame.exe"],
  "log_files": [],
  "log_patterns": [],
  "memory_patterns": []
}
```

2. **Find the capture region:**
   - Run `capture_debug_once.py` while game shows "YOU DIED"
   - Check `debug_capture.png` to see captured region
   - Adjust `region` coordinates in config

3. **Test and refine:**
   - Start daemon and play the game
   - Check `debug.log` for OCR output
   - Adjust keywords and region as needed

### Customizing OCR Settings

**Tesseract Config Options:**
- `--oem 3` - Use default OCR engine mode
- `--psm 7` - Treat image as single text line
- `-c tessedit_char_whitelist=...` - Limit characters to specific set

**Example:**
```json
"tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT0123456789"
```

### Multi-Monitor Setup

1. **Identify monitor indices:**
   - Run `change_monitor_id.py` to see available monitors
   - Note the index number for your game's monitor

2. **Set monitor index:**
   - In Settings GUI: Change "Monitor Index"
   - Or in `games_config.json`: Set `"monitor_index": 2` (for second monitor)

3. **Per-game monitors:**
   - Each game can have its own `monitor_index` setting

## 🐛 Debugging

### Debug Files

- **`debug.log`** - Main daemon log with detailed information
- **`gui_debug.log`** - GUI application debug log
- **`debug_capture.png`** - Latest captured image (for OCR testing)
- **`debug_capture_raw.png`** - Raw captured image (before processing)
- **`daemon_startup_error.txt`** - Daemon startup errors

### Debug Mode

The daemon logs information every N ticks (configured by `debug_every_ticks`):
- Current game
- OCR text detected
- Detection status
- Memory/Log scan results

### Capture Debug Images

Run `CAPTURE_DEBUG.bat` or:
```bash
python capture_debug_once.py
```

This captures the current screen region and saves:
- `debug_capture_raw.png` - Raw capture
- `debug_capture.png` - Processed image (what OCR sees)

Use these to:
- Verify capture region is correct
- See what OCR is reading
- Adjust keywords based on OCR output

## 📝 Changelog

### Version 2.0
- ✅ Added Log File Monitoring method
- ✅ Added Process Memory Scanning method
- ✅ Added Settings GUI for easy configuration
- ✅ Added Fuzzy OCR Matching
- ✅ Improved error handling and logging
- ✅ Added comprehensive installer
- ✅ Multi-monitor support improvements
- ✅ Better game detection logic

### Version 1.5
- ✅ OCR-based death detection
- ✅ Multi-game support
- ✅ GUI application
- ✅ Automatic game detection
- ✅ Text file output for OBS integration

## 📄 License

This project is provided as-is for personal use.

## 🤝 Contributing

To add support for new games:
1. Test with the game to find appropriate settings
2. Add configuration to `games_config.json`
3. Submit configuration with game name and tested settings

## ⚠️ Disclaimer

This software:
- Does not modify game files or memory
- Does not provide unfair advantages in games
- Uses only read-only detection methods
- Is for personal tracking/streaming purposes only

Memory scanning method may trigger antivirus warnings. This is a false positive - the software only reads memory, never writes.

## 📞 Support

For issues or questions:
1. Check `debug.log` for error messages
2. Review troubleshooting section above
3. Check configuration in `games_config.json`
4. Verify all requirements are installed

## 🎯 Tips for Best Results

1. **Use appropriate detection method:**
   - OCR: Best for most games, most versatile
   - Log Monitoring: Best if game logs deaths reliably
   - Memory Scanning: Fastest, but requires game-specific setup

2. **Calibrate capture region:**
   - Use debug capture to verify region
   - Adjust region to only capture "YOU DIED" area
   - Avoid UI elements that might trigger false positives

3. **Fine-tune keywords:**
   - Include common OCR misreadings (Y0UD13D, etc.)
   - Enable fuzzy matching for better OCR handling
   - Test with actual game captures

4. **Optimize performance:**
   - Increase tick_seconds if performance is an issue
   - Disable unused detection methods
   - Use faster methods (log/memory) when possible

5. **Multi-game setup:**
   - Configure each game separately
   - Use game-specific monitor indices
   - Test each game individually

---

**Happy Dying! 💀**

*Remember: Deaths are just learning opportunities!*
