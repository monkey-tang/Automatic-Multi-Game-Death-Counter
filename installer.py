"""
Death Counter Installer
Single EXE installer that handles everything - extracts files, installs dependencies, creates shortcuts
"""

import os
import sys
import json
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Get the temporary directory where installer is running from
if getattr(sys, 'frozen', False):
    INSTALLER_DIR = os.path.dirname(sys.executable)
else:
    INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))

# Embedded files (will be extracted)
EMBEDDED_FILES = {
    "multi_game_death_counter.py": "multi_game_death_counter.py",
    "death_counter_gui.py": "death_counter_gui.py",
    "death_counter_settings.py": "death_counter_settings.py",
    "log_monitor.py": "log_monitor.py",
    "memory_scanner.py": "memory_scanner.py",
    "games_config.json": "games_config.json",
    "reset_death_counter.py": "reset_death_counter.py",
    "switch_game_manual.py": "switch_game_manual.py",
    "capture_debug_once.py": "capture_debug_once.py",
    "change_monitor_id.py": "change_monitor_id.py",
    "requirements.txt": "requirements.txt",
    "README.md": "README.md",
    "FUZZY_MATCHING_GUIDE.md": "FUZZY_MATCHING_GUIDE.md",
}

# Batch files to create
BATCH_FILES = {
    "START_DEATH_COUNTER.bat": """@echo off
REM Start Death Counter Daemon
cd /d "%~dp0"
python multi_game_death_counter.py
pause
""",
    "STOP_DEATH_COUNTER.bat": """@echo off
REM Stop Death Counter Daemon
cd /d "%~dp0"
echo. > STOP
timeout /t 2 /nobreak >nul
if exist daemon.lock (
    for /f "tokens=*" %%i in (daemon.lock) do (
        taskkill /F /PID %%i >nul 2>&1
    )
    del daemon.lock >nul 2>&1
)
if exist STOP del STOP >nul 2>&1
pause
""",
    "RESET_DEATH_COUNTER.bat": """@echo off
REM Reset Death Counter
cd /d "%~dp0"
python reset_death_counter.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
""",
    "CAPTURE_DEBUG.bat": """@echo off
REM Capture debug images
cd /d "%~dp0"
python capture_debug_once.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
""",
    "CHANGE_MONITOR_ID.bat": """@echo off
REM Change monitor ID
cd /d "%~dp0"
python change_monitor_id.py
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
""",
}


