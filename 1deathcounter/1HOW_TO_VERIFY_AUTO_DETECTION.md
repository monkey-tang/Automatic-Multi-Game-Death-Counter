# How to Verify Auto-Detection is Working

## Quick Test

Run this to see if any games are currently detected:

```powershell
cd C:\deathcounter
python test_auto_detection.py
```

This will show:
- Which games are configured
- Which games are currently running (detected)
- What process names are being checked

## How to Verify Auto-Detection is Working

### Method 1: Check Current Status

```powershell
python test_death_counter.py
```

Look for:
- **Current Game**: Should show the detected game name (not "Unknown")
- If it shows "Unknown", either:
  - No game is running
  - The game process name doesn't match the config

### Method 2: Monitor in Real-Time

```powershell
python test_death_counter.py monitor
```

Watch for:
- **Game changes**: When you launch/close games, the "Current Game" should update
- **Log entries**: Look for messages about game detection

### Method 3: Check the Log File

```powershell
# View recent log entries
Get-Content C:\deathcounter\debug.log -Tail 50 | Select-String -Pattern "Auto-detected|Game changed|Switched to"
```

Look for messages like:
- `Auto-detected game: Elden Ring (process: eldenring.exe)`
- `🔄 Game changed detected: [Old Game] → [New Game]`
- `Switched to: [Game Name]`

### Method 4: Test It Manually

1. **Start the daemon** (if not running):
   ```powershell
   python restart_daemon.py
   ```

2. **Check initial state**:
   ```powershell
   python test_death_counter.py
   ```
   Note the "Current Game"

3. **Launch a game** (e.g., Elden Ring)

4. **Wait ~9 seconds** (auto-detection checks every 30 ticks = ~9 seconds)

5. **Check status again**:
   ```powershell
   python test_death_counter.py
   ```
   The "Current Game" should now show the game you launched

6. **Close the game, launch a different one** (e.g., Dark Souls 3)

7. **Wait ~9 seconds**

8. **Check status** - should show the new game

## What to Look For

### ✅ Signs Auto-Detection is Working:

1. **Status shows game name** (not "Unknown")
   ```
   Current Game: Elden Ring
   ```

2. **Log shows detection messages**:
   ```
   Auto-detected game: Elden Ring (process: eldenring.exe)
   ```

3. **Game switches automatically** when you change games

4. **Config file updates** - `current_game` in `games_config.json` changes

### ❌ Signs It's NOT Working:

1. **Always shows "Unknown"** - No games detected
2. **Doesn't switch** when you change games
3. **Wrong game detected** - Process name mismatch

## Troubleshooting

### Game Not Detected

1. **Check process name**:
   ```powershell
   # See what processes are running
   python test_auto_detection.py
   ```

2. **Find the actual process name**:
   - Open Task Manager
   - Find your game process
   - Note the exact .exe name (case-sensitive)

3. **Update config**:
   - Edit `games_config.json`
   - Add the correct process name to `process_names` array
   - Restart daemon: `python restart_daemon.py`

### Example: Finding Process Name

If Elden Ring isn't detected:

1. Launch Elden Ring
2. Open Task Manager (Ctrl+Shift+Esc)
3. Find "eldenring.exe" or similar
4. Note the exact name (might be "ELDEN RING.exe" or "elden_ring.exe")
5. Add it to the config:
   ```json
   "process_names": [
     "eldenring.exe",
     "elden ring.exe",
     "ELDEN RING.exe"  // Add the actual name you found
   ]
   ```

### Auto-Detection Timing

- Checks every **30 ticks** = ~9 seconds (at 0.3s per tick)
- So there's a delay of up to 9 seconds when switching games
- This is normal - be patient!

## Quick Commands Reference

```powershell
# Test what's currently detected
python test_auto_detection.py

# Check daemon status
python test_death_counter.py

# Monitor for changes
python test_death_counter.py monitor

# View detection in log
Get-Content debug.log -Tail 50 | Select-String "Auto-detected|Game changed"
```

