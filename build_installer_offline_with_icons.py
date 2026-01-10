"""
Build helper script for offline installer that conditionally includes icon files.
This ensures the build succeeds even if icon files are missing.
"""

import os
import subprocess
import sys

def build_installer_offline():
    """Build the offline installer with conditional icon files."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--windowed",
        "--name", "DeathCounterInstaller-offline",
    ]
    
    # Add installer icon if it exists
    installer_icons = [
        "installer_icon.ico",
        "3386_life_support.ico",
        "3386 life support.ico",
    ]
    for icon in installer_icons:
        if os.path.exists(icon):
            cmd.extend(["--icon", icon])
            print(f"Using installer icon: {icon}")
            break
    
    # Always add required data files
    required_files = [
        "multi_game_death_counter.py",
        "death_counter_gui.py",
        "death_counter_settings.py",
        "log_monitor.py",
        "memory_scanner.py",
        "games_config.json",
        "reset_death_counter.py",
        "switch_game_manual.py",
        "capture_debug_once.py",
        "change_monitor_id.py",
        "requirements.txt",
        "README.md",
        "FUZZY_MATCHING_GUIDE.md",
        "INSTALLER_README.md",  # Installer-specific documentation
        "deathcounteraction.cs",  # Streamer.bot integration action file
    ]
    
    for file in required_files:
        cmd.extend(["--add-data", f"{file};."])
    
    # Conditionally add icon files (for shortcuts)
    icon_files = [
        "gui_icon.ico",
        "smonker.ico",
        "Smonker.ico",
        "shortcut_icon.ico",
        "screenshot.ico",
        "Screenshot.ico",
    ]
    
    icons_added = []
    for icon in icon_files:
        if os.path.exists(icon):
            cmd.extend(["--add-data", f"{icon};."])
            icons_added.append(icon)
    
    if icons_added:
        print(f"Including icon files: {', '.join(icons_added)}")
    else:
        print("No icon files found - shortcuts will use default icons")
    
    # Add hidden imports
    cmd.extend([
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        "--hidden-import", "pytesseract",
        "--hidden-import", "mss",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        "--hidden-import", "psutil",
        "--hidden-import", "watchdog",
        "--hidden-import", "watchdog.observers",
        "--hidden-import", "watchdog.events",
        "--collect-all", "cv2",
        "--collect-all", "numpy",
        "--collect-all", "opencv",
        "--noconfirm",
        "--clean",
        "installer_offline.py",
    ])
    
    print("\nBuilding offline installer...")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    success = build_installer_offline()
    sys.exit(0 if success else 1)
