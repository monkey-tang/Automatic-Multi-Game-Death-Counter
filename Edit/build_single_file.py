"""
Build Script - Creates a single-file distribution
This script packages all files into a single executable installer.
"""

import os
import sys
import base64
import zipfile
import json
from pathlib import Path

# Files to include in the distribution
FILES_TO_INCLUDE = [
    "multi_game_death_counter.py",
    "death_counter_gui.py",
    "switch_game_manual.py",
    "games_config.json",
    "START_DEATH_COUNTER.bat",
    "STOP_DEATH_COUNTER.bat",
    "install_dependencies.bat",
    "README.md",
    "change_monitor_id.py",
    "capture_debug_once.py",
    "CHANGE_MONITOR_ID.bat",
    "CAPTURE_DEBUG.bat",
    "deathcounteraction.cs",
    "test_daemon_start.py",  # Test script to diagnose daemon startup
    "reset_death_counter.py",  # Reset death counts to 0
    "RESET_DEATH_COUNTER.bat",  # Batch file to run reset script
]

# Target filenames are identical now (no prefix mapping needed)
TARGET_NAMES = {name: name for name in FILES_TO_INCLUDE}

def read_file_binary(filepath):
    """Read a file as binary."""
    with open(filepath, 'rb') as f:
        return f.read()

def create_embedded_installer():
    """Create an installer script with embedded files."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read all files
    embedded_files = {}
    for filename in FILES_TO_INCLUDE:
        filepath = os.path.join(script_dir, filename)
        if os.path.exists(filepath):
            content = read_file_binary(filepath)
            # Use target name (without "1" prefix) for extraction
            target_name = TARGET_NAMES.get(filename, filename)
            embedded_files[target_name] = base64.b64encode(content).decode('utf-8')
            print(f"Embedded: {filename} -> {target_name} ({len(content)} bytes)")
        else:
            print(f"Warning: {filename} not found")
    
    # Create the installer script
    installer_template = '''"""
Death Counter - Single File Installer
This is a self-extracting installer that contains all necessary files.
"""

# CRITICAL: Single instance check BEFORE any imports
# This must be the absolute first thing that happens
import sys
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    
    # Try to create a named mutex
    mutex_name = "DeathCounterInstaller_SingleInstance_Mutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    
    # If mutex already exists, another instance is running
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        import ctypes.wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        # Try to find and bring existing window to front
        def enum_windows_callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    if "Death Counter" in buffer.value:
                        user32.SetForegroundWindow(hwnd)
                        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                        return False  # Stop enumeration
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        callback = EnumWindowsProc(enum_windows_callback)
        user32.EnumWindows(callback, None)
        
        sys.exit(0)

import os
import base64
import subprocess
import shutil
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import webbrowser

# Embedded files (base64 encoded)
EMBEDDED_FILES = {embedded_files_dict}

# Get the directory where the installer is located (works for both .exe and .py)
def get_install_dir():
    """Get the installation directory - same folder as the installer executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe - use the directory where .exe is located
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Running as script - use the directory where the script is located
        return os.path.dirname(os.path.abspath(__file__))

INSTALL_DIR = get_install_dir()

def extract_files():
    """Extract all embedded files."""
    extracted = []
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    for filename, content_b64 in EMBEDDED_FILES.items():
        try:
            content = base64.b64decode(content_b64)
            filepath = os.path.join(INSTALL_DIR, filename)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(content)
            
            extracted.append(filepath)
            print(f"Extracted: {{filename}}")
        except Exception as e:
            print(f"Error extracting {{filename}}: {{e}}")
    
    return extracted

