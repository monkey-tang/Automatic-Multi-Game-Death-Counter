# How to Run Streamer.bot Actions

Now that your actions are set up, here's how to run each one:

## Method 1: Right-Click Execute (Quick Test)

1. In the **Actions** list (left panel), find your action
2. **Right-click** on the action name
3. Select **"Execute Action"** from the context menu
4. The action will run immediately

**Good for:** Testing if actions work correctly

---

## Method 2: Assign Hotkeys (Recommended)

Assign keyboard shortcuts to quickly trigger actions:

1. **Right-click** on an action (e.g., "StreamerBot_StartDeathCounter.cs")
2. Select **"Hotkey"**
3. Press the key combination you want (e.g., `F9`, `Ctrl+F9`, `F10`, etc.)
4. Click **Save** or **OK**

### Suggested Hotkeys:
- **F9** → Start Death Counter
- **F10** → Stop Death Counter
- **F11** → Get Death Count
- **F12** → Switch Game (or skip if not needed often)

**Good for:** Quick access while streaming/gaming

---

## Method 3: Chat Commands (For Streaming)

Let viewers or yourself trigger actions via chat commands:

1. **Right-click** on an action (e.g., "StreamerBot_GetDeathCount.cs")
2. Select **"Command"**
3. Enter the command (e.g., `!deaths`, `!deathcount`, `!startcounter`)
4. Configure options (who can use it, cooldown, etc.)
5. Click **Save**

### Suggested Commands:
- **!startcounter** → Start Death Counter
- **!stopcounter** → Stop Death Counter
- **!deaths** → Get Death Count (shows in chat)
- **!switchgame** → Switch Game (requires GameName variable)

**Good for:** Interactive streams, letting chat control the counter

---

## Method 4: Create a Trigger (Automated)

Set up triggers that automatically run actions:

1. Select an action in the left panel
2. In the **Triggers** section (right panel), click the search bar or right-click
3. Add a trigger (e.g., "Action Executed", "Timer", "Stream Start", etc.)
4. Configure the trigger settings
5. Save

**Example:** Set "Start Death Counter" to trigger on "Stream Started"

**Good for:** Automatic startup/shutdown

---

## Method 5: Call from Other Actions

You can have one action call another:

1. Create or edit an action
2. Add a **Sub-Action**: "Execute Action"
3. Select which action to call (e.g., "Get Death Count")
4. This action will run when the parent action runs

**Good for:** Combining multiple actions together

---

## Recommended Setup for Death Counter

### Quick Setup (Hotkeys):
1. **F9** → Start Death Counter (when you start gaming)
2. **F10** → Stop Death Counter (when done)
3. **F11** → Get Death Count (check current count)

### Stream Setup (Commands):
1. **!startcounter** → Start Death Counter
2. **!stopcounter** → Stop Death Counter  
3. **!deaths** → Show death count in chat
   - Add a "Send Message" sub-action after "Get Death Count"
   - Use variable: `Current deaths: %DeathCountTotal% (%DeathCounterCurrentGame%: %DeathCountGame%)`

---

## Testing Actions

**To test if actions work:**

1. **Start Death Counter:**
   - Run the action (right-click → Execute Action)
   - Check if `C:\deathcounter\daemon.lock` file is created
   - Check `C:\deathcounter\debug.log` for startup messages

2. **Get Death Count:**
   - Run the action
   - Check Streamer.bot Variables (should see DeathCountTotal, DeathCountGame, etc.)
   - Or use the variables in a test message

3. **Stop Death Counter:**
   - Run the action
   - Check if `C:\deathcounter\daemon.lock` file is removed
   - Daemon should exit gracefully

---

## Troubleshooting

**Action doesn't do anything:**
- Check if Python is installed and in PATH
- Verify the script path in the code is correct (`C:\deathcounter\multi_game_death_counter.py`)
- Check `C:\deathcounter\debug.log` for errors
- Make sure you compiled the code successfully (no errors)

**"Get Death Count" variables are empty:**
- Make sure the death counter daemon is running first
- Run "Start Death Counter" before "Get Death Count"
- Variables are **Global Variables**, not User Variables

**Hotkey/Command not working:**
- Make sure the action is **Enabled** (check the "Enabled" column)
- For commands, make sure you're in the correct platform/chat
- Try running the action manually first (right-click → Execute) to test





