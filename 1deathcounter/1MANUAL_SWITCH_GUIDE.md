# Manual Game Switch Guide

## Quick Command

To manually switch games, use:

```powershell
cd C:\deathcounter
python switch_game_manual.py "Game Name"
```

## Examples

```powershell
# Switch to Elden Ring
python switch_game_manual.py "Elden Ring"

# Switch to Dark Souls 3
python switch_game_manual.py "Dark Souls 3"

# Switch to Dark Souls Remastered
python switch_game_manual.py "Dark Souls Remastered"

# Switch to Sekiro
python switch_game_manual.py "Sekiro"
```

## What It Does

1. **Updates the config file** - Sets `current_game` in `games_config.json`
2. **Updates the state file** - Sets `current_game` in `death_state.json`
3. **Updates text files** - Writes the correct death count for that game:
   - `death_counter.txt` → Shows current game's count
   - `death_counter_[GameName].txt` → Shows per-game count

## Important Notes

- **The daemon keeps running** - You don't need to restart it
- **Auto-detection still works** - If the daemon detects a different game running, it will auto-switch
- **Text files update immediately** - OBS will see the new count right away
- **All settings preserved** - Uses the exact same setup (region, keywords, monitor, etc.)

## When to Use Manual Switch

Use manual switch when:
- You want to force a specific game (even if it's not running)
- Auto-detection isn't working (wrong process name)
- You want to test a specific game's configuration
- You're switching games manually and want the counter ready

## List Available Games

If you're not sure of the exact game name, the script will show available games if you use a wrong name:

```powershell
python switch_game_manual.py "Wrong Name"
```

It will show:
```
[ERROR] Game 'Wrong Name' not found in configuration.

Available games:
  - Elden Ring
  - Dark Souls 3
  - Dark Souls Remastered
  - Sekiro
```

## One-Line Examples

```powershell
# Quick switch commands
python switch_game_manual.py "Elden Ring"
python switch_game_manual.py "Dark Souls 3"
python switch_game_manual.py "Dark Souls Remastered"
python switch_game_manual.py "Sekiro"
```

## Integration with Streamer.bot

You can also use the existing `StreamerBot_SwitchGame.cs` script in Streamer.bot, which does the same thing but through Streamer.bot's interface.