class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Death Counter Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
        
        self.install_dir = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), 'Desktop', 'DeathCounter')
        self.installing = False
        
        self.create_ui()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Death Counter Installer", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Welcome text
        welcome_text = """Welcome to the Death Counter Installer!

This installer will:
• Extract all necessary files
• Install Python dependencies (if needed)
• Set up configuration files
• Create shortcuts

Click 'Browse' to choose installation location, then click 'Install'."""
        
        welcome_label = ttk.Label(main_frame, text=welcome_text, justify=tk.LEFT, wraplength=550)
        welcome_label.pack(pady=(0, 20))
        
        # Installation directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Installation Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X)
        
        self.dir_var = tk.StringVar(value=self.install_dir)
        dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(dir_entry_frame, text="Browse...", command=self.browse_directory, width=15)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.create_shortcut_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create desktop shortcut", variable=self.create_shortcut_var).pack(anchor=tk.W)
        
        self.install_deps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Install Python dependencies automatically", variable=self.install_deps_var).pack(anchor=tk.W)
        
        self.check_tesseract_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Check for Tesseract OCR installation", variable=self.check_tesseract_var).pack(anchor=tk.W)
        
        # Progress
        self.progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready to install...", font=("Arial", 9))
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.log_text = tk.Text(self.progress_frame, height=8, width=60, wrap=tk.WORD, font=("Consolas", 8))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.progress_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.install_btn = ttk.Button(button_frame, text="Install", command=self.start_installation, width=20)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=20)
        self.cancel_btn.pack(side=tk.LEFT)
        
        self.close_btn = ttk.Button(button_frame, text="Close", command=self.root.quit, width=20, state=tk.DISABLED)
        self.close_btn.pack(side=tk.RIGHT)
    
    def browse_directory(self):
        if self.installing:
            return
        
        directory = filedialog.askdirectory(initialdir=self.install_dir, title="Select Installation Directory")
        if directory:
            self.install_dir = directory
            self.dir_var.set(directory)
    
    def log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message, progress=None):
        """Update status label and progress bar."""
        self.status_label.config(text=message)
        if progress is not None:
            self.progress_bar['value'] = progress
        self.root.update_idletasks()
    
    def start_installation(self):
        """Start installation in a separate thread."""
        if self.installing:
            return
        
        self.install_dir = self.dir_var.get().strip()
        if not self.install_dir:
            messagebox.showerror("Error", "Please select an installation directory.")
            return
        
        # Validate installation directory
        try:
            # Check if path is valid
            if not os.path.isabs(self.install_dir):
                messagebox.showerror("Error", "Please provide an absolute path for the installation directory.")
                return
            
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(self.install_dir)
            # Only check parent if it's different from install_dir (not a root directory)
            if parent_dir and parent_dir != self.install_dir:
                if not os.path.exists(parent_dir):
                    messagebox.showerror("Error", f"Parent directory does not exist: {parent_dir}")
                    return
                
                if not os.access(parent_dir, os.W_OK):
                    messagebox.showerror("Error", f"No write permission for: {parent_dir}")
                    return
        except Exception as e:
            messagebox.showerror("Error", f"Invalid installation directory: {e}")
            return
        
        # Disable install button
        self.install_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        self.installing = True
        
        # Start installation thread
        thread = threading.Thread(target=self.install, daemon=True)
        thread.start()
    
    def install(self):
        """Perform installation."""
        try:
            self.log("=" * 60)
            self.log("Death Counter Installation Starting...")
            self.log("=" * 60)
            self.update_status("Preparing installation...", 5)
            
            # Create installation directory
            self.log(f"\nCreating installation directory: {self.install_dir}")
            try:
                os.makedirs(self.install_dir, exist_ok=True)
                
                # Verify directory was created and is writable
                if not os.path.exists(self.install_dir):
                    raise Exception(f"Failed to create directory: {self.install_dir}")
                
                if not os.access(self.install_dir, os.W_OK):
                    raise Exception(f"Directory is not writable: {self.install_dir}")
                
                self.update_status("Directory created", 10)
            except Exception as e:
                self.log(f"  ✗ Failed to create installation directory: {e}")
                raise
            
            # Extract embedded files
            self.log("\nExtracting files...")
            self.update_status("Extracting files...", 15)
            
            files_extracted = 0
            total_files = len(EMBEDDED_FILES)
            
            # Get the resource path (handles both script and PyInstaller bundle)
            def resource_path(relative_path):
                """Get absolute path to resource, works for dev and for PyInstaller"""
                if getattr(sys, 'frozen', False):
                    # Running as compiled EXE - PyInstaller creates a temp folder and stores path in _MEIPASS
                    try:
                        base_path = sys._MEIPASS
                    except AttributeError:
                        # Fallback if _MEIPASS doesn't exist
                        base_path = INSTALLER_DIR
                else:
                    # Running as script
                    base_path = INSTALLER_DIR
                
                # PyInstaller with --add-data puts files in the base_path directly (not in subdirectories)
                # The format is: --add-data "file;." which puts file in base_path
                full_path = os.path.join(base_path, relative_path)
                return full_path
            
            for source_name, dest_name in EMBEDDED_FILES.items():
                dest_path = os.path.join(self.install_dir, dest_name)
                
                try:
                    # Try to get file from resource path
                    source_path = resource_path(source_name)
                    
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, dest_path)
                        self.log(f"  ✓ {dest_name}")
                        files_extracted += 1
                    else:
                        # Try alternative locations (for development/testing)
                        # Use INSTALLER_DIR as base since we're already in that context
                        alt_paths = [
                            os.path.join(INSTALLER_DIR, source_name),
                            os.path.join(os.path.dirname(INSTALLER_DIR), source_name),
                        ]
                        
                        # Try to get script directory if running as script (not frozen)
                        if not getattr(sys, 'frozen', False):
                            try:
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                if script_dir and script_dir != INSTALLER_DIR:
                                    alt_paths.append(os.path.join(script_dir, source_name))
                            except:
                                pass
                        
                        found = False
                        for alt_path in alt_paths:
                            if alt_path and os.path.exists(alt_path):
                                try:
                                    shutil.copy2(alt_path, dest_path)
                                    self.log(f"  ✓ {dest_name} (from alternative location)")
                                    files_extracted += 1
                                    found = True
                                    break
                                except Exception as e:
                                    self.log(f"  ⚠ Failed to copy from {alt_path}: {e}")
                        
                        if not found:
                            # This is a critical error - log it but continue
                            self.log(f"  ✗ {dest_name} - File not found in bundle")
                            self.log(f"     Searched: {source_path}")
                            if os.path.exists(source_path):
                                self.log(f"     File exists but may not be readable")
                            # Continue installation - some files may be optional
                            
                except Exception as e:
                    self.log(f"  ✗ {dest_name}: {e}")
            
            # Calculate progress (handle division by zero)
            if total_files > 0:
                progress = 15 + int((files_extracted / total_files) * 30)
            else:
                progress = 45
            self.update_status(f"Extracted {files_extracted}/{total_files} files", progress)
            
            # Warn if too many files are missing
            if files_extracted < total_files * 0.7:  # Less than 70% extracted
                self.log(f"\n  ⚠ WARNING: Only {files_extracted}/{total_files} files extracted")
                self.log("  Installation may not work correctly.")
            
            # Warn if critical files are missing
            critical_files = ["multi_game_death_counter.py", "death_counter_gui.py", "games_config.json"]
            missing_critical = []
            for critical_file in critical_files:
                dest_path = os.path.join(self.install_dir, critical_file)
                if not os.path.exists(dest_path):
                    missing_critical.append(critical_file)
            
            if missing_critical:
                self.log(f"\n  ⚠ WARNING: Critical files are missing: {missing_critical}")
                self.log("  Installation may not work correctly.")
                self.log("  Please ensure all files were extracted properly.")
            
            # Create batch files
            self.log("\nCreating batch files...")
            self.update_status("Creating batch files...", 50)
            
            for batch_name, batch_content in BATCH_FILES.items():
                batch_path = os.path.join(self.install_dir, batch_name)
                try:
                    with open(batch_path, 'w', encoding='utf-8') as f:
                        f.write(batch_content)
                    self.log(f"  ✓ {batch_name}")
                except Exception as e:
                    self.log(f"  ✗ {batch_name}: {e}")
            
            self.update_status("Batch files created", 55)
            
            # Check for Python
            self.log("\nChecking Python installation...")
            self.update_status("Checking Python...", 60)
            
            python_exe = self.find_python()
            if not python_exe:
                self.log("  ⚠ Python not found!")
                self.log("  Files have been extracted, but Python is required to run the application.")
                self.log("  Please install Python 3.8-3.12 from python.org")
                self.log("  Dependencies cannot be installed without Python.")
                self.update_status("Python not found - Files extracted", 85)
                # Don't return - continue with installation, just skip dependency installation
                # The user can install Python later and run the application
            else:
                self.log(f"  ✓ Python found: {python_exe}")
                self.update_status("Python found", 65)
            
            # Install dependencies if requested (only if Python is found)
            if python_exe and self.install_deps_var.get():
                self.log("\nInstalling Python dependencies...")
                self.update_status("Installing dependencies...", 70)
                
                requirements_file = os.path.join(self.install_dir, "requirements.txt")
                if os.path.exists(requirements_file):
                    try:
                        self.log("  Running: pip install -r requirements.txt")
                        self.log("  This may take a few minutes...")
                        
                        # Update pip first
                        try:
                            subprocess.run(
                                [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                        except:
                            pass  # Ignore pip upgrade errors
                        
                        result = subprocess.run(
                            [python_exe, "-m", "pip", "install", "-r", requirements_file],
                            capture_output=True,
                            text=True,
                            timeout=600  # 10 minute timeout
                        )
                        if result.returncode == 0:
                            self.log("  ✓ Dependencies installed successfully")
                        else:
                            self.log(f"  ⚠ Some dependencies may have failed to install")
                            if result.stderr:
                                error_lines = result.stderr.split('\n')[:5]
                                for line in error_lines:
                                    if line.strip():
                                        self.log(f"    {line[:100]}")
                            if result.stdout:
                                # Check for success messages in stdout
                                if "Successfully installed" in result.stdout:
                                    self.log("  ✓ Some packages installed successfully")
                    except subprocess.TimeoutExpired:
                        self.log("  ⚠ Dependency installation timed out (this is normal if packages are large)")
                        self.log("  You can install dependencies manually later with: pip install -r requirements.txt")
                    except Exception as e:
                        self.log(f"  ⚠ Failed to install dependencies: {e}")
                        self.log("  You can install dependencies manually later with: pip install -r requirements.txt")
                else:
                    self.log("  ⚠ requirements.txt not found, skipping dependency installation")
            elif not python_exe:
                self.log("  ⚠ Skipping dependency installation (Python not found)")
            
            if python_exe:
                self.update_status("Dependencies installed", 85)
            else:
                self.update_status("Python check complete", 85)
            
            # Check Tesseract if requested
            if self.check_tesseract_var.get():
                self.log("\nChecking Tesseract OCR...")
                self.update_status("Checking Tesseract OCR...", 90)
                
                tesseract_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                ]
                
                tesseract_found = False
                for path in tesseract_paths:
                    if os.path.exists(path):
                        self.log(f"  ✓ Tesseract found: {path}")
                        tesseract_found = True
                        break
                
                if not tesseract_found:
                    self.log("  ⚠ Tesseract OCR not found")
                    self.log("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
                    self.log("  Default installation path: C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
            
            self.update_status("Installation checks complete", 95)
            
            # Create shortcut if requested
            if self.create_shortcut_var.get():
                self.log("\nCreating desktop shortcut...")
                try:
                    desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
                    if not os.path.exists(desktop):
                        # Try alternative desktop paths
                        alt_desktop = os.path.join(os.environ.get('PUBLIC', ''), 'Desktop')
                        if os.path.exists(alt_desktop):
                            desktop = alt_desktop
                        else:
                            raise Exception("Desktop directory not found")
                    
                    shortcut_path = os.path.join(desktop, "DeathCounter.lnk")
                    gui_script = os.path.join(self.install_dir, "death_counter_gui.py")
                    
                    if not os.path.exists(gui_script):
                        self.log(f"  ⚠ GUI script not found at: {gui_script}")
                        self.log("  Skipping shortcut creation")
                    elif not python_exe:
                        self.log("  ⚠ Cannot create shortcut (Python not found)")
                        self.log("  Install Python and manually create shortcut if needed")
                    else:
                        if self.create_shortcut(shortcut_path, gui_script, python_exe, "Death Counter"):
                            self.log("  ✓ Desktop shortcut created")
                        else:
                            self.log("  ⚠ Could not create shortcut (fallback batch file created)")
                except Exception as e:
                    self.log(f"  ⚠ Could not create shortcut: {e}")
                    self.log("  You can manually create a shortcut later")
            
            # Create death_state.json if it doesn't exist
            state_file = os.path.join(self.install_dir, "death_state.json")
            if not os.path.exists(state_file):
                try:
                    with open(state_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "total_deaths": 0,
                            "game_deaths": {},
                            "tick": 0,
                            "streak": 0,
                            "last_death_ts": 0.0,
                            "current_game": None
                        }, f, indent=2)
                    self.log("  ✓ Created death_state.json")
                except Exception as e:
                    self.log(f"  ⚠ Could not create state file: {e}")
            
            # Final verification
            self.log("\nVerifying installation...")
            critical_files_check = ["multi_game_death_counter.py", "death_counter_gui.py", "games_config.json"]
            all_critical_present = all(os.path.exists(os.path.join(self.install_dir, f)) for f in critical_files_check)
            
            if all_critical_present:
                self.log("  ✓ All critical files present")
                self.update_status("Installation complete!", 100)
                
                self.log("\n" + "=" * 60)
                self.log("Installation Complete!")
                self.log("=" * 60)
                self.log(f"\nInstallation directory: {self.install_dir}")
                self.log(f"Files extracted: {files_extracted}/{total_files}")
                self.log("\nTo start the Death Counter:")
                self.log("  1. Run 'START_DEATH_COUNTER.bat' to start the daemon")
                self.log("  2. Run 'death_counter_gui.py' to open the GUI")
                self.log("     (or double-click the desktop shortcut)")
                self.log("\nNote: Make sure Tesseract OCR is installed for OCR detection to work.")
                
                messagebox.showinfo(
                    "Installation Complete",
                    f"Death Counter has been installed successfully!\n\n"
                    f"Installation directory: {self.install_dir}\n\n"
                    "To start:\n"
                    "• Run START_DEATH_COUNTER.bat to start the daemon\n"
                    "• Run death_counter_gui.py (or use the desktop shortcut) to open the GUI\n\n"
                    "Note: Tesseract OCR must be installed separately for OCR detection."
                )
            else:
                self.log("  ⚠ Some critical files are missing!")
                self.update_status("Installation incomplete - some files missing", 95)
                
                missing = [f for f in critical_files_check if not os.path.exists(os.path.join(self.install_dir, f))]
                warning_msg = (
                    f"Installation completed with warnings.\n\n"
                    f"Some critical files are missing: {', '.join(missing)}\n\n"
                    f"Installation directory: {self.install_dir}\n\n"
                    "The installation may not work correctly. Please check the log for details."
                )
                messagebox.showwarning("Installation Warning", warning_msg)
            
            # Enable close button
            self.cancel_btn.config(state=tk.DISABLED)
            self.close_btn.config(state=tk.NORMAL)
            self.installing = False
            
        except Exception as e:
            self.log(f"\n✗ Installation failed: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.update_status("Installation failed", 100)
            messagebox.showerror("Installation Failed", f"Installation failed:\n\n{e}")
            self.install_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.NORMAL)
            self.close_btn.config(state=tk.NORMAL)
            self.installing = False
    
    def find_python(self):
        """Find Python executable."""
        # Try 'python' command
        try:
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'python'
        except:
            pass
        
        # Try 'py' launcher
        try:
            result = subprocess.run(['py', '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'py'
        except:
            pass
        
        # Check common paths
        common_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python'),
            r"C:\Python312",
            r"C:\Python311",
            r"C:\Python310",
        ]
        
        for base in common_paths:
            if os.path.exists(base):
                try:
                    for item in os.listdir(base):
                        item_path = os.path.join(base, item)
                        python_dir = item_path if os.path.isdir(item_path) else base
                        python_exe = os.path.join(python_dir, 'python.exe')
                        if os.path.exists(python_exe):
                            return python_exe
                except (OSError, PermissionError):
                    continue
        
        return None
    
    def create_shortcut(self, shortcut_path, target, python_exe, description):
        """Create a Windows shortcut."""
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = python_exe
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.Description = description
            shortcut.IconLocation = python_exe
            shortcut.save()
            return True
        except:
            # Fallback: create a batch file shortcut
            try:
                batch_content = f'@echo off\ncd /d "{os.path.dirname(target)}"\n"{python_exe}" "{target}"\npause\n'
                with open(shortcut_path.replace('.lnk', '.bat'), 'w', encoding='utf-8') as f:
                    f.write(batch_content)
                return True
            except:
                return False


def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
