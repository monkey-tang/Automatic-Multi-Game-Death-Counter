# Streamer.bot Integration Guide

This guide explains how to set up the death counter with Streamer.bot.

## Overview

You have 4 C# scripts for Streamer.bot:
1. **StreamerBot_StartDeathCounter.cs** - Start the death counter daemon
2. **StreamerBot_StopDeathCounter.cs** - Stop the death counter daemon
3. **StreamerBot_GetDeathCount.cs** - Get current death counts (sets variables)
4. **StreamerBot_SwitchGame.cs** - Switch between games

## Step-by-Step Setup

### Step 1: Create Actions in Streamer.bot

1. Open **Streamer.bot**
2. Go to the **Actions** tab (or press `Ctrl+A`)
3. Click the **+** button to create a new action
4. Name it (e.g., "Start Death Counter")
5. Click on the action to open it

### Step 2: Add C# Code to Actions

For each script, create a separate action:

#### Action 1: Start Death Counter

1. Create action: **"Start Death Counter"**
2. Click **Sub-Actions** tab
3. Click **+** to add a sub-action
4. Select **Execute C# Code**
5. Click the **Code** tab
6. Open `StreamerBot_StartDeathCounter.cs` in Notepad
7. **Copy ALL the code** (Ctrl+A, Ctrl+C)
8. **Paste it into the Code box** in Streamer.bot (Ctrl+V)
9. Click **Compile** to verify it compiles (should show "Success")
10. Click **Save**

#### Action 2: Stop Death Counter

1. Create action: **"Stop Death Counter"**
2. Add sub-action: **Execute C# Code**
3. Copy code from `StreamerBot_StopDeathCounter.cs`
4. Paste into the Code box
5. Compile and Save

#### Action 3: Get Death Count

1. Create action: **"Get Death Count"**
2. Add sub-action: **Execute C# Code**
3. Copy code from `StreamerBot_GetDeathCount.cs`
4. Paste into the Code box
5. Compile and Save

This action sets these variables you can use elsewhere:
- `DeathCountTotal` - Total deaths across all games
- `DeathCountGame` - Deaths for current game
- `DeathCounterCurrentGame` - Name of current game

#### Action 4: Switch Game (Optional)

1. Create action: **"Switch Death Counter Game"**
2. Add sub-action: **Execute C# Code**
3. Copy code from `StreamerBot_SwitchGame.cs`
4. Paste into the Code box
5. Compile and Save

**To use this action**, you need to set a variable or argument:
- Set a **Global Variable** named `GameName` with the game name (e.g., "Elden Ring")
- Or pass it as an argument when calling the action

## Step 3: Assign Hotkeys/Commands (Optional)

You can assign hotkeys or chat commands to these actions:

1. Right-click an action
2. Select **Hotkey** or **Command**
3. Set your key/command
4. Save

### Example Setup:

- **Hotkey F9** → Start Death Counter
- **Hotkey F10** → Stop Death Counter  
- **Hotkey F11** → Get Death Count (displays in chat or OBS)
- **Command !deaths** → Get Death Count (shows death count in chat)

## Step 4: Using Variables in OBS/Other Actions

After running "Get Death Count", you can use the variables:

### In Streamer.bot Actions:
- Use `%DeathCountTotal%` in chat messages
- Use `%DeathCountGame%` for current game deaths
- Use `%DeathCounterCurrentGame%` for game name

### In OBS:
The death counter **automatically writes to text files** that OBS can read:
- `C:\deathcounter\death_counter.txt` - Total deaths
- `C:\deathcounter\death_counter_[GameName].txt` - Per-game deaths

You don't need Streamer.bot variables for OBS - just use the text file source!

## Troubleshooting

### "Script not found" Error

If you get an error that the script isn't found:
1. Verify the path in `StreamerBot_StartDeathCounter.cs` line 14:
   ```csharp
   string scriptPath = @"C:\deathcounter\multi_game_death_counter.py";
   ```
2. Make sure the file exists at that path

### Compilation Errors

If the code won't compile:
1. Make sure you copied the **entire** code block
2. Make sure Streamer.bot has the required references (should be automatic)
3. Check for any syntax errors (missing brackets, etc.)

### Variables Not Updating

- Make sure you run "Get Death Count" action before using the variables
- Variables are **Global Variables** (not User Variables)
- The death counter daemon must be running for counts to update

### Daemon Won't Start

- Make sure Python is installed and in PATH
- Make sure the Python script exists at the path specified
- Check `C:\deathcounter\debug.log` for error messages

## Quick Reference

**Files to copy from:**
- `C:\deathcounter\StreamerBot_StartDeathCounter.cs`
- `C:\deathcounter\StreamerBot_StopDeathCounter.cs`
- `C:\deathcounter\StreamerBot_GetDeathCount.cs`
- `C:\deathcounter\StreamerBot_SwitchGame.cs`

**What to do:**
1. Open each .cs file in Notepad
2. Copy all the code
3. Paste into Streamer.bot Execute C# Code action
4. Compile and Save

**That's it!** The scripts are ready to use.





