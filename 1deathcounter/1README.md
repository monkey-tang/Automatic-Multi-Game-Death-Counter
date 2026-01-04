# Multi-Game Death Counter

An automatic death counter that works across multiple Souls-like games (Elden Ring, Dark Souls, Sekiro, etc.)

## Quick Start

### 1. Install Dependencies

**Option A: Use the batch file (Recommended)**
```
Double-click: install_dependencies.bat
```

**Option B: Manual installation**
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

Download and install Tesseract OCR:
- **Download:** https://github.com/UB-Mannheim/tesseract/wiki
- **Default path:** `C:\Program Files\Tesseract-OCR\tesseract.exe`
- If installed elsewhere, edit `TESSERACT_EXE` in `multi_game_death_counter.py`

### 3. Run the Death Counter

**Option A: Use the batch file (Recommended)**
```
Double-click: START_DEATH_COUNTER.bat
```

**Option B: Command line**
```bash
python multi_game_death_counter.py
```

**To stop:** Double-click `STOP_DEATH_COUNTER.bat` or press Ctrl+C

## Files Overview

### Main Files
- **`multi_game_death_counter.py`** - Main daemon script (run this)
- **`switch_game.py`** - Utility to switch between games
- **`test_preprocessing.py`** - Test script to verify your setup
- **`requirements.txt`** - Python dependencies
- **`START_DEATH_COUNTER.bat`** - Easy launcher
- **`STOP_DEATH_COUNTER.bat`** - Easy stopper
- **`install_dependencies.bat`** - Dependency installer

### Streamer.bot Integration (Optional)
- **`StreamerBot_StartDeathCounter.cs`** - Start daemon from Streamer.bot
- **`StreamerBot_StopDeathCounter.cs`** - Stop daemon from Streamer.bot
- **`StreamerBot_GetDeathCount.cs`** - Get death count in Streamer.bot
- **`StreamerBot_SwitchGame.cs`** - Switch games from Streamer.bot

## Configuration

### First Run
On first run, the script creates:
- `C:\deathcounter\games_config.json` - Game configurations
- `C:\deathcounter\death_state.json` - Death counts and state
- `C:\deathcounter\death_counter.txt` - Text file for OBS (total deaths)
- `C:\deathcounter\debug.log` - Log file

### Editing Game Settings

Edit `C:\deathcounter\games_config.json` to configure:

```json
{
  "settings": {
    "tick_seconds": 0.30,
    "debug_every_ticks": 30,
    "consecutive_hits": 2,
    "cooldown_seconds": 8.0,
    "monitor_index": 2
  },
  "games": {
    "Elden Ring": {
      "region": {"left": 520, "top": 470, "width": 880, "height": 200},
      "keywords": ["YOUDIED", "YOUDIE", "DIED"],
      "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
      "monitor_index": 2
    }
  },
  "current_game": "Elden Ring"
}
```

### Finding the Right Region Coordinates

1. Take a screenshot when "YOU DIED" appears
2. Use an image editor (Paint, GIMP, etc.) to find coordinates
3. Update the `region` in the config:
   - `left`: X position of left edge
   - `top`: Y position of top edge  
   - `width`: Width of the region
   - `height`: Height of the region

### Switching Games

**Option A: Edit config file**
Change `"current_game"` in `games_config.json`

**Option B: Use switch script**
```bash
python switch_game.py "Elden Ring"
```

## OBS Integration

The death counter writes to text files that OBS can read:

- **Total deaths:** `C:\deathcounter\death_counter.txt`
- **Per-game deaths:** `C:\deathcounter\death_counter_GameName.txt`

### OBS Setup

1. In OBS, add a **Text (GDI+)** source
2. Check **"Read from file"**
3. Browse to: `C:\deathcounter\death_counter.txt`
4. Customize the font/style as desired

## Debugging

### Test Your Setup

Run the test script to verify everything works:
```bash
python test_preprocessing.py
```

This will:
- Capture the configured region
- Show preprocessing results
- Test OCR detection
- Save debug images to `C:\deathcounter\`

### Debug Images

The daemon saves debug images every 30 ticks (default):
- `debug_capture_raw.png` - Original screenshot
- `debug_capture.png` - Processed image (what OCR sees)

### Log File

Check `C:\deathcounter\debug.log` for detailed information:
- OCR results
- Detection status
- Death counts
- Errors

### Common Issues

**Black processed image (fixed!):**
- The new version uses adaptive threshold fallback
- Should always produce a visible image now
- If still black, check region coordinates

**Not detecting deaths:**
1. Check `debug_capture_raw.png` - is the region correct?
2. Check `debug_capture.png` - can you see text?
3. Verify monitor index is correct
4. Try adjusting keywords in config

**False positives:**
1. Increase `consecutive_hits` (requires more detections)
2. Increase `cooldown_seconds` (longer time between deaths)

**Tesseract errors:**
1. Verify Tesseract is installed
2. Check `TESSERACT_EXE` path in the script
3. Ensure Tesseract is in PATH

## Streamer.bot Integration

### Setup

1. Copy the `.cs` files to your Streamer.bot actions folder (or paste directly)
2. Create actions for each script:
   - **Start Death Counter** - Uses `StreamerBot_StartDeathCounter.cs`
   - **Stop Death Counter** - Uses `StreamerBot_StopDeathCounter.cs`
   - **Get Death Count** - Uses `StreamerBot_GetDeathCount.cs` (sets variables)
   - **Switch Game** - Uses `StreamerBot_SwitchGame.cs`

### Important: Update Paths

The script path in `StreamerBot_StartDeathCounter.cs` is already configured for `C:\deathcounter\`. 
If you moved the files to a different location, update the path:
```csharp
string scriptPath = @"C:\deathcounter\multi_game_death_counter.py";
```

### Variables Set by Get Death Count

- `DeathCountTotal` - Total deaths across all games
- `DeathCountGame` - Deaths for current game
- `DeathCounterCurrentGame` - Name of current game

## Troubleshooting

**Daemon won't start:**
- Check if another instance is running (look for `daemon.lock`)
- Delete `daemon.lock` if previous instance crashed
- Check `debug.log` for errors

**Deaths not counting:**
- Verify region captures "YOU DIED" text
- Check debug images
- Lower `consecutive_hits` if detection is inconsistent
- Verify keywords match OCR output

**High CPU usage:**
- Increase `tick_seconds` (slower checking = lower CPU)
- Reduce `debug_every_ticks` (less frequent image saving)

## Adding New Games

1. Add entry to `games` in `games_config.json`:
```json
"Your Game Name": {
  "region": {"left": X, "top": Y, "width": W, "height": H},
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "tesseract_config": "--oem 3 --psm 7",
  "monitor_index": 1
}
```

2. Switch to the new game using `switch_game.py` or edit config

## Support

Most issues can be resolved by:
1. Checking debug images (`debug_capture_raw.png` and `debug_capture.png`)
2. Reviewing `debug.log` for error messages
3. Verifying region coordinates and monitor index
4. Adjusting detection parameters in config

The new version fixes the "black image" issue by using robust preprocessing with adaptive threshold fallback.

