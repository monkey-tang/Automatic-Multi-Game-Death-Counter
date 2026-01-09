"""
Death Counter GUI Application
A simple GUI to control the death counter daemon and view stats.

To create an .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "DeathCounter" death_counter_gui.py
"""

import os
import sys
import json
import time
import subprocess
import threading
from tkinter import *
from tkinter import ttk, messagebox

# Get the directory where this script is located (works for both .exe and .py)
def get_base_dir():
    """Get the base directory - same folder as this script."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe - use the directory where .exe is located
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Running as script - use the directory where the script is located
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
READY_FILE = os.path.join(BASE_DIR, "daemon.ready")  # Signal file created after full initialization
STOP_FILE = os.path.join(BASE_DIR, "STOP")
GUI_DEBUG_LOG = os.path.join(BASE_DIR, "gui_debug.log")  # Debug log for GUI
# Primary script path (new naming)
SCRIPT_PATH = os.path.join(BASE_DIR, "multi_game_death_counter.py")
# Backward compatibility: also try the old name if needed
if not os.path.exists(SCRIPT_PATH):
    SCRIPT_PATH = os.path.join(BASE_DIR, "multi_game_death_counter.py")
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")


class DeathCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Death Counter Control")
        self.root.geometry("400x340")
        self.root.resizable(False, False)
        
        # Variables
        self.daemon_process = None
        self.monitoring = False
        
        # Create UI
        self.create_ui()
        
        # Check initial state (after UI is created)
        self.update_status()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Death Counter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        # Status and total deaths in a row
        status_row = ttk.Frame(status_frame)
        status_row.grid(row=0, column=0, sticky=(W, E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_row, text="Checking...", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=W)
        
        # Total deaths label
        self.total_deaths_label = ttk.Label(status_row, text="Total Deaths: 0", font=("Arial", 10, "bold"))
        self.total_deaths_label.grid(row=0, column=1, sticky=E, padx=(20, 0))
        
        # Death count display - Large clickable button
        count_frame = ttk.Frame(main_frame)
        count_frame.grid(row=2, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        # Create a large button that shows death count and game name
        # Use a frame with label for better text control
        button_container = Frame(count_frame, bg="#f0f0f0", relief=RAISED, bd=3)
        button_container.grid(row=0, column=0, sticky=(W, E), ipadx=10, ipady=10)
        count_frame.columnconfigure(0, weight=1)
        
        # Death count label (large)
        self.death_count_label = Label(
            button_container,
            text="0",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="black"
        )
        self.death_count_label.pack(pady=(10, 5))
        
        # Game name label (smaller, wraps)
        self.game_name_label = Label(
            button_container,
            text="No game selected",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black",
            wraplength=320,
            justify=CENTER
        )
        self.game_name_label.pack(pady=(0, 10))
        
        # Make the whole container clickable
        self.death_count_button = button_container
        # Use ButtonRelease-1 for better click detection
        button_container.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        button_container.bind("<Enter>", lambda e: self.on_button_enter(button_container))
        button_container.bind("<Leave>", lambda e: self.on_button_leave(button_container))
        self.death_count_label.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        self.game_name_label.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        button_container.config(cursor="hand2")
        self.death_count_label.config(cursor="hand2")
        self.game_name_label.config(cursor="hand2")
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Control", padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(W, E), pady=(0, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Daemon", command=self.start_daemon, width=18)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Daemon", command=self.stop_daemon, width=18, state=DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(5, 0))
        
        # Load available games
        self.load_games()
    
    def on_button_enter(self, container):
        """Change background on hover."""
        container.config(bg="#e0e0e0")
        self.death_count_label.config(bg="#e0e0e0")
        self.game_name_label.config(bg="#e0e0e0")
    
    def on_button_leave(self, container):
        """Restore background on leave."""
        container.config(bg="#f0f0f0")
        self.death_count_label.config(bg="#f0f0f0")
        self.game_name_label.config(bg="#f0f0f0")
    
    def load_games(self):
        """Load available games from config."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.available_games = list(config.get("games", {}).keys())
            else:
                self.available_games = ["Elden Ring", "Dark Souls 3", "Dark Souls Remastered", "Sekiro"]
        except:
            self.available_games = ["Elden Ring", "Dark Souls 3", "Dark Souls Remastered", "Sekiro"]
        
        if not self.available_games:
            self.available_games = ["No games configured"]
    
    def get_current_game(self):
        """Get current game from state or config."""
        try:
            # Try state file first
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                game = state.get("current_game")
                if game:
                    return game
            
            # Fall back to config
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("current_game", self.available_games[0] if self.available_games else "Unknown")
        except:
            pass
        
        return self.available_games[0] if self.available_games else "Unknown"
    
    def get_death_count(self, game_name):
        """Get death count for a specific game."""
        try:
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                game_deaths = state.get("game_deaths", {})
                return game_deaths.get(game_name, 0)
        except:
            pass
        return 0
    
    def get_total_deaths(self):
        """Get total deaths across all games."""
        try:
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                return state.get("total_deaths", 0)
        except:
            pass
        return 0
    
    def cycle_game(self, event=None):
        """Cycle to the next game in the list."""
        if not self.available_games or len(self.available_games) == 0:
            messagebox.showwarning("No Games", "No games configured.")
            return
        
        current_game = self.get_current_game()
        
        # Find current index
        try:
            current_index = self.available_games.index(current_game)
            next_index = (current_index + 1) % len(self.available_games)
        except:
            next_index = 0
        
        new_game = self.available_games[next_index]
        
        # Switch game using the manual switch script
        try:
            switch_script = os.path.join(BASE_DIR, "switch_game_manual.py")
            if os.path.exists(switch_script):
                result = subprocess.run(
                    [sys.executable, switch_script, new_game],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR
                )
                if result.returncode == 0:
                    self.update_status()
                    # Silently switch - no popup
                else:
                    # Fallback to direct switch if script fails
                    self.switch_game_direct(new_game)
            else:
                # Fallback: directly update config
                self.switch_game_direct(new_game)
        except Exception as e:
            # Fallback to direct switch on any error
            try:
                self.switch_game_direct(new_game)
            except:
                pass
    
    def switch_game_direct(self, game_name):
        """Directly switch game by updating config and state."""
        try:
            # Update config
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                config["current_game"] = game_name
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
            
            # Update state
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                state["current_game"] = game_name
                with open(STATE_JSON, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
            
            # Update text file
            game_deaths = self.get_death_count(game_name)
            with open(DEATH_TXT, "w", encoding="utf-8") as f:
                f.write(str(game_deaths))
            
            self.update_status()
            # Silently switch - no popup
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch game: {e}")
    
    def is_daemon_running(self):
        """Check if daemon is running - check both lock file and process."""
        # Check lock file
        if not os.path.exists(LOCK_FILE):
            return False
        
        # Verify the process in the lock file is actually running
        try:
            with open(LOCK_FILE, "r") as f:
                pid_str = f.read().strip()
            if pid_str:
                pid = int(pid_str)
                # Check if process exists
                try:
                    import psutil
                    return psutil.pid_exists(pid)
                except:
                    # Fallback: use tasklist on Windows
                    try:
                        result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}"],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        return f"{pid}" in result.stdout
                    except:
                        # If we can't check, assume it's running if lock file exists
                        return True
        except:
            # If we can't read the lock file, assume it's not running
            return False
        
        return True
    
    def find_python_executable(self):
        """Find Python executable, checking PATH and common installation locations.
        Comprehensive search for general public use."""
        # If running as a script (not frozen), use sys.executable
        if not getattr(sys, 'frozen', False):
            return sys.executable
        
        # If running as PyInstaller exe, we need to find Python
        # Method 1: Try 'python' command (if in PATH) - most reliable
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'python'
        except:
            pass
        
        # Method 2: Try 'py' launcher (Windows Python launcher) - also reliable
        try:
            result = subprocess.run(['py', '--version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'py'
        except:
            pass
        
        # Method 3: Search Windows Registry for Python installations
        try:
            import winreg
            # Check both 32-bit and 64-bit registry
            for arch in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
                try:
                    # Check HKEY_LOCAL_MACHINE
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                        r"SOFTWARE\Python\PythonCore", 0,
                                        winreg.KEY_READ | arch)
                    try:
                        # Get all installed Python versions
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                install_path_key = winreg.OpenKey(key, f"{version}\\InstallPath")
                                try:
                                    install_path = winreg.QueryValueEx(install_path_key, "")[0]
                                    python_exe = os.path.join(install_path, "python.exe")
                                    if os.path.exists(python_exe):
                                        winreg.CloseKey(install_path_key)
                                        winreg.CloseKey(key)
                                        return python_exe
                                    winreg.CloseKey(install_path_key)
                                except:
                                    pass
                                i += 1
                            except OSError:
                                break
                        winreg.CloseKey(key)
                    except:
                        try:
                            winreg.CloseKey(key)
                        except:
                            pass
                except:
                    pass
        except:
            pass
        
        # Method 4: Search common installation locations
        userprofile = os.getenv('USERPROFILE', '')
        programfiles = os.getenv('ProgramFiles', r'C:\Program Files')
        programfiles_x86 = os.getenv('ProgramFiles(x86)', r'C:\Program Files (x86)')
        
        search_paths = []
        
        # User AppData locations (most common for Python 3.8+)
        if userprofile:
            appdata_local = os.path.join(userprofile, r"AppData\Local\Programs\Python")
            if os.path.exists(appdata_local):
                # Search all Python versions in this directory
                try:
                    for item in os.listdir(appdata_local):
                        python_dir = os.path.join(appdata_local, item)
                        if os.path.isdir(python_dir):
                            python_exe = os.path.join(python_dir, "python.exe")
                            if os.path.exists(python_exe):
                                search_paths.append(python_exe)
                except:
                    pass
        
        # Common root-level Python installations
        for version in ['312', '311', '310', '39', '38']:
            search_paths.extend([
                os.path.join(r"C:\Python" + version, "python.exe"),
                os.path.join(programfiles, f"Python{version}", "python.exe"),
                os.path.join(programfiles_x86, f"Python{version}", "python.exe"),
            ])
        
        # Check all collected paths
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        # Method 5: Recursive search in Program Files (last resort, slower)
        try:
            for root_dir in [programfiles, programfiles_x86]:
                if os.path.exists(root_dir):
                    for root, dirs, files in os.walk(root_dir):
                        # Limit depth to avoid slow searches
                        depth = root[len(root_dir):].count(os.sep)
                        if depth > 2:  # Max 2 levels deep
                            dirs[:] = []  # Don't recurse deeper
                            continue
                        
                        if 'python.exe' in files:
                            python_exe = os.path.join(root, 'python.exe')
                            # Verify it's actually Python
                            try:
                                result = subprocess.run([python_exe, '--version'], 
                                                      capture_output=True, timeout=1)
                                if result.returncode == 0:
                                    return python_exe
                            except:
                                pass
        except:
            pass
        
        return None
    
    def is_python_version_compatible(self, python_exe):
        """Check if Python version is compatible (3.8-3.13)."""
        try:
            # Try to get version without hanging - use a very short timeout
            result = subprocess.run(
                [python_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                version_str = result.stdout.strip() or result.stderr.strip()
                # Parse version (e.g., "Python 3.12.0" -> (3, 12))
                import re
                match = re.search(r'(\d+)\.(\d+)', version_str)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    # Check if version is 3.8-3.13
                    if major == 3 and 8 <= minor <= 13:
                        return True
        except:
            pass
        return False
    
    def find_python_executable_daemon(self):
        """Find python.exe specifically (not pythonw.exe) for daemon.
        Only returns Python versions 3.8-3.13 (compatible with dependencies)."""
        # Try 'python' command first (should be python.exe)
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                if self.is_python_version_compatible('python'):
                    return 'python'
        except:
            pass
        
        # Search for python.exe in common locations
        userprofile = os.getenv('USERPROFILE', '')
        programfiles = os.getenv('ProgramFiles', r'C:\Program Files')
        programfiles_x86 = os.getenv('ProgramFiles(x86)', r'C:\Program Files (x86)')
        
        python_versions = []  # List of (version_tuple, path) for sorting
        
        # User AppData locations - collect all versions and check compatibility
        if userprofile:
            appdata_local = os.path.join(userprofile, r"AppData\Local\Programs\Python")
            if os.path.exists(appdata_local):
                try:
                    for item in os.listdir(appdata_local):
                        python_dir = os.path.join(appdata_local, item)
                        if os.path.isdir(python_dir):
                            python_exe = os.path.join(python_dir, "python.exe")
                            if os.path.exists(python_exe):
                                # Check if version is compatible
                                if self.is_python_version_compatible(python_exe):
                                    # Extract version number from directory name (e.g., "Python312" -> (3, 12))
                                    try:
                                        version_str = item.replace("Python", "").replace("python", "").replace(".", "")
                                        if version_str:
                                            # Handle formats like "312", "39", "310"
                                            if len(version_str) >= 2:
                                                major = 3
                                                if len(version_str) == 2:
                                                    minor = int(version_str)
                                                else:
                                                    minor = int(version_str[:2])
                                                python_versions.append(((major, minor), python_exe))
                                    except:
                                        # If we can't parse, check by running Python
                                        python_versions.append(((0, 0), python_exe))
                except:
                    pass
        
        # Common root-level Python installations (3.8-3.13)
        for major_minor in [(3, 13), (3, 12), (3, 11), (3, 10), (3, 9), (3, 8)]:
            version_str = f"{major_minor[0]}{major_minor[1]:02d}"  # e.g., "312", "39"
            for base_path in [
                os.path.join(rf"C:\Python{version_str}", "python.exe"),
                os.path.join(programfiles, f"Python{version_str}", "python.exe"),
                os.path.join(programfiles_x86, f"Python{version_str}", "python.exe"),
            ]:
                if os.path.exists(base_path):
                    if self.is_python_version_compatible(base_path):
                        python_versions.append((major_minor, base_path))
        
        # Sort by version (newest first) - (3, 13) > (3, 12) > ... > (3, 8)
        python_versions.sort(reverse=True, key=lambda x: x[0])
        
        # Return the newest compatible version
        for (major, minor), path in python_versions:
            return path
        
        return None
    
    def start_daemon(self):
        """Start the death counter daemon."""
        # Initialize debug log at the very start - MUST be first thing
        debug_log_created = False
        try:
            os.makedirs(BASE_DIR, exist_ok=True)  # Ensure directory exists
            with open(GUI_DEBUG_LOG, "w", encoding="utf-8") as f:
                f.write(f"{'='*70}\n")
                f.write(f"GUI: start_daemon() called at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"GUI: BASE_DIR = {BASE_DIR}\n")
                f.write(f"GUI: LOCK_FILE = {LOCK_FILE}\n")
                f.write(f"GUI: READY_FILE = {READY_FILE}\n")
                f.write(f"GUI: BASE_DIR exists: {os.path.exists(BASE_DIR)}\n")
                f.write(f"GUI: BASE_DIR writable: {os.access(BASE_DIR, os.W_OK)}\n")
                f.flush()  # Force write
            debug_log_created = True
        except Exception as e:
            # If we can't write debug log, try to show error in messagebox
            try:
                messagebox.showerror("Debug Log Error", f"Could not create debug log: {e}\n\nBASE_DIR: {BASE_DIR}")
            except:
                pass
        
        # Check if daemon is running
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write("GUI: Calling is_daemon_running()...\n")
        except:
            pass
        
        daemon_running_check = self.is_daemon_running()
        
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"GUI: is_daemon_running() returned: {daemon_running_check}\n")
        except:
            pass
        
        if daemon_running_check:
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write("GUI: Daemon appears to be running - checking process...\n")
            except:
                pass
            # Check if the process is actually running
            try:
                with open(LOCK_FILE, "r") as f:
                    pid_str = f.read().strip()
                if pid_str:
                    pid = int(pid_str)
                    # Check if process exists
                    try:
                        import psutil
                        if psutil.pid_exists(pid):
                            messagebox.showinfo("Info", f"Daemon is already running (PID: {pid}).")
                            return
                        else:
                            # Stale lock file - process doesn't exist
                            os.remove(LOCK_FILE)
                    except:
                        # psutil not available or other error - try tasklist
                        try:
                            result = subprocess.run(
                                ["tasklist", "/FI", f"PID eq {pid}"],
                                capture_output=True,
                                text=True,
                                timeout=2
                            )
                            if f"{pid}" in result.stdout:
                                messagebox.showinfo("Info", f"Daemon is already running (PID: {pid}).")
                                return
                            else:
                                # Stale lock file
                                os.remove(LOCK_FILE)
                        except:
                            # Can't check - remove lock file to be safe
                            try:
                                os.remove(LOCK_FILE)
                            except:
                                pass
            except:
                # Can't read lock file - remove it
                try:
                    os.remove(LOCK_FILE)
                except:
                    pass
        
        # Check if script exists (try both possible names)
        script_path = SCRIPT_PATH
        if not os.path.exists(script_path):
            alt_path = os.path.join(BASE_DIR, "multi_game_death_counter.py")
            if os.path.exists(alt_path):
                script_path = alt_path
            else:
                messagebox.showerror("Error", f"Death counter script not found.\n\nLooking for:\n{SCRIPT_PATH}\nor\n{alt_path}")
                return
        
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write("GUI: Finding Python executable...\n")
                    f.write(f"GUI: sys.frozen = {getattr(sys, 'frozen', False)}\n")
        except:
            pass
        
        # Find Python executable (use python.exe, not pythonw.exe for daemon)
        python_cmd = None
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write("GUI: About to check sys.frozen...\n")
                    f.flush()
        except:
            pass
        
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled exe - need to find Python
                # First try to find python.exe directly
                python_cmd = self.find_python_executable_daemon()
                if not python_cmd:
                    # Fallback to regular finder
                    python_cmd = self.find_python_executable()
                    if not python_cmd:
                        messagebox.showerror("Error", "Python not found. Please install Python and add it to PATH, or restart the installer after installing Python.")
                        return
                
                # Ensure we're using python.exe, not pythonw.exe
                if python_cmd.endswith('pythonw.exe') or 'pythonw' in python_cmd.lower():
                    # Try to find python.exe in the same directory
                    if os.path.exists(python_cmd):
                        python_dir = os.path.dirname(python_cmd)
                        python_exe = os.path.join(python_dir, "python.exe")
                        if os.path.exists(python_exe):
                            python_cmd = python_exe
                        else:
                            # Try replacing pythonw with python in the path
                            python_cmd = python_cmd.replace('pythonw.exe', 'python.exe').replace('pythonw', 'python')
            else:
                # Running as script - use sys.executable
                try:
                    if debug_log_created:
                        with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                            f.write(f"GUI: Running as script, using sys.executable\n")
                            f.write(f"GUI: sys.executable = {sys.executable}\n")
                            f.flush()
                except:
                    pass
                python_cmd = sys.executable
                # If it's pythonw, try to find python.exe
                if python_cmd.endswith('pythonw.exe'):
                    try:
                        if debug_log_created:
                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                f.write(f"GUI: sys.executable is pythonw.exe, looking for python.exe\n")
                                f.flush()
                    except:
                        pass
                    python_dir = os.path.dirname(python_cmd)
                    python_exe = os.path.join(python_dir, "python.exe")
                    if os.path.exists(python_exe):
                        python_cmd = python_exe
                        try:
                            if debug_log_created:
                                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                    f.write(f"GUI: Found python.exe: {python_exe}\n")
                                    f.flush()
                        except:
                            pass
                    else:
                        try:
                            if debug_log_created:
                                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                    f.write(f"GUI: python.exe not found in {python_dir}\n")
                                    f.flush()
                        except:
                            pass
                else:
                    try:
                        if debug_log_created:
                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                f.write(f"GUI: Using sys.executable as-is: {python_cmd}\n")
                                f.flush()
                    except:
                        pass
        except Exception as e:
            # If there's an error finding Python, log it
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write(f"GUI: ERROR in Python finding logic: {e}\n")
                        import traceback
                        f.write(traceback.format_exc())
                        f.flush()
            except:
                pass
            messagebox.showerror("Error", f"Error finding Python executable: {e}")
            return
        
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"GUI: Final Python command: {python_cmd}\n")
                    f.write(f"GUI: Python exists: {os.path.exists(python_cmd) if python_cmd else False}\n")
                    f.flush()
        except:
            pass
        
        if not python_cmd:
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write("GUI: ERROR - python_cmd is None!\n")
                        f.flush()
            except:
                pass
            messagebox.showerror("Error", "Could not determine Python executable.")
            return
        
        # Skip Python test - we already verified the executable exists
        # The test was timing out on some systems (especially with multiple Python versions),
        # and we'll get better error messages from the daemon itself if Python doesn't work
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write("GUI: Skipping Python test (already verified executable exists)\n")
                    f.write(f"GUI: Using Python: {python_cmd}\n")
                    f.write("GUI: Proceeding directly to start daemon\n")
                    f.flush()
        except:
            pass
        
        # Start daemon in background
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"GUI: About to start daemon process with subprocess.Popen\n")
                    f.write(f"GUI: Python: {python_cmd}\n")
                    f.write(f"GUI: Script: {script_path}\n")
                    f.write(f"GUI: Working dir: {BASE_DIR}\n")
                    f.write(f"GUI: Script exists: {os.path.exists(script_path)}\n")
                    f.flush()
        except:
            pass
        
        try:
            # Use subprocess.PIPE but also allow seeing output for debugging
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write("GUI: Calling subprocess.Popen() now...\n")
                        f.flush()
            except:
                pass
            
            CREATE_NO_WINDOW = 0x08000000 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            if sys.platform == "win32":
                self.daemon_process = subprocess.Popen(
                    [python_cmd, script_path],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Merge stderr into stdout
                    text=True,
                    bufsize=1,  # Line buffered
                    creationflags=CREATE_NO_WINDOW
                )
            else:
                self.daemon_process = subprocess.Popen(
                    [python_cmd, script_path],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write(f"GUI: subprocess.Popen() completed\n")
                        f.write(f"GUI: Daemon process PID: {self.daemon_process.pid}\n")
                        f.write(f"GUI: Process poll result: {self.daemon_process.poll()}\n")
                        f.flush()
            except Exception as e:
                try:
                    if debug_log_created:
                        with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                            f.write(f"GUI: ERROR logging process info: {e}\n")
                            f.flush()
                except:
                    pass
        except Exception as e:
            try:
                if debug_log_created:
                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                        f.write(f"GUI: ERROR - Exception during subprocess.Popen(): {e}\n")
                        import traceback
                        f.write(traceback.format_exc())
                        f.flush()
            except:
                pass
            messagebox.showerror("Error", f"Error starting daemon: {e}\n\nPython: {python_cmd}\nScript: {script_path}")
            return
        
        # Wait for daemon to start - poll both process and lock file
        max_wait_time = 15  # Wait up to 15 seconds (increased for safety)
        check_interval = 0.2  # Check every 0.2 seconds (more frequent)
        waited = 0
        process_exited = False
        lock_file_created = False
        
        # Debug: Log paths being checked to file
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"\n{'='*70}\n")
                    f.write(f"GUI: Starting daemon at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"GUI: Checking for LOCK_FILE at: {LOCK_FILE}\n")
                    f.write(f"GUI: Checking for READY_FILE at: {READY_FILE}\n")
                    f.write(f"GUI: BASE_DIR is: {BASE_DIR}\n")
                    f.write(f"GUI: Script path: {script_path}\n")
                    f.write(f"GUI: Python cmd: {python_cmd}\n")
                    f.write(f"GUI: LOCK_FILE exists: {os.path.exists(LOCK_FILE)}\n")
                    f.write(f"GUI: READY_FILE exists: {os.path.exists(READY_FILE)}\n")
                    f.flush()
        except:
            pass
        
        while waited < max_wait_time:
            # Log every 2 seconds what we're checking
            if waited > 0 and int(waited * 10) % 10 == 0:  # Every 1 second
                    try:
                        if debug_log_created:
                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                f.write(f"GUI: Wait loop - waited {waited:.1f}s, checking files...\n")
                                f.write(f"GUI:   LOCK_FILE exists: {os.path.exists(LOCK_FILE)}\n")
                                f.write(f"GUI:   READY_FILE exists: {os.path.exists(READY_FILE)}\n")
                                f.write(f"GUI:   Process running: {self.daemon_process.poll() is None}\n")
                    except:
                        pass
            
            # Check if process exited (error)
            if self.daemon_process.poll() is not None:
                    process_exited = True
                    # Process exited - there was an error
                    try:
                        stdout, _ = self.daemon_process.communicate(timeout=1)
                        error_msg = ""
                        if stdout:
                            error_msg = stdout.strip() if isinstance(stdout, str) else stdout.decode('utf-8', errors='ignore').strip()
                        if not error_msg:
                            error_msg = f"Process exited with code {self.daemon_process.returncode}"
                        
                        # Check debug.log for more details
                        log_file = os.path.join(BASE_DIR, "debug.log")
                        if os.path.exists(log_file):
                            try:
                                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines = f.readlines()
                                    if lines:
                                        last_lines = ''.join(lines[-5:])  # Last 5 lines
                                        if last_lines.strip():
                                            error_msg += f"\n\nLast log entries:\n{last_lines[:400]}"
                            except:
                                pass
                        
                        # Try to get more info by running the script directly
                        direct_test = subprocess.run(
                            [python_cmd, script_path],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            cwd=BASE_DIR
                        )
                        if direct_test.stderr:
                            error_msg = direct_test.stderr[:500]
                        elif direct_test.stdout:
                            error_msg = direct_test.stdout[:500]
                        
                        messagebox.showerror("Error", f"Failed to start daemon.\n\nPython: {python_cmd}\nScript: {script_path}\n\nError: {error_msg[:500]}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to start daemon.\n\nPython: {python_cmd}\nScript: {script_path}\n\nProcess exited immediately. Check if all dependencies are installed.\n\nException: {e}")
                    return
            
            # Check if lock file exists (even if process check fails)
            if os.path.exists(LOCK_FILE):
                    lock_file_created = True
                    if waited < 0.5:  # Only log once
                        try:
                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                f.write(f"GUI: Lock file found at: {LOCK_FILE}\n")
                        except:
                            pass
                    
                    # Check for ready file (daemon fully initialized)
                    # Also verify the file actually has content (not just created)
                    # Try multiple times with small delay to handle filesystem delays
                    ready_file_found = False
                    for check_attempt in range(5):  # Increased retries
                        if os.path.exists(READY_FILE):
                            try:
                                # Verify file has content and is recent
                                stat = os.stat(READY_FILE)
                                if stat.st_size > 0:
                                    # Double-check the process is still running
                                    if self.daemon_process.poll() is None:
                                        # Daemon is fully ready!
                                        try:
                                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                                f.write(f"GUI: Ready file found and verified! Size: {stat.st_size} bytes\n")
                                                f.write(f"GUI: Daemon started successfully!\n")
                                        except:
                                            pass
                                        self.update_status()
                                        messagebox.showinfo("Success", "Death counter daemon started successfully!")
                                        return
                                    else:
                                        # Process died - break out and show error
                                        try:
                                            with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                                f.write(f"GUI: Ready file exists but process exited (code: {self.daemon_process.returncode})\n")
                                        except:
                                            pass
                                        break
                                else:
                                    try:
                                        with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                            f.write(f"GUI: Ready file exists but is empty (attempt {check_attempt + 1})\n")
                                    except:
                                        pass
                            except Exception as e:
                                try:
                                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                        f.write(f"GUI: Error checking ready file: {e}\n")
                                except:
                                    pass
                        else:
                            if check_attempt == 0 and waited > 1:
                                try:
                                    with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                                        f.write(f"GUI: Ready file not found yet (attempt {check_attempt + 1}), waited {waited:.1f}s\n")
                                        f.write(f"GUI: LOCK_FILE exists: {os.path.exists(LOCK_FILE)}\n")
                                        f.write(f"GUI: READY_FILE exists: {os.path.exists(READY_FILE)}\n")
                                except:
                                    pass
                        # Small delay before retry (filesystem might need time)
                        if check_attempt < 4:
                            time.sleep(0.2)
                    # Lock file exists but not ready yet - check debug.log to see what's happening
                    log_file = os.path.join(BASE_DIR, "debug.log")
                    if os.path.exists(log_file) and waited > 2:  # Only check log after 2 seconds
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                if lines:
                                    last_line = lines[-1].strip() if lines else ""
                                    # If we see "Ready file created" but file doesn't exist, there's a filesystem issue
                                    if "Ready file created" in last_line or "READY_FILE created" in last_line:
                                        # File should exist - maybe filesystem delay, wait a bit more
                                        time.sleep(0.5)
                                        if os.path.exists(READY_FILE):
                                            self.update_status()
                                            messagebox.showinfo("Success", "Death counter daemon started successfully!")
                                            return
                        except:
                            pass
                    # Lock file exists but not ready yet - give it more time
                    time.sleep(0.2)
                    continue
            # Also check if process is still running (even without lock file yet)
            elif self.daemon_process.poll() is None:
                # Process is running, might still be initializing
                continue
            
            # Wait a bit before checking again
            time.sleep(check_interval)
            waited += check_interval
        
        # Timeout - check what happened
        # Log timeout to debug file
        try:
            if debug_log_created:
                with open(GUI_DEBUG_LOG, "a", encoding="utf-8") as f:
                    f.write(f"GUI: TIMEOUT after {waited:.1f} seconds\n")
                    f.write(f"GUI: LOCK_FILE exists: {os.path.exists(LOCK_FILE)}\n")
                    f.write(f"GUI: READY_FILE exists: {os.path.exists(READY_FILE)}\n")
                    f.write(f"GUI: Process running: {self.daemon_process.poll() is None}\n")
                    f.flush()
        except:
            pass
        
        # First, check for startup error file
        startup_error_file = os.path.join(BASE_DIR, "daemon_startup_error.txt")
        if os.path.exists(startup_error_file):
            try:
                with open(startup_error_file, 'r', encoding='utf-8', errors='ignore') as f:
                    error_content = f.read().strip()
                if error_content:
                    messagebox.showerror("Daemon Startup Error", 
                        f"Daemon encountered an error during startup:\n\n{error_content[:1000]}\n\n"
                        f"Python: {python_cmd}\nScript: {script_path}")
                    return
            except:
                pass
        
        if process_exited:
            # Already handled above
            return
        elif lock_file_created and os.path.exists(READY_FILE):
            # Both files exist - daemon should be running
            if self.is_daemon_running():
                self.update_status()
                messagebox.showinfo("Success", "Death counter daemon started successfully!")
                return
            else:
                error_msg = "Ready file exists but process is not running."
        elif lock_file_created:
            # Lock file exists but ready file doesn't - daemon may be stuck initializing
            error_msg = "Lock file exists but daemon did not finish initializing (ready file missing)."
            try:
                with open(LOCK_FILE, "r") as f:
                    pid_str = f.read().strip()
                error_msg = f"Lock file exists (PID: {pid_str}) but daemon did not finish initializing (ready file missing)."
                
                # Check if process is still running
                process_running = False
                try:
                    import psutil
                    if pid_str:
                        pid = int(pid_str)
                        if psutil.pid_exists(pid):
                            process_running = True
                            error_msg += f"\n\nProcess {pid} is still running."
                        else:
                            error_msg += f"\n\nProcess {pid} is NOT running (stale lock file)."
                except:
                    # Fallback: check if daemon process is still running
                    if self.daemon_process.poll() is None:
                        process_running = True
                        error_msg += "\n\nDaemon process is still running."
                
                # If process is running but ready file missing, check if it's just slow
                if process_running:
                    error_msg += "\n\nThis might be a filesystem delay. The daemon may still be starting."
                    error_msg += "\nCheck debug.log to see if 'Ready file created' appears."
            except:
                pass
            
            # Check debug.log
            log_file = os.path.join(BASE_DIR, "debug.log")
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if lines:
                            last_lines = ''.join(lines[-15:])  # Last 15 lines
                            error_msg += f"\n\nLast log entries:\n{last_lines[:500]}"
                except:
                    pass
            
            messagebox.showerror("Error", f"{error_msg}\n\nPython: {python_cmd}\nScript: {script_path}\n\nTry stopping any existing daemon first, then start again.")
        elif self.daemon_process.poll() is None:
            # Process is still running but no lock file
            error_msg = "Daemon process is running but failed to create lock file."
            try:
                # Check debug.log for errors
                log_file = os.path.join(BASE_DIR, "debug.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if lines:
                            last_lines = ''.join(lines[-15:])  # Last 15 lines
                            error_msg += f"\n\nLast log entries:\n{last_lines[:500]}"
                else:
                    error_msg += "\n\nNo debug.log found - daemon may not have initialized."
            except:
                pass
            messagebox.showerror("Error", f"{error_msg}\n\nPython: {python_cmd}\nScript: {script_path}\n\nCheck if all dependencies are installed and Tesseract OCR is installed.")
        else:
            # Process exited during wait
            error_msg = "Process exited before creating lock file."
            # Check debug.log
            log_file = os.path.join(BASE_DIR, "debug.log")
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if lines:
                            last_lines = ''.join(lines[-15:])  # Last 15 lines
                            error_msg += f"\n\nLast log entries:\n{last_lines[:500]}"
                except:
                    pass
            messagebox.showerror("Error", f"{error_msg}\n\nPython: {python_cmd}\nScript: {script_path}\n\nCheck debug.log for details.")
    
    def stop_daemon(self):
        """Stop the death counter daemon."""
        if not self.is_daemon_running():
            # Silently return - no popup
            return
        
        try:
            # Create STOP file
            with open(STOP_FILE, "w") as f:
                f.write("")
            
            # Wait for daemon to stop
            for i in range(10):
                time.sleep(1)
                if not self.is_daemon_running():
                    break
            
            # If still running, try to kill process
            if self.is_daemon_running():
                try:
                    with open(LOCK_FILE, "r") as f:
                        pid = f.read().strip()
                    if pid:
                        subprocess.run(["taskkill", "/F", "/PID", pid], 
                                     capture_output=True, check=False)
                    if os.path.exists(LOCK_FILE):
                        os.remove(LOCK_FILE)
                except:
                    pass
            
            # Clean up
            if os.path.exists(STOP_FILE):
                os.remove(STOP_FILE)
            if os.path.exists(READY_FILE):
                os.remove(READY_FILE)
            
            self.update_status()
            # Silently stop - no popup
        except Exception as e:
            # Silently fail - no popup
            pass
    
    def update_status(self):
        """Update the UI with current status."""
        # Check if UI elements exist (they might not during initialization)
        if not hasattr(self, 'status_label'):
            return
        
        # Update daemon status
        running = self.is_daemon_running()
        if running:
            self.status_label.config(text="Status: Running", foreground="green")
            if hasattr(self, 'start_button'):
                self.start_button.config(state=DISABLED)
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=NORMAL)
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            if hasattr(self, 'start_button'):
                self.start_button.config(state=NORMAL)
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=DISABLED)
        
        # Update game and death count on the button
        current_game = self.get_current_game()
        death_count = self.get_death_count(current_game)
        total_deaths = self.get_total_deaths()
        
        # Update the labels separately
        if hasattr(self, 'death_count_label') and hasattr(self, 'game_name_label'):
            self.death_count_label.config(text=str(death_count))
            self.game_name_label.config(text=current_game)
        
        # Update total deaths display
        if hasattr(self, 'total_deaths_label'):
            self.total_deaths_label.config(text=f"Total Deaths: {total_deaths}")
    
    def start_monitoring(self):
        """Start background thread to monitor status."""
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    self.root.after(0, self.update_status)
                    time.sleep(2)  # Update every 2 seconds
                except:
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window closing."""
        self.monitoring = False
        self.root.destroy()


def main():
    # Prevent multiple instances of the GUI using Windows mutex
    # Check mutex BEFORE creating any GUI elements
    mutex = None
    kernel32 = None
    try:
        import ctypes
        mutex_name = "Global\\DeathCounterGUIMutex"
        kernel32 = ctypes.windll.kernel32
        mutex = kernel32.CreateMutexW(None, False, mutex_name)
        last_error = kernel32.GetLastError()
        
        # If ERROR_ALREADY_EXISTS, another GUI instance is running
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            if mutex:
                kernel32.CloseHandle(mutex)
            # Exit immediately - GUI already running
            sys.exit(0)
    except Exception:
        # If mutex fails, continue anyway
        pass
    
    root = Tk()
    app = DeathCounterGUI(root)
    
    def cleanup():
        try:
            if mutex and kernel32:
                kernel32.CloseHandle(mutex)
        except:
            pass
        if hasattr(app, 'on_closing'):
            app.on_closing()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", cleanup)
    
    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
