# Daemon Control Scripts

## Overview

You have two scripts to control the death counter daemon:

1. **`restart_daemon.py`** - Restarts the daemon while preserving all death counts
2. **`reset_daemon.py`** - Resets all death counts to 0 and restarts the daemon

## Progress Persistence

**YES, the daemon saves progress automatically!**

The daemon saves its state to `death_state.json`:
- **Every 10 ticks** (about every 3 seconds) - periodic saves
- **Immediately after each death** is detected
- **On shutdown** (when stopped cleanly)

This means:
- ✅ Death counts are preserved across restarts
- ✅ Per-game counts are preserved
- ✅ You can safely restart without losing progress
- ✅ Only use `reset_daemon.py` when you want to start fresh

## Usage

### Restart Daemon (Preserves Counts)

```powershell
cd C:\deathcounter
python restart_daemon.py
```

**What it does:**
1. Stops the running daemon
2. Starts it again with the same code
3. **Preserves all death counts**
4. Auto-detects which game is running

**Use when:**
- You updated the code and need to reload it
- The daemon seems stuck or not responding
- You want to refresh the daemon without losing progress

### Reset Daemon (Resets to 0)

```powershell
cd C:\deathcounter
python reset_daemon.py
```

**What it does:**
1. Stops the running daemon
2. Resets all death counts to 0 in the state file
3. Resets the main text file to "0"
4. Deletes all per-game text files
5. Restarts the daemon

**Use when:**
- Starting a new playthrough
- Testing the counter from scratch
- You want to start fresh

**⚠️ WARNING:** This will permanently delete all death counts!

## State File Location

The daemon saves its state to:
- `C:\deathcounter\death_state.json`

This file contains:
- `total_deaths` - Total across all games
- `game_deaths` - Per-game death counts
- `current_game` - Currently detected game
- `tick` - Internal counter
- `streak` - Current detection streak
- `last_death_ts` - Timestamp of last death

## Text Files

The daemon also writes text files for OBS:
- `C:\deathcounter\death_counter.txt` - Total deaths (just the number)
- `C:\deathcounter\death_counter_[GameName].txt` - Per-game deaths

These are updated:
- Immediately after each death
- On daemon startup
- When the game switches

## Manual Control

You can also control the daemon manually:

**Stop:**
```powershell
# Create STOP file
New-Item -ItemType File -Path "C:\deathcounter\STOP" -Force

# Or kill the process (check PID in daemon.lock first)
taskkill /F /PID [PID_NUMBER]
```

**Start:**
```powershell
cd C:\deathcounter
python multi_game_death_counter.py
```

## Troubleshooting

**Daemon won't stop:**
- The scripts will try to kill the process automatically
- If that fails, manually kill it: `taskkill /F /PID [PID]`

**State not saving:**
- Check file permissions on `C:\deathcounter\`
- Check `debug.log` for errors
- Make sure the daemon has write access

**Counts lost after restart:**
- This shouldn't happen - the daemon saves every 10 ticks
- Check if `death_state.json` exists and has the correct format
- Check `debug.log` for save errors

## Quick Reference

| Action | Command | Preserves Counts? |
|--------|---------|-------------------|
| Restart | `python restart_daemon.py` | ✅ Yes |
| Reset | `python reset_daemon.py` | ❌ No (resets to 0) |
| Check Status | `python test_death_counter.py` | N/A |
| Monitor | `python test_death_counter.py monitor` | N/A |

