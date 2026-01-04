# Automatic Death Count & Game Switching Setup

This guide shows you how to set up automatic death count updates and game switching.

## Option 1: Automatic Death Count Updates (Recommended)

Set up a timer to automatically get death counts every X seconds:

### Step 1: Create Auto-Update Action

1. In Streamer.bot, create a new action: **"Auto Update Death Count"**
2. Add Sub-Action: **Execute C# Code**
3. Copy the code from `StreamerBot_GetDeathCount.cs`
4. Paste and compile

### Step 2: Add Timer Trigger

1. Select the "Auto Update Death Count" action
2. In the **Triggers** section (right panel), click the search bar
3. Search for and add: **"Timer"** trigger
4. Configure:
   - **Interval**: 5-10 seconds (recommended: 5 seconds)
   - **Enabled**: Yes
5. Save

**Result:** Death count variables update every 5 seconds automatically!

---

## Option 2: Switch Game and Get Count (Combined Action)

Use this when you want to switch games AND get the count in one action:

### Step 1: Create Combined Action

1. Create new action: **"Switch Game and Get Count"**
2. Add Sub-Action: **Execute C# Code**
3. Copy code from `StreamerBot_SwitchGameAndGetCount.cs`
4. Paste and compile

### Step 2: Set Up Game Switching

**Method A: Using Hotkeys with Variables**

1. Create separate hotkey actions for each game:
   - Action: "Switch to Elden Ring"
     - Add Sub-Action: **Set Global Variable**
       - Variable: `GameName`
       - Value: `Elden Ring`
     - Add Sub-Action: **Execute Action**
       - Action: "Switch Game and Get Count"

2. Assign hotkeys:
   - **Ctrl+1** → Switch to Elden Ring
   - **Ctrl+2** → Switch to Dark Souls 3
   - etc.

**Method B: Using Commands**

1. Create command actions for each game:
   - Command: `!eldenring`
     - Add Sub-Action: **Set Global Variable**: `GameName` = `Elden Ring`
     - Add Sub-Action: **Execute Action**: "Switch Game and Get Count"

---

## Option 3: Fully Automatic Setup (Timer + Manual Game Switch)

**Best setup for most users:**

1. **Auto-Update Death Count** (Timer every 5 seconds)
   - Uses: `StreamerBot_GetDeathCount.cs`
   - Trigger: Timer (5 seconds)

2. **Manual Game Switching** (Hotkeys)
   - Hotkey **Ctrl+1**: Set variable `GameName` = "Elden Ring" → Execute "Switch Game and Get Count"
   - Hotkey **Ctrl+2**: Set variable `GameName` = "Dark Souls 3" → Execute "Switch Game and Get Count"
   - etc.

**Result:**
- Death counts update automatically every 5 seconds
- Switch games with hotkeys
- Counts stay current for the active game

---

## Quick Setup Instructions

### Automatic Death Count (5-second updates):

1. Copy `StreamerBot_GetDeathCount.cs` code
2. Create action: "Auto Update Death Count"
3. Add Execute C# Code sub-action, paste code
4. Add Timer trigger: 5 seconds
5. Enable trigger

### Game Switching (Hotkeys):

For each game (e.g., Elden Ring):

1. Create action: "Switch to Elden Ring"
2. Add Sub-Action: **Set Global Variable**
   - Variable Name: `GameName`
   - Variable Value: `Elden Ring`
3. Add Sub-Action: **Execute Action**
   - Select: "Switch Game and Get Count"
4. Assign hotkey (e.g., Ctrl+1)

Repeat for each game with different hotkeys.

---

## Variables Available

After setup, these variables update automatically:
- `%DeathCountTotal%` - Total deaths across all games
- `%DeathCountGame%` - Deaths for current game
- `%DeathCounterCurrentGame%` - Name of current game

Use these in:
- Chat messages
- OBS text sources (via Streamer.bot integration)
- Other actions

---

## Notes

**Game Detection:** Currently, the system cannot automatically detect which game is running. You need to manually switch games using hotkeys/commands when you change games.

**OBS Integration:** The death counter also writes to text files automatically:
- `C:\deathcounter\death_counter.txt` - Total deaths
- `C:\deathcounter\death_counter_[GameName].txt` - Per-game deaths

You can use OBS Text (GDI+) source with "Read from file" - no Streamer.bot needed for OBS!

---

## Troubleshooting

**Variables not updating:**
- Make sure the Timer trigger is enabled
- Check that the death counter daemon is running
- Verify the action compiled successfully

**Game switch not working:**
- Make sure you set the `GameName` variable before calling "Switch Game and Get Count"
- Verify the game name matches exactly (case-sensitive) with names in config

**Death count is 0:**
- Make sure the death counter daemon is running
- Check that deaths have been counted (check `C:\deathcounter\death_state.json`)





