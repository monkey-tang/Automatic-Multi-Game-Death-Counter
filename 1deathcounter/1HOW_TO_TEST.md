# How to Test the Death Counter

This guide shows you how to verify the death counter is working and updating text files.

## Quick Status Check

Run this to see the current status:

```bash
python test_death_counter.py
```

This will show:
- ✅ Whether the daemon is running
- 📄 Current values in text files
- 📊 Current state from JSON files
- ⚙️ Current configuration
- 📝 Recent log entries

## Real-Time Monitoring

To watch for changes in real-time (updates every 2 seconds):

```bash
python test_death_counter.py monitor
```

Or monitor for a specific duration (e.g., 120 seconds):

```bash
python test_death_counter.py monitor 120
```

This will:
- Show current death counts
- Highlight when changes are detected
- Display recent log entries
- Show if the game switches automatically

## Step-by-Step Testing

### 1. Start the Death Counter

First, make sure the daemon is running. You can start it via:
- Streamer.bot action: "Start Death Counter"
- Or manually: `python multi_game_death_counter.py`

### 2. Check Initial Status

```bash
python test_death_counter.py
```

You should see:
- ✅ Daemon is RUNNING
- Current death counts (should be 0 if first run)
- Current game detected

### 3. Monitor While Testing

Open a second terminal/command prompt and run:

```bash
python test_death_counter.py monitor
```

Keep this running while you test.

### 4. Test Detection

1. **Start your game** (Elden Ring, Dark Souls, etc.)
2. **Trigger a death** in the game
3. **Watch the monitor** - you should see:
   - The death count increment
   - A log entry showing "💀 DEATH COUNTED"
   - The text files update

### 5. Check Text Files Directly

You can also check the text files directly:

**Total deaths:**
```bash
type C:\deathcounter\death_counter.txt
```

**Per-game deaths (example for Elden Ring):**
```bash
type C:\deathcounter\death_counter_Elden_Ring.txt
```

### 6. Check Debug Images

The daemon saves debug images every 30 ticks:
- `C:\deathcounter\debug_capture_raw.png` - Original captured region
- `C:\deathcounter\debug_capture.png` - Processed image for OCR

Check these to verify the region is being captured correctly.

### 7. Check Log File

View the full log:

```bash
type C:\deathcounter\debug.log
```

Or view the last 20 lines:

```bash
powershell "Get-Content C:\deathcounter\debug.log -Tail 20"
```

## What to Look For

### ✅ Signs It's Working:

1. **Daemon is running** - Lock file exists
2. **Text files update** - Numbers increment when deaths occur
3. **Log shows detections** - You see "💀 DEATH COUNTED" messages
4. **Game auto-detection** - Game switches automatically when you launch a different game
5. **Debug images** - Images show the correct region of the screen

### ❌ Common Issues:

1. **Daemon not running**
   - Solution: Start it via Streamer.bot or manually

2. **No detections**
   - Check if the game process name matches the config
   - Verify the region coordinates are correct
   - Check debug images to see what's being captured

3. **Text files not updating**
   - Check if daemon has write permissions
   - Verify the BASE_DIR path is correct

4. **Wrong game detected**
   - Check process names in `games_config.json`
   - Verify the game executable name matches

## Testing Auto-Detection

To test auto-detection:

1. Start the daemon
2. Launch Game A (e.g., Elden Ring)
3. Check status - should show Game A
4. Close Game A, launch Game B (e.g., Dark Souls 3)
5. Wait ~9 seconds (auto-detection checks every 30 ticks)
6. Check status - should now show Game B

## Quick Test Commands

```bash
# Check status once
python test_death_counter.py

# Monitor for 60 seconds
python test_death_counter.py monitor 60

# View last 10 log lines
powershell "Get-Content C:\deathcounter\debug.log -Tail 10"

# Check if daemon is running
if exist C:\deathcounter\daemon.lock (echo Running) else (echo Not running)

# View current death count
type C:\deathcounter\death_counter.txt
```

## Tips

- Keep the monitor running in a separate window while testing
- Check debug images if detections aren't working
- The log file has detailed information about each tick
- Auto-detection happens every ~9 seconds, so be patient when switching games

