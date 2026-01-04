# Building the Death Counter GUI as an .exe

## Quick Build

1. **Install PyInstaller:**
   ```powershell
   pip install pyinstaller
   ```

2. **Build the .exe:**
   ```powershell
   cd C:\deathcounter
   pyinstaller --onefile --windowed --name "DeathCounter" --icon=NONE death_counter_gui.py
   ```

3. **Find your .exe:**
   The .exe will be in the `dist` folder:
   ```
   C:\deathcounter\dist\DeathCounter.exe
   ```

## Build Options Explained

- `--onefile` - Creates a single .exe file (no separate files needed)
- `--windowed` - No console window (GUI only)
- `--name "DeathCounter"` - Name of the output .exe
- `--icon=NONE` - No custom icon (you can add one later with `--icon=icon.ico`)

## Advanced Build (with icon)

If you have an icon file:

```powershell
pyinstaller --onefile --windowed --name "DeathCounter" --icon=icon.ico death_counter_gui.py
```

## What Gets Included

The .exe will include:
- Python interpreter
- tkinter (GUI library)
- All necessary Python libraries
- Your GUI code

**Note:** The .exe is standalone - you can move it anywhere and run it, but it still needs:
- The `C:\deathcounter` folder with all the scripts and config files
- Python dependencies installed (for the daemon script)

## Distribution

To distribute the .exe:
1. Build the .exe using the steps above
2. Copy `DeathCounter.exe` to wherever you want
3. Make sure the user has the `C:\deathcounter` folder with all scripts
4. The .exe will work from any location as long as the deathcounter folder exists

## Troubleshooting

**"Module not found" errors:**
- Make sure all dependencies are installed: `pip install pyinstaller`

**Large file size:**
- This is normal - PyInstaller bundles Python and all libraries
- Typical size: 10-20 MB

**Antivirus warnings:**
- Some antivirus software flags PyInstaller .exe files
- This is a false positive - you can add an exception

