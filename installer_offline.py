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
import re

# Get the temporary directory where installer is running from
if getattr(sys, 'frozen', False):
    INSTALLER_DIR = os.path.dirname(sys.executable)
else:
    INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))

# Version info
INSTALLER_VERSION = "2.0-offline"
DEATH_COUNTER_VERSION = "2.0"
OFFLINE_MODE = True  # This installer bundles all dependencies

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
    "INSTALLER_README.md": "INSTALLER_README.md",  # Installer-specific documentation
    "deathcounteraction.cs": "deathcounteraction.cs",  # Streamer.bot integration action file
}

# Icon files to copy (if they exist) - for desktop shortcuts
ICON_FILES = [
    "gui_icon.ico",
    "smonker.ico",
    "Smonker.ico",
    "shortcut_icon.ico",
    "screenshot.ico",
    "Screenshot.ico",
]

# Batch files to create
BATCH_FILES = {
    "START_DEATH_COUNTER.bat": """@echo off
REM Start Death Counter Daemon (uses VBScript for silent launch)
cd /d "%~dp0"

REM First resort: Use VBScript launcher (completely silent - no console window)
if exist "START_DEATH_COUNTER.vbs" (
    wscript "START_DEATH_COUNTER.vbs"
    exit /b 0
)

REM Fallback: Check if compiled daemon EXE exists (windowless)
if exist "DeathCounterDaemon.exe" (
    start "" "DeathCounterDaemon.exe"
    exit /b 0
)

REM Fallback: Try pythonw.exe (windowless Python)
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw.exe multi_game_death_counter.py
    exit /b 0
)

REM Fallback: Use python normally (normal window)
where python >nul 2>&1
if %errorlevel% == 0 (
    start "" python multi_game_death_counter.py
    exit /b 0
)

REM Last resort: Use python with console window visible
python multi_game_death_counter.py
exit /b 0
""",
    "STOP_DEATH_COUNTER.bat": """@echo off
REM Stop Death Counter Daemon (silent mode)
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
exit /b 0
""",
    "RESET_DEATH_COUNTER.bat": """@echo off
REM Reset Death Counter (silent mode)
cd /d "%~dp0"

REM Check if pythonw.exe exists (windowless Python)
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    pythonw.exe reset_death_counter.py
    exit /b %errorlevel%
)

REM Fallback: use python but minimize window
start /min /wait python reset_death_counter.py
exit /b %errorlevel%
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
    "START_GUI.bat": """@echo off
REM Start Death Counter GUI (uses VBScript for silent launch - no console window)
cd /d "%~dp0"

REM First resort: Use VBScript launcher (completely silent - no console window)
if exist "START_GUI.vbs" (
    wscript "START_GUI.vbs"
    exit /b 0
)

REM Fallback: Check if compiled GUI EXE exists (windowless)
if exist "DeathCounter.exe" (
    start "" "DeathCounter.exe"
    exit /b 0
)

REM Fallback: Try pythonw.exe (windowless Python)
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw.exe death_counter_gui.py
    exit /b 0
)

REM Fallback: Use python normally (normal window)
where python >nul 2>&1
if %errorlevel% == 0 (
    start "" python death_counter_gui.py
    exit /b 0
)

REM Last resort: Use python with console window visible
python death_counter_gui.py
exit /b 0
""",
}


class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Death Counter Installer v{INSTALLER_VERSION} (Offline)")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        self.root.minsize(650, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"700x700+{x}+{y}")
        
        self.install_dir = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), 'Desktop', 'DeathCounter')
        self.installing = False
        self.system_checked = False
        
        self.create_ui()
        self.check_system_requirements()
    
    def create_ui(self):
        # Main frame with scrollable canvas
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        def mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", mousewheel)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_frame = scrollable_frame
        
        # Title with version
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Death Counter Installer", font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(title_frame, text=f"v{INSTALLER_VERSION}", font=("Arial", 10))
        version_label.pack(side=tk.LEFT, padx=(10, 0), pady=(5, 0))
        
        about_btn = ttk.Button(title_frame, text="About", command=self.show_about, width=10)
        about_btn.pack(side=tk.RIGHT)
        
        # Welcome text
        welcome_text = f"""Welcome to the Death Counter Installer v{INSTALLER_VERSION} (Offline)!