def find_python_executable(use_pythonw=False):
    """Find the actual Python executable (not the installer exe).
    Comprehensive search for general public use.
    If use_pythonw=True, searches for pythonw.exe (no console window)."""
    # If running as a script (not frozen), use sys.executable
    if not getattr(sys, 'frozen', False):
        if use_pythonw:
            # Try to find pythonw.exe in the same directory as python.exe
            python_dir = os.path.dirname(sys.executable)
            pythonw_exe = os.path.join(python_dir, "pythonw.exe")
            if os.path.exists(pythonw_exe):
                return pythonw_exe
            return sys.executable  # Fallback to python.exe
        return sys.executable
    
    exe_name = "pythonw.exe" if use_pythonw else "python.exe"
    command_name = "pythonw" if use_pythonw else "python"
    
    # If running as PyInstaller exe, we need to find Python
    # Method 1: Try command (if in PATH) - most reliable
    if not use_pythonw:  # pythonw is rarely in PATH
        try:
            result = subprocess.run([command_name, '--version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return command_name
        except:
            pass
    
    # Method 2: Try 'py' launcher (Windows Python launcher) - also reliable
    if not use_pythonw:  # py launcher doesn't support pythonw directly
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
                            install_path_key = winreg.OpenKey(key, rf"{version}\InstallPath")
                            try:
                                install_path = winreg.QueryValueEx(install_path_key, "")[0]
                                python_exe = os.path.join(install_path, exe_name)
                                if os.path.exists(python_exe):
                                    winreg.CloseKey(install_path_key)
                                    winreg.CloseKey(key)
                                    return python_exe
                                # If pythonw.exe not found, try python.exe as fallback
                                if use_pythonw:
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
                        python_exe = os.path.join(python_dir, exe_name)
                        if os.path.exists(python_exe):
                            search_paths.append(python_exe)
                        # If pythonw.exe not found, try python.exe as fallback
                        elif use_pythonw:
                            python_exe = os.path.join(python_dir, "python.exe")
                            if os.path.exists(python_exe):
                                search_paths.append(python_exe)
            except:
                pass
    
    # Common root-level Python installations
    for version in ['312', '311', '310', '39', '38']:
        search_paths.extend([
            os.path.join(r"C:\Python" + version, exe_name),
            os.path.join(programfiles, f"Python{version}", exe_name),
            os.path.join(programfiles_x86, f"Python{version}", exe_name),
        ])
        # If pythonw.exe not found, add python.exe as fallback
        if use_pythonw:
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
                    
                    if exe_name in files or (use_pythonw and 'python.exe' in files):
                        python_exe = os.path.join(root, exe_name if exe_name in files else 'python.exe')
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

def is_python_version_compatible(python_exe):
    """Check if Python version is compatible (3.8-3.13)."""
    try:
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

def check_python():
    """Check if Python is installed and return version info."""
    python_exe = find_python_executable()
    if not python_exe:
        return False, None, None
    
    try:
        result = subprocess.run([python_exe, '--version'], 
                              capture_output=True, text=True, timeout=5)
        version_str = result.stdout.strip()
        is_compatible = is_python_version_compatible(python_exe)
        return True, version_str, is_compatible
    except:
        return False, None, None

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    default_path = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    if os.path.exists(default_path):
        return True, default_path
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "tesseract"
    except:
        pass
    return False, None

def find_tesseract_tessdata():
    """Find the Tesseract tessdata directory."""
    tesseract_paths = [
        r"C:\\Program Files\\Tesseract-OCR\\tessdata",
        r"C:\\Program Files (x86)\\Tesseract-OCR\\tessdata",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            return path
    return None

def check_japanese_lang_pack():
    """Check if Japanese language pack is installed."""
    tessdata_dir = find_tesseract_tessdata()
    if not tessdata_dir:
        return False
    jpn_file = os.path.join(tessdata_dir, "jpn.traineddata")
    jpn_vert_file = os.path.join(tessdata_dir, "jpn_vert.traineddata")
    return os.path.exists(jpn_file) and os.path.exists(jpn_vert_file)

def download_japanese_lang_pack(log_callback=None):
    """Download Japanese language pack for Tesseract with multiple fallbacks.
    
    Args:
        log_callback: Optional function to call for logging messages (takes a string)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    tessdata_dir = find_tesseract_tessdata()
    if not tessdata_dir:
        return False, "Tesseract tessdata directory not found"
    
    urls = {{
        "jpn.traineddata": "https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata",
        "jpn_vert.traineddata": "https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata",
    }}
    
    import ssl
    import shutil
    
    log("Downloading Japanese language packs for Tesseract...")
    log("Note: Japanese packs are required for reliable Sekiro detection (Japanese '死' character)")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Download files to temp directory first (no admin needed)
        files_to_download = []
        for filename, url in urls.items():
            target_file = os.path.join(tessdata_dir, filename)
            if not os.path.exists(target_file):
                files_to_download.append((filename, url))
        
        if not files_to_download:
            log("Japanese language packs already installed.")
            return True, "Japanese pack already installed"
        
        # Attempt 1: Standard urllib with SSL verification
        log("Attempt 1: Downloading to temp with standard SSL verification...")
        attempt1_success = {{}}
        for filename, url in files_to_download:
            temp_file = os.path.join(temp_dir, filename)
            try:
                import urllib.request
                # Use urlopen for better compatibility
                with urllib.request.urlopen(url) as response:
                    with open(temp_file, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                attempt1_success[filename] = True
            except Exception as e1:
                attempt1_success[filename] = False
                log(f"Attempt 1 failed for {{filename}}: {{e1}}")
        
        # If attempt 1 failed for any files, try attempt 2
        failed_files = [f for f, success in attempt1_success.items() if not success]
        if failed_files:
            attempt_num = 2
            log(f"Attempt {{attempt_num}}: Downloading to temp with relaxed SSL (ignoring certificate validation)...")
            attempt2_success = {{}}
            for filename, url in files_to_download:
                if filename in failed_files:
                    temp_file = os.path.join(temp_dir, filename)
                    try:
                        # Use urlopen with context instead of urlretrieve (more compatible)
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        with urllib.request.urlopen(url, context=ssl_context) as response:
                            with open(temp_file, 'wb') as out_file:
                                shutil.copyfileobj(response, out_file)
                        attempt2_success[filename] = True
                    except Exception as e2:
                        attempt2_success[filename] = False
                        log(f"Attempt {{attempt_num}} failed for {{filename}}: {{e2}}")
                        # Attempt 3: PowerShell Invoke-WebRequest with -SkipCertificateCheck (non-elevated)
                        attempt_num = 3
                        log(f"Attempt {{attempt_num}}: Downloading with PowerShell (bypassing certificate check)...")
                        try:
                            ps_cmd = f'Invoke-WebRequest -Uri "{{url}}" -OutFile "{{temp_file}}" -SkipCertificateCheck'
                            result = subprocess.run(
                                ['powershell', '-Command', ps_cmd],
                                capture_output=True,
                                timeout=60
                            )
                            if result.returncode == 0 and os.path.exists(temp_file):
                                attempt2_success[filename] = True
                            else:
                                attempt2_success[filename] = False
                                log(f"Attempt {{attempt_num}} failed for {{filename}}: PowerShell returned code {{result.returncode}}")
                                # Attempt 4: Elevated PowerShell download (downloads to temp, then copies)
                                attempt_num = 4
                                log(f"Attempt {{attempt_num}}: Downloading with elevated PowerShell (staged download)...")
                                try:
                                    # Download to temp with elevated PowerShell
                                    ps_cmd = f'Start-Process powershell -ArgumentList "-Command", "Invoke-WebRequest -Uri \\'{{url}}\\' -OutFile \\'{{temp_file}}\\' -SkipCertificateCheck" -Verb RunAs -Wait'
                                    result = subprocess.run(
                                        ['powershell', '-Command', ps_cmd],
                                        capture_output=True,
                                        timeout=90
                                    )
                                    if result.returncode == 0 and os.path.exists(temp_file):
                                        attempt2_success[filename] = True
                                    else:
                                        attempt2_success[filename] = False
                                        log(f"Attempt {{attempt_num}} failed for {{filename}}: Elevated PowerShell returned code {{result.returncode}}")
                                except Exception as e4:
                                    attempt2_success[filename] = False
                                    log(f"Attempt {{attempt_num}} failed for {{filename}}: {{e4}}")
                        except Exception as e3:
                            attempt2_success[filename] = False
                            log(f"Attempt {{attempt_num}} failed for {{filename}}: {{e3}}")
                else:
                    attempt2_success[filename] = True  # Already downloaded in attempt 1
            
            # Check if all files downloaded successfully
            all_success = all(attempt2_success.get(f, False) for f, _ in files_to_download)
            if all_success:
                log(f"Downloaded to temp successfully (Attempt 2 - unverified SSL)")
            else:
                failed = [f for f, success in attempt2_success.items() if not success]
                return False, f"Failed to download: {{', '.join(failed)}}"
        else:
            # All files downloaded in attempt 1
            log("Downloaded to temp successfully (Attempt 1 - standard SSL)")
        
        # Copy files from temp to tessdata (may need elevation)
        log("Attempting elevated copy (UAC prompt) to install Japanese packs...")
        elevation_used = False
        for filename in urls.keys():
            temp_file = os.path.join(temp_dir, filename)
            target_file = os.path.join(tessdata_dir, filename)
            
            if not os.path.exists(temp_file):
                continue
            
            try:
                shutil.copy2(temp_file, target_file)
            except PermissionError:
                # Attempt elevated PowerShell copy
                elevation_used = True
                try:
                    ps_cmd = f'Start-Process powershell -ArgumentList "-Command", "Copy-Item -Path \\'{{temp_file}}\\' -Destination \\'{{target_file}}\\' -Force" -Verb RunAs -Wait'
                    result = subprocess.run(
                        ['powershell', '-Command', ps_cmd],
                        capture_output=True,
                        timeout=30
                    )
                    if not os.path.exists(target_file):
                        return False, f"Permission denied copying {{filename}}"
                except Exception as e:
                    return False, f"Permission denied copying {{filename}}: {{e}}"
        
        if elevation_used:
            log("Japanese language packs installed via elevated copy. Sekiro detection is now fully supported!")
        
        log("Japanese pack downloaded successfully! Sekiro detection is now fully supported!")
        return True, "Japanese pack downloaded successfully"
    
    except Exception as e:
        log(f"Error during download: {{e}}")
        return False, str(e)
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

def install_dependencies():
    """Install Python dependencies."""
    python_exe = find_python_executable()
    if not python_exe:
        return False
    
    try:
        packages = ['mss', 'pillow', 'pytesseract', 'opencv-python', 'numpy', 'psutil']
        subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=False, capture_output=True)
        subprocess.run([python_exe, '-m', 'pip', 'install'] + packages, 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Death Counter - Installer & Launcher")
        self.root.geometry("850x650")
        self.root.resizable(False, False)
        
        self.setup_complete = False
        self.streamerbot_imported = False
        self.create_ui()
        self.check_system()
    
    def create_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title = ttk.Label(main_frame, text="Death Counter", 
                         font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        status_frame = ttk.LabelFrame(main_frame, text="System Check", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.python_status = ttk.Label(status_frame, text="Checking Python...")
        self.python_status.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.tesseract_status = ttk.Label(status_frame, text="Checking Tesseract OCR...")
        self.tesseract_status.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.deps_status = ttk.Label(status_frame, text="Checking dependencies...")
        self.deps_status.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.japanese_pack_status = ttk.Label(status_frame, text="Checking Japanese pack...")
        self.japanese_pack_status.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # First row of buttons
        button_frame1 = ttk.Frame(main_frame)
        button_frame1.grid(row=3, column=0, columnspan=2, pady=(0, 5))
        
        self.install_button = ttk.Button(button_frame1, text="Install/Update Files", 
                                         command=self.install_files, width=22)
        self.install_button.pack(side=tk.LEFT, padx=3)
        
        self.install_python_button = ttk.Button(button_frame1, text="Install Python", 
                                               command=self.install_python, width=22)
        self.install_python_button.pack(side=tk.LEFT, padx=3)
        
        self.install_tesseract_button = ttk.Button(button_frame1, text="Install Tesseract", 
                                                   command=self.install_tesseract, width=22)
        self.install_tesseract_button.pack(side=tk.LEFT, padx=3)
        
        self.install_deps_button = ttk.Button(button_frame1, text="Install Dependencies", 
                                              command=self.install_deps, width=22)
        self.install_deps_button.pack(side=tk.LEFT, padx=3)
        
        # Second row of buttons
        button_frame2 = ttk.Frame(main_frame)
        button_frame2.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        self.streamerbot_download_button = ttk.Button(button_frame2, text="Streamer.bot Download", 
                                                      command=self.download_streamerbot, width=22)
        self.streamerbot_download_button.pack(side=tk.LEFT, padx=3)
        
        self.streamerbot_import_button = ttk.Button(button_frame2, text="Import to Streamer.bot", 
                                                    command=self.import_streamerbot, width=22)
        self.streamerbot_import_button.pack(side=tk.LEFT, padx=3)
        
        self.confirm_import_button = ttk.Button(button_frame2, text="✓ Confirm Import", 
                                                command=self.confirm_import, width=22, state=tk.DISABLED)
        self.confirm_import_button.pack(side=tk.LEFT, padx=3)
        
        self.launch_button = ttk.Button(button_frame2, text="Launch Death Counter", 
                                       command=self.launch_app, width=22, state=tk.DISABLED)
        self.launch_button.pack(side=tk.LEFT, padx=3)
        
        info_text = ("1. Click 'Install/Update Files' to extract all files (auto-downloads Japanese pack for Sekiro)\\n"
                    "2. Click 'Install Dependencies' to install Python packages\\n"
                    "3. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki\\n"
                    "4. Click 'Streamer.bot Download' to download and install Streamer.bot (optional)\\n"
                    "5. Click 'Import to Streamer.bot' and import the action file, then click 'Confirm Import' (optional)\\n"
                    "6. Click 'Launch Death Counter' to start")
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=5, column=0, columnspan=2, sticky=tk.W)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def check_system(self):
        python_ok, python_version, is_compatible = check_python()
        if python_ok:
            if is_compatible:
                self.python_status.config(text=f"✓ Python: {{python_version}}", foreground="green")
            else:
                self.python_status.config(text=f"⚠ Python: {{python_version}} (Requires 3.8-3.13)", foreground="orange")
                messagebox.showwarning("Python Version Warning", 
                    f"Your Python version ({{python_version}}) may not be fully compatible.\\n\\n"
                    "This application requires Python 3.8-3.13 for optimal compatibility.\\n\\n"
                    "Please install a compatible Python version from:\\n"
                    "https://www.python.org/downloads/\\n\\n"
                    "The application may still work, but some features may not function correctly.")
        else:
            self.python_status.config(text="✗ Python not found", foreground="red")
        
        tesseract_ok, tesseract_path = check_tesseract()
        if tesseract_ok:
            self.tesseract_status.config(text="✓ Tesseract OCR: Found", foreground="green")
            # Check Japanese pack if Tesseract is found
            try:
                if check_japanese_lang_pack():
                    self.japanese_pack_status.config(text="✓ Japanese Pack: Installed (Sekiro support)", foreground="green")
                else:
                    self.japanese_pack_status.config(text="⚠ Japanese Pack: Not found (auto-download on install)", foreground="orange")
            except Exception as e:
                self.japanese_pack_status.config(text="⚠ Japanese Pack: Error checking status", foreground="orange")
                self.log(f"Error checking Japanese pack: {{e}}")
        else:
            self.tesseract_status.config(text="✗ Tesseract OCR: Not found (install from link below)", foreground="orange")
            self.japanese_pack_status.config(text="⚠ Japanese Pack: Tesseract required", foreground="gray")
        
        try:
            import mss
            import cv2
            import pytesseract
            import psutil
            self.deps_status.config(text="✓ Dependencies: Installed", foreground="green")
        except ImportError:
            self.deps_status.config(text="✗ Dependencies: Not installed", foreground="red")
        
        gui_path = os.path.join(INSTALL_DIR, "death_counter_gui.py")
        cs_file_path = os.path.join(INSTALL_DIR, "deathcounteraction.cs")
        if os.path.exists(gui_path):
            self.setup_complete = True
            if os.path.exists(cs_file_path):
                self.log("Files already installed. Import to Streamer.bot to enable launch button.")
                # Enable Confirm Import button if action file exists
                self.confirm_import_button.config(state=tk.NORMAL)
            else:
                self.log("Files already installed. Ready to launch!")
                self.update_launch_button_state()
        else:
            self.log("Files not yet installed. Click 'Install/Update Files' first.")
    
    def update_launch_button_state(self):
        """Update launch button state based on setup completion and Streamer.bot import status."""
        if self.setup_complete:
            if self.streamerbot_imported:
                self.launch_button.config(state=tk.NORMAL)
            else:
                cs_file_path = os.path.join(INSTALL_DIR, "deathcounteraction.cs")
                if not os.path.exists(cs_file_path):
                    # If no Streamer.bot action file, allow launch without import
                    self.launch_button.config(state=tk.NORMAL)
                else:
                    # Action file exists, require import confirmation
                    self.launch_button.config(state=tk.DISABLED)
    
    def install_python(self):
        """Open Python download page."""
        self.log("Opening Python download page...")
        webbrowser.open("https://www.python.org/downloads/")
        self.log("Python download page opened. After installing, restart this installer.")
        messagebox.showinfo("Python Installation", 
                          "After installing Python, please:\\n"
                          "1. Check 'Add Python to PATH' during installation\\n"
                          "2. Restart this installer")
    
    def install_tesseract(self):
        """Open Tesseract OCR download page."""
        self.log("Opening Tesseract OCR download page...")
        webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")
        self.log("Tesseract OCR download page opened.")
        messagebox.showinfo("Tesseract OCR Installation", 
                          "Default install path: C:\\\\Program Files\\\\Tesseract-OCR\\\\\\n"
                          "After installing, restart this installer.")
    
    def download_streamerbot(self):
        """Open Streamer.bot download page."""
        self.log("Opening Streamer.bot download page...")
        webbrowser.open("https://streamer.bot/")
        self.log("Streamer.bot download page opened.")
    
    def import_streamerbot(self):
        """Open file location for Streamer.bot action file."""
        cs_file_path = os.path.join(INSTALL_DIR, "deathcounteraction.cs")
        if not os.path.exists(cs_file_path):
            self.log("Action file not found. Please install files first.")
            messagebox.showerror("Error", 
                               "The action file has not been extracted yet.\\n\\n"
                               "Please click 'Install/Update Files' first to extract all files.")
            return
        
        # Open the file location in Explorer
        try:
            subprocess.Popen(f'explorer /select,"{{cs_file_path}}"')
            self.log("Opened file location: {{cs_file_path}}")
            self.log("Streamer.bot import instructions displayed.")
            # Enable the Confirm Import button after showing instructions
            self.confirm_import_button.config(state=tk.NORMAL)
            messagebox.showinfo("Import to Streamer.bot", 
                              "1. In Streamer.bot, go to Actions\\n"
                              "2. Click 'Import'\\n"
                              "3. Select the deathcounteraction.cs file\\n"
                              "4. After importing, click 'Confirm Import' button")
        except Exception as e:
            self.log(f"Error opening file location: {{e}}")
            messagebox.showerror("Error", f"Could not open file location: {{e}}")
    
    def confirm_import(self):
        """Confirm that Streamer.bot action has been imported."""
        self.streamerbot_imported = True
        self.confirm_import_button.config(state=tk.DISABLED)
        self.update_launch_button_state()
        self.log("Streamer.bot import confirmed! Launch button enabled.")
        messagebox.showinfo("Import Confirmed", "Streamer.bot import confirmed. You can now launch the Death Counter!")
    
    def install_files(self):
        self.log("Installing files...")
        self.install_button.config(state=tk.DISABLED)
        
        def do_install():
            try:
                extracted = extract_files()
                self.log(f"Extracted {{len(extracted)}} files successfully!")
                
                # Auto-download Japanese pack if Tesseract is found and pack is missing
                tesseract_ok, _ = check_tesseract()
                if tesseract_ok:
                    if not check_japanese_lang_pack():
                        self.log("Japanese language pack not found. Attempting auto-download...")
                        self.log("Note: Japanese pack is required for reliable Sekiro detection (Japanese '死' character)")
                        success, message = download_japanese_lang_pack(log_callback=self.log)
                        if success:
                            self.japanese_pack_status.config(text="✓ Japanese Pack: Installed (Sekiro support)", foreground="green")
                        else:
                            self.log(f"Japanese pack auto-download failed. Manual download recommended for Sekiro.")
                            self.log("Download from:")
                            self.log("  https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata")
                            self.log("  https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata")
                            self.log(f"Save to: {{find_tesseract_tessdata() or 'Tesseract tessdata directory'}}")
                            self.japanese_pack_status.config(text="⚠ Japanese Pack: Auto-download failed", foreground="orange")
                    else:
                        self.log("Japanese language pack already installed.")
                
                self.setup_complete = True
                self.update_launch_button_state()
            except Exception as e:
                self.log(f"Error installing files: {{e}}")
                messagebox.showerror("Error", f"Failed to install files: {{e}}")
            finally:
                self.install_button.config(state=tk.NORMAL)
        
        threading.Thread(target=do_install, daemon=True).start()
    
    def install_deps(self):
        self.log("Installing dependencies...")
        self.install_deps_button.config(state=tk.DISABLED)
        
        def do_install():
            try:
                if install_dependencies():
                    self.log("Dependencies installed successfully!")
                    self.check_system()
                else:
                    self.log("Failed to install dependencies.")
                    messagebox.showerror("Error", "Failed to install dependencies.")
            except Exception as e:
                self.log(f"Error: {{e}}")
                messagebox.showerror("Error", f"Failed to install dependencies: {{e}}")
            finally:
                self.install_deps_button.config(state=tk.NORMAL)
        
        threading.Thread(target=do_install, daemon=True).start()
    
    def launch_app(self):
        gui_path = os.path.join(INSTALL_DIR, "death_counter_gui.py")
        if not os.path.exists(gui_path):
            messagebox.showerror("Error", "Death Counter GUI not found. Please install files first.")
            return
        
        try:
            # Find pythonw.exe (no console window) for GUI applications
            python_exe = find_python_executable(use_pythonw=True)
            if not python_exe:
                error_msg = "Python executable not found. Please install Python and ensure it's in PATH."
                self.log(error_msg)
                messagebox.showerror("Error", error_msg)
                return
            
            self.log(f"Launching: {{python_exe}} {{gui_path}}")
            self.log(f"Working directory: {{INSTALL_DIR}}")
            
            # Launch with CREATE_NO_WINDOW to hide console window
            # Use pythonw.exe which doesn't create a console window
            CREATE_NO_WINDOW = 0x08000000 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            process = subprocess.Popen(
                [python_exe, gui_path], 
                cwd=INSTALL_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=CREATE_NO_WINDOW  # Hide console window
            )
            
            # Give it a moment to start, then check if it's still running
            import time
            time.sleep(0.5)
            
            if process.poll() is None:
                # Process is still running (good)
                self.log("Death Counter launched successfully!")
                messagebox.showinfo("Success", "Death Counter GUI launched!")
            else:
                # Process exited immediately (error)
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                self.log(f"Process exited immediately. Error: {{error_msg}}")
                messagebox.showerror("Error", f"Death Counter failed to start:\\n{{error_msg}}")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log(f"Error launching: {{e}}")
            self.log(f"Details: {{error_details}}")
            messagebox.showerror("Error", f"Failed to launch: {{e}}")

def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
    
    # Format the embedded files dictionary
    embedded_files_str = json.dumps(embedded_files, indent=2)
    
    # Replace placeholder
    installer_code = installer_template.replace('{embedded_files_dict}', embedded_files_str)
    installer_code = installer_code.replace('{{', '{').replace('}}', '}')
    
    # Write the installer
    output_path = os.path.join(script_dir, "DeathCounter_Installer_Standalone.py")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(installer_code)
    
    print(f"\nCreated standalone installer: {output_path}")
    print("\nTo create a single .exe file, run:")
    print("  pip install pyinstaller")
    print(f"  pyinstaller --onefile --windowed --name DeathCounterInstaller {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_embedded_installer()