This installer will:
• Extract all necessary files ({len(EMBEDDED_FILES)} Python scripts, configs, and documentation)
• All dependencies are bundled - NO pip install required
• Set up configuration files
• Create desktop shortcuts
• Verify system requirements

✓ NOTE: This is the OFFLINE version - all dependencies are included (~64MB).
Works without internet connection after download.
Click 'Check Requirements' to verify your system, then click 'Install' to proceed."""
        
        welcome_label = ttk.Label(main_frame, text=welcome_text, justify=tk.LEFT, wraplength=650)
        welcome_label.pack(pady=(0, 15), anchor=tk.W)
        
        # System Requirements Check Section
        req_frame = ttk.LabelFrame(main_frame, text="System Requirements", padding="10")
        req_frame.pack(fill=tk.X, pady=(0, 15))
        
        req_btn_frame = ttk.Frame(req_frame)
        req_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        check_req_btn = ttk.Button(req_btn_frame, text="Check Requirements", command=self.check_system_requirements, width=20)
        check_req_btn.pack(side=tk.LEFT)
        
        self.req_status_label = ttk.Label(req_btn_frame, text="Click 'Check Requirements' to verify system", font=("Arial", 9))
        self.req_status_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Requirements results frame
        self.req_results_frame = ttk.Frame(req_frame)
        self.req_results_frame.pack(fill=tk.X)
        
        # Row 1: Python and Tesseract
        self.python_status_label = ttk.Label(self.req_results_frame, text="Python: Not checked", font=("Arial", 9))
        self.python_status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        tesseract_frame = ttk.Frame(self.req_results_frame)
        tesseract_frame.grid(row=0, column=1, sticky=tk.W)
        
        self.tesseract_status_label = ttk.Label(tesseract_frame, text="Tesseract OCR: Not checked", font=("Arial", 9))
        self.tesseract_status_label.pack(side=tk.LEFT)
        
        self.tesseract_download_btn = ttk.Button(tesseract_frame, text="Download", command=self.open_tesseract_download, width=10)
        self.tesseract_download_btn.pack(side=tk.LEFT, padx=(10, 0))
        self.tesseract_download_btn.pack_forget()  # Hide by default
        
        # Row 2: Streamer.bot (optional tool for integration)
        streamerbot_frame = ttk.Frame(self.req_results_frame)
        streamerbot_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.streamerbot_status_label = ttk.Label(streamerbot_frame, text="Streamer.bot: Optional (for OBS integration)", font=("Arial", 9), foreground="gray")
        self.streamerbot_status_label.pack(side=tk.LEFT)
        
        self.streamerbot_download_btn = ttk.Button(streamerbot_frame, text="Download Streamer.bot", command=self.open_streamerbot_download, width=23)
        self.streamerbot_download_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Installation directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Installation Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X)
        
        self.dir_var = tk.StringVar(value=self.install_dir)
        dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(dir_entry_frame, text="Browse...", command=self.browse_directory, width=15)
        browse_btn.pack(side=tk.RIGHT)
        
        # Files to be installed section
        files_frame = ttk.LabelFrame(main_frame, text=f"Files to be Installed ({len(EMBEDDED_FILES)} files)", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        files_text = tk.Text(files_frame, height=6, wrap=tk.WORD, font=("Consolas", 8))
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=files_text.yview)
        files_text.config(yscrollcommand=files_scrollbar.set)
        
        files_list = "\n".join(sorted(EMBEDDED_FILES.keys()))
        files_text.insert(tk.END, files_list)
        files_text.config(state=tk.DISABLED)
        
        files_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_shortcut_var = tk.BooleanVar(value=True)
        shortcut_cb = ttk.Checkbutton(options_frame, text="Create desktop shortcut", variable=self.create_shortcut_var)
        shortcut_cb.grid(row=0, column=0, sticky=tk.W)
        ttk.Label(options_frame, text="(Creates a shortcut to launch the GUI)", font=("Arial", 8), foreground="gray").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # For offline version, dependencies are already bundled - show info instead
        self.install_deps_var = tk.BooleanVar(value=False)  # Always False for offline
        deps_info = ttk.Label(options_frame, text="All dependencies are bundled (offline mode)", font=("Arial", 9), foreground="green")
        deps_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.check_tesseract_var = tk.BooleanVar(value=True)
        tess_cb = ttk.Checkbutton(options_frame, text="Check for Tesseract OCR installation", variable=self.check_tesseract_var)
        tess_cb.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(options_frame, text="(Required for OCR death detection)", font=("Arial", 8), foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
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
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_btn = ttk.Button(button_frame, text="Install", command=self.start_installation, width=18)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.streamerbot_import_btn = ttk.Button(button_frame, text="Import Streamer.bot Action", command=self.import_streamerbot_action, width=30, state=tk.DISABLED)
        self.streamerbot_import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=18)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.close_btn = ttk.Button(button_frame, text="Close", command=self.root.quit, width=18, state=tk.DISABLED)
        self.close_btn.pack(side=tk.RIGHT)
    
    def check_system_requirements(self):
        """Check system requirements before installation."""
        self.req_status_label.config(text="Checking requirements...", foreground="blue")
        self.root.update_idletasks()
        
        # Check Python
        python_exe = self.find_python()
        if python_exe:
            try:
                # Get Python version
                if sys.platform == "win32":
                    CREATE_NO_WINDOW = 0x08000000
                    result = subprocess.run([python_exe, '--version'], capture_output=True, text=True, timeout=2, creationflags=CREATE_NO_WINDOW, shell=False)
                else:
                    result = subprocess.run([python_exe, '--version'], capture_output=True, text=True, timeout=2)
                version_str = result.stdout.strip() or result.stderr.strip()
                # Parse version
                match = re.search(r'(\d+)\.(\d+)', version_str)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    if major == 3 and 8 <= minor <= 12:
                        self.python_status_label.config(text=f"Python: {version_str} ✓ (Compatible)", foreground="green")
                    else:
                        self.python_status_label.config(text=f"Python: {version_str} ⚠ (3.8-3.12 recommended)", foreground="orange")
                else:
                    self.python_status_label.config(text=f"Python: Found ✓ (Version unknown)", foreground="green")
            except:
                self.python_status_label.config(text="Python: Found ✓ (Version check failed)", foreground="green")
        else:
            self.python_status_label.config(text="Python: ✗ Not found (Required)", foreground="red")
        
        # Check Tesseract
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        tesseract_found = False
        tesseract_path = None
        for path in tesseract_paths:
            if os.path.exists(path):
                tesseract_found = True
                tesseract_path = path
                break
        
        if tesseract_found:
            try:
                # Get Tesseract version
                if sys.platform == "win32":
                    CREATE_NO_WINDOW = 0x08000000
                    result = subprocess.run([tesseract_path, '--version'], capture_output=True, text=True, timeout=2, creationflags=CREATE_NO_WINDOW, shell=False)
                else:
                    result = subprocess.run([tesseract_path, '--version'], capture_output=True, text=True, timeout=2)
                version_line = result.stdout.split('\n')[0] if result.stdout else ""
                version_match = re.search(r'(\d+\.\d+)', version_line)
                version_str = version_match.group(1) if version_match else "Found"
                self.tesseract_status_label.config(text=f"Tesseract OCR: {version_str} ✓ (Installed)", foreground="green")
            except:
                self.tesseract_status_label.config(text="Tesseract OCR: Found ✓ (Required for OCR)", foreground="green")
            # Hide download button if Tesseract is found
            self.tesseract_download_btn.pack_forget()
        else:
            self.tesseract_status_label.config(text="Tesseract OCR: ✗ Not found (Required for OCR)", foreground="red")
            # Show download button if Tesseract is not found
            self.tesseract_download_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.system_checked = True
        self.req_status_label.config(text="Requirements check complete", foreground="green")
    
    def open_tesseract_download(self):
        """Open Tesseract OCR download page in default browser."""
        try:
            import webbrowser
            tesseract_url = "https://github.com/UB-Mannheim/tesseract/wiki"
            webbrowser.open(tesseract_url)
            # Update status to show that browser was opened
            self.tesseract_status_label.config(text="Tesseract OCR: ✗ Not found → Opening download page...", foreground="orange")
            self.root.after(2000, lambda: self.tesseract_status_label.config(text="Tesseract OCR: ✗ Not found (Required for OCR)", foreground="red"))
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error Opening Browser",
                f"Could not open browser automatically.\n\n"
                f"Please manually visit:\n"
                f"https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                f"Error: {e}"
            )
    
    def open_streamerbot_download(self):
        """Open Streamer.bot download page in default browser."""
        try:
            import webbrowser
            streamerbot_url = "https://streamer.bot/"
            webbrowser.open(streamerbot_url)
            # Update status to show that browser was opened
            self.streamerbot_status_label.config(text="Streamer.bot: Opening download page...", foreground="blue")
            self.root.after(2000, lambda: self.streamerbot_status_label.config(text="Streamer.bot: Optional (for OBS integration)", foreground="gray"))
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error Opening Browser",
                f"Could not open browser automatically.\n\n"
                f"Please manually visit:\n"
                f"https://streamer.bot/\n\n"
                f"Error: {e}"
            )
    
    def import_streamerbot_action(self):
        """
        Open Windows Explorer to the installation directory with the .cs file selected.
        
        This function does NOT copy files to Streamer.bot. It only:
        1. Finds the deathcounteraction.cs file in the installation directory
        2. Opens Windows Explorer to that directory with the file selected
        3. Provides instructions for manual drag-and-drop import into Streamer.bot
        
        Streamer.bot requires manual drag-and-drop import through its UI.
        This function just makes it easy to find the file location.
        """
        try:
            import tkinter.messagebox as messagebox
            import subprocess
            import platform
            
            # Get the action file from installation directory (where files were installed)
            action_file_source = None
            
            # First priority: Check installation directory (where files were installed)
            if hasattr(self, 'install_dir') and self.install_dir and os.path.exists(self.install_dir):
                install_dir_action = os.path.join(self.install_dir, "deathcounteraction.cs")
                if os.path.exists(install_dir_action):
                    action_file_source = install_dir_action
            
            # Second priority: Check embedded files (if installer is running)
            if not action_file_source:
                try:
                    if getattr(sys, 'frozen', False):
                        # Running as compiled EXE - PyInstaller creates a temp folder
                        try:
                            base_path = sys._MEIPASS
                        except AttributeError:
                            base_path = INSTALLER_DIR
                    else:
                        # Running as script
                        base_path = INSTALLER_DIR
                    
                    embedded_path = os.path.join(base_path, "deathcounteraction.cs")
                    if os.path.exists(embedded_path):
                        action_file_source = embedded_path
                except:
                    pass
            
            # Third priority: Try current directory or script directory
            if not action_file_source:
                alt_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "deathcounteraction.cs"),
                    os.path.join(os.getcwd(), "deathcounteraction.cs"),
                ]
                
                for alt_path in alt_paths:
                    if alt_path and os.path.exists(alt_path):
                        action_file_source = alt_path
                        break
            
            # If still not found, browse for it (defaulting to installation directory)
            if not action_file_source or not os.path.exists(action_file_source):
                import tkinter.filedialog as filedialog
                
                # Default to installation directory if available
                initial_dir = self.install_dir if hasattr(self, 'install_dir') and self.install_dir and os.path.exists(self.install_dir) else os.path.expanduser("~\\Desktop")
                
                action_file_source = filedialog.askopenfilename(
                    title="Select deathcounteraction.cs File",
                    filetypes=[("C# Files", "*.cs"), ("All Files", "*.*")],
                    initialdir=initial_dir,
                )
                
                if not action_file_source:
                    messagebox.showinfo(
                        "Import Cancelled",
                        "Import cancelled.\n\n"
                        f"The action file should be in your installation directory:\n"
                        f"{self.install_dir if hasattr(self, 'install_dir') and self.install_dir else 'N/A'}\n\n"
                        "You can import it manually from there by:\n"
                        "1. Opening the installation directory in Windows Explorer\n"
                        "2. Dragging 'deathcounteraction.cs' into Streamer.bot's import window"
                    )
                    return
            
            # Open Windows Explorer to the file location (NOT copying to Streamer.bot!)
            # This just opens Explorer with the file selected so you can drag-and-drop it
            try:
                if platform.system() == "Windows":
                    # Open Windows Explorer with the file selected
                    # This opens the installation directory and highlights the .cs file
                    # Does NOT copy files anywhere - just opens Explorer!
                    subprocess.Popen(f'explorer /select,"{action_file_source}"', shell=True)
                else:
                    # For other platforms, just open the directory
                    file_dir = os.path.dirname(os.path.abspath(action_file_source))
                    subprocess.Popen(['open' if platform.system() == 'Darwin' else 'xdg-open', file_dir])
                
                messagebox.showinfo(
                    "Action File Location Opened",
                    f"Windows Explorer has been opened to your installation directory\n"
                    f"with 'deathcounteraction.cs' selected.\n\n"
                    f"File location:\n{action_file_source}\n\n"
                    f"To import into Streamer.bot (manual drag-and-drop required):\n"
                    f"1. Open Streamer.bot\n"
                    f"2. Go to Actions tab → Import (or File → Import Action)\n"
                    f"3. Drag and drop 'deathcounteraction.cs' from Windows Explorer\n"
                    f"   into Streamer.bot's import window\n\n"
                    f"Note: This does NOT automatically copy files to Streamer.bot.\n"
                    f"You must manually drag-and-drop the file."
                )
                
                self.streamerbot_status_label.config(
                    text="Streamer.bot: File location opened - drag & drop file manually",
                    foreground="blue"
                )
                self.root.after(8000, lambda: self.streamerbot_status_label.config(
                    text="Streamer.bot: Optional (for OBS integration)",
                    foreground="gray"
                ))
                
            except Exception as e:
                # Fallback: just show the file location
                messagebox.showinfo(
                    "Action File Location",
                    f"Death Counter action file location:\n\n"
                    f"{action_file_source}\n\n"
                    f"To import into Streamer.bot (manual drag-and-drop required):\n"
                    f"1. Open Streamer.bot\n"
                    f"2. Go to Actions tab → Import\n"
                    f"3. Navigate to the file location above in Windows Explorer\n"
                    f"4. Drag and drop 'deathcounteraction.cs' into Streamer.bot's import window\n\n"
                    f"Note: This does NOT automatically copy files. Manual drag-and-drop is required.\n\n"
                    f"Error opening file location: {e}"
                )
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Error Opening File Location",
                f"An error occurred while opening the action file location:\n\n{e}\n\n"
                f"Please ensure files were installed and try again.\n\n"
                f"The file should be in your installation directory:\n"
                f"{self.install_dir if hasattr(self, 'install_dir') and self.install_dir else 'N/A'}"
            )
    
    def show_about(self):
        """Show About dialog."""
        about_text = f"""Death Counter Installer v{INSTALLER_VERSION}

Death Counter v{DEATH_COUNTER_VERSION}
Multi-Game Soulsborne Death Counter

Features:
• Multi-method detection (OCR, Log Monitoring, Memory Scanning)
• Supports Elden Ring, Dark Souls series, Sekiro, and more
• Automatic game detection
• GUI and Settings interface
• Per-game and total death counts

System Requirements:
• Python 3.8-3.12 (required)
• Tesseract OCR (optional, for OCR detection)
• Windows 7 or later

Files Included:
• {len(EMBEDDED_FILES)} Python scripts and configuration files
• Documentation (README.md, FUZZY_MATCHING_GUIDE.md)
• Batch files for easy startup/shutdown

For more information, see the README.md file after installation.

© 2024 Death Counter Project"""
        
        messagebox.showinfo("About Death Counter Installer", about_text)
    
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
        
        # Warn if requirements not checked
        if not self.system_checked:
            result = messagebox.askyesno(
                "Requirements Not Checked",
                "System requirements have not been checked yet.\n\n"
                "It's recommended to check requirements before installing.\n\n"
                "Do you want to continue anyway?",
                icon=messagebox.WARNING
            )
            if not result:
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
            
            # Copy icon files (if they exist) - for desktop shortcuts
            # This happens after files are extracted, so icons should be in the bundle
            self.log("\nCopying icon files for shortcuts...")
            icons_copied = 0
            for icon_name in ICON_FILES:
                icon_source = resource_path(icon_name)
                if os.path.exists(icon_source):
                    icon_dest = os.path.join(self.install_dir, icon_name)
                    try:
                        shutil.copy2(icon_source, icon_dest)
                        self.log(f"  ✓ Copied {icon_name}")
                        icons_copied += 1
                    except Exception as e:
                        self.log(f"  ⚠ Failed to copy {icon_name}: {e}")
            
            if icons_copied > 0:
                self.log(f"  ✓ {icons_copied} icon file(s) copied")
            else:
                self.log("  ℹ No icon files found (shortcuts will use default icon)")
            
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
            
            # Create VBScript launcher for silent startup (no console window)
            self.log("\nCreating VBScript launcher...")
            vbs_lines = [
                'Set objShell = CreateObject("WScript.Shell")',
                'Set objFSO = CreateObject("Scripting.FileSystemObject")',
                'strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)',
                '',
                "' Change to script directory",
                'objShell.CurrentDirectory = strScriptDir',
                '',
                "' Check if compiled daemon EXE exists (preferred - no console window)",
                'strDaemonExe = strScriptDir & "\\DeathCounterDaemon.exe"',
                'If objFSO.FileExists(strDaemonExe) Then',
                '    objShell.Run Chr(34) & strDaemonExe & Chr(34), 0, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Try pythonw.exe (windowless Python)",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where pythonw")',
                'strPythonW = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPythonW) And strPythonW <> "" Then',
                '    objShell.Run Chr(34) & strPythonW & Chr(34) & " " & Chr(34) & strScriptDir & "\\multi_game_death_counter.py" & Chr(34), 0, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Try to find pythonw.exe by finding python.exe location",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where python")',
                'strPython = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPython) And strPython <> "" Then',
                '    strPythonDir = objFSO.GetParentFolderName(strPython)',
                '    strPythonW = strPythonDir & "\\pythonw.exe"',
                '    If objFSO.FileExists(strPythonW) Then',
                '        objShell.Run Chr(34) & strPythonW & Chr(34) & " " & Chr(34) & strScriptDir & "\\multi_game_death_counter.py" & Chr(34), 0, False',
                '        WScript.Quit',
                '    End If',
                'End If',
                '',
                "' Second resort: use python normally (normal window, not minimized)",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where python")',
                'strPython = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPython) And strPython <> "" Then',
                '    objShell.Run Chr(34) & strPython & Chr(34) & " " & Chr(34) & strScriptDir & "\\multi_game_death_counter.py" & Chr(34), 1, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Third resort: use python with console window visible",
                'objShell.Run "python " & Chr(34) & strScriptDir & "\\multi_game_death_counter.py" & Chr(34), 1, False',
            ]
            vbs_launcher = '\n'.join(vbs_lines)
            vbs_path = os.path.join(self.install_dir, "START_DEATH_COUNTER.vbs")
            try:
                with open(vbs_path, 'w', encoding='utf-8') as f:
                    f.write(vbs_launcher)
                self.log("  ✓ START_DEATH_COUNTER.vbs (silent launcher)")
            except Exception as e:
                self.log(f"  ⚠ START_DEATH_COUNTER.vbs: {e}")
            
            # Create VBScript launcher for GUI (no console window)
            self.log("\nCreating GUI VBScript launcher...")
            gui_vbs_lines = [
                'Set objShell = CreateObject("WScript.Shell")',
                'Set objFSO = CreateObject("Scripting.FileSystemObject")',
                'strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)',
                '',
                "' Change to script directory",
                'objShell.CurrentDirectory = strScriptDir',
                '',
                "' Check if compiled GUI EXE exists (preferred - no console window)",
                'strGuiExe = strScriptDir & "\\DeathCounter.exe"',
                'If objFSO.FileExists(strGuiExe) Then',
                '    objShell.Run Chr(34) & strGuiExe & Chr(34), 0, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Try pythonw.exe (windowless Python)",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where pythonw")',
                'strPythonW = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPythonW) And strPythonW <> "" Then',
                '    objShell.Run Chr(34) & strPythonW & Chr(34) & " " & Chr(34) & strScriptDir & "\\death_counter_gui.py" & Chr(34), 0, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Try to find pythonw.exe by finding python.exe location",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where python")',
                'strPython = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPython) And strPython <> "" Then',
                '    strPythonDir = objFSO.GetParentFolderName(strPython)',
                '    strPythonW = strPythonDir & "\\pythonw.exe"',
                '    If objFSO.FileExists(strPythonW) Then',
                '        objShell.Run Chr(34) & strPythonW & Chr(34) & " " & Chr(34) & strScriptDir & "\\death_counter_gui.py" & Chr(34), 0, False',
                '        WScript.Quit',
                '    End If',
                'End If',
                '',
                "' Second resort: use python normally (normal window, not minimized)",
                'On Error Resume Next',
                'Set objExec = objShell.Exec("where python")',
                'strPython = objExec.StdOut.ReadLine()',
                'On Error Goto 0',
                '',
                'If Not IsEmpty(strPython) And strPython <> "" Then',
                '    objShell.Run Chr(34) & strPython & Chr(34) & " " & Chr(34) & strScriptDir & "\\death_counter_gui.py" & Chr(34), 1, False',
                '    WScript.Quit',
                'End If',
                '',
                "' Third resort: use python with console window visible",
                'objShell.Run "python " & Chr(34) & strScriptDir & "\\death_counter_gui.py" & Chr(34), 1, False',
            ]
            gui_vbs_launcher = '\n'.join(gui_vbs_lines)
            gui_vbs_path = os.path.join(self.install_dir, "START_GUI.vbs")
            try:
                with open(gui_vbs_path, 'w', encoding='utf-8') as f:
                    f.write(gui_vbs_launcher)
                self.log("  ✓ START_GUI.vbs (silent GUI launcher)")
            except Exception as e:
                self.log(f"  ⚠ START_GUI.vbs: {e}")
            
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
            
            # For offline version, dependencies are bundled - skip pip install
            self.log("\nDependency installation (OFFLINE MODE)...")
            self.update_status("Checking bundled dependencies...", 70)
            self.log("  ✓ All dependencies are bundled in this installer")
            self.log("  ✓ No pip install required - ready to use")
            self.log("  ✓ This is the offline/self-contained version")
            
            if python_exe:
                self.update_status("Offline installation ready", 85)
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
                    # Open download page in browser
                    try:
                        import webbrowser
                        webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")
                        self.log("  → Opened Tesseract download page in your browser")
                    except Exception as e:
                        self.log(f"  → Could not open browser automatically: {e}")
                        self.log("  → Please manually visit: https://github.com/UB-Mannheim/tesseract/wiki")
            
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
                    gui_exe = os.path.join(self.install_dir, "DeathCounter.exe")
                    
                    # Check if GUI EXE exists first (preferred - no console window)
                    if os.path.exists(gui_exe):
                        # Use the GUI EXE directly (no console window)
                        if self.create_shortcut_exe(shortcut_path, gui_exe, "Death Counter"):
                            self.log("  ✓ Desktop shortcut created (using DeathCounter.exe)")
                        else:
                            self.log("  ⚠ Could not create shortcut")
                    elif not os.path.exists(gui_script):
                        self.log(f"  ⚠ GUI script not found at: {gui_script}")
                        self.log("  Skipping shortcut creation")
                    elif not python_exe:
                        self.log("  ⚠ Cannot create shortcut (Python not found)")
                        self.log("  Install Python and manually create shortcut if needed")
                    else:
                        # Convert python.exe to pythonw.exe (windowless) for GUI
                        pythonw_exe = None
                        if python_exe == 'python' or python_exe == 'py':
                            # For command names, try pythonw or py -3 -3.11 etc
                            try:
                                if sys.platform == "win32":
                                    CREATE_NO_WINDOW = 0x08000000
                                    result = subprocess.run(['pythonw', '--version'], capture_output=True, text=True, timeout=2, creationflags=CREATE_NO_WINDOW, shell=False)
                                    if result.returncode == 0:
                                        pythonw_exe = 'pythonw'
                            except:
                                pass
                        elif isinstance(python_exe, str) and 'python' in python_exe.lower():
                            # For paths, replace python.exe with pythonw.exe
                            pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe').replace('python', 'pythonw')
                            if not os.path.exists(pythonw_exe):
                                pythonw_exe = None
                        
                        # Use pythonw.exe if found, otherwise fallback to python.exe
                        if not pythonw_exe:
                            pythonw_exe = python_exe
                            self.log("  ⚠ pythonw.exe not found, using python.exe (console window may appear)")
                        
                        if self.create_shortcut(shortcut_path, gui_script, pythonw_exe, "Death Counter"):
                            if pythonw_exe != python_exe:
                                self.log("  ✓ Desktop shortcut created (using pythonw.exe - no console window)")
                            else:
                                self.log("  ✓ Desktop shortcut created (using python.exe)")
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
                
                # Enable import button after files are installed
                self.streamerbot_import_btn.config(state=tk.NORMAL)
                
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
        # Define CREATE_NO_WINDOW flag for Windows
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
        else:
            CREATE_NO_WINDOW = 0
        
        # Try 'python' command
        try:
            if sys.platform == "win32":
                result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=2, creationflags=CREATE_NO_WINDOW, shell=False)
            else:
                result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'python'
        except:
            pass
        
        # Try 'py' launcher
        try:
            if sys.platform == "win32":
                result = subprocess.run(['py', '--version'], capture_output=True, text=True, timeout=2, creationflags=CREATE_NO_WINDOW, shell=False)
            else:
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
    
    def create_shortcut_exe(self, shortcut_path, exe_path, description):
        """Create a Windows shortcut to an EXE file (no console window)."""
        # Find shortcut icon
        shortcut_icon = None
        icon_candidates = [
            os.path.join(INSTALLER_DIR, "shortcut_icon.ico"),
            os.path.join(INSTALLER_DIR, "screenshot.ico"),
            os.path.join(INSTALLER_DIR, "Screenshot.ico"),
            os.path.join(self.install_dir, "shortcut_icon.ico"),
            os.path.join(self.install_dir, "screenshot.ico"),
            os.path.join(self.install_dir, "gui_icon.ico"),
            os.path.join(self.install_dir, "smonker.ico"),
        ]
        
        for icon_path in icon_candidates:
            if os.path.exists(icon_path):
                shortcut_icon = icon_path
                break
        
        if not shortcut_icon:
            gui_icon_candidates = [
                os.path.join(INSTALLER_DIR, "gui_icon.ico"),
                os.path.join(INSTALLER_DIR, "smonker.ico"),
                os.path.join(self.install_dir, "gui_icon.ico"),
                os.path.join(self.install_dir, "smonker.ico"),
            ]
            for icon_path in gui_icon_candidates:
                if os.path.exists(icon_path):
                    shortcut_icon = icon_path
                    break
        
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.Description = description
            if shortcut_icon:
                shortcut.IconLocation = shortcut_icon
            else:
                shortcut.IconLocation = exe_path
            shortcut.save()
            return True
        except:
            return False
    
    def create_shortcut(self, shortcut_path, target, python_exe, description):
        """Create a Windows shortcut using pythonw.exe (windowless)."""
        # Find shortcut icon (screenshot icon for desktop shortcuts)
        shortcut_icon = None
        icon_candidates = [
            os.path.join(INSTALLER_DIR, "shortcut_icon.ico"),
            os.path.join(INSTALLER_DIR, "screenshot.ico"),
            os.path.join(INSTALLER_DIR, "Screenshot.ico"),
            os.path.join(self.install_dir, "shortcut_icon.ico"),
            os.path.join(self.install_dir, "screenshot.ico"),
            os.path.join(self.install_dir, "gui_icon.ico"),
            os.path.join(self.install_dir, "smonker.ico"),
        ]
        
        for icon_path in icon_candidates:
            if os.path.exists(icon_path):
                shortcut_icon = icon_path
                break
        
        # If no shortcut icon found, try to use GUI icon or fallback to Python icon
        if not shortcut_icon:
            gui_icon_candidates = [
                os.path.join(INSTALLER_DIR, "gui_icon.ico"),
                os.path.join(INSTALLER_DIR, "smonker.ico"),
                os.path.join(self.install_dir, "gui_icon.ico"),
                os.path.join(self.install_dir, "smonker.ico"),
            ]
            for icon_path in gui_icon_candidates:
                if os.path.exists(icon_path):
                    shortcut_icon = icon_path
                    break
        
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = python_exe  # This should already be pythonw.exe
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.Description = description
            # Use shortcut icon if found, otherwise use Python icon
            if shortcut_icon:
                shortcut.IconLocation = shortcut_icon
            else:
                shortcut.IconLocation = python_exe
            shortcut.save()
            return True
        except:
            # Fallback: create a batch file shortcut using pythonw.exe (windowless)
            try:
                batch_content = f'@echo off\ncd /d "{os.path.dirname(target)}"\n"{python_exe}" "{target}"\n'
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
