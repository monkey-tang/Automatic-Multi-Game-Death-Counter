"""
Death Counter Settings GUI
A settings window to configure all death counter options.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, BooleanVar, DoubleVar, IntVar


class SettingsWindow:
    def __init__(self, parent, base_dir, config_file):
        self.parent = parent
        self.base_dir = base_dir
        self.config_file = config_file
        self.original_config = None
        self.needs_restart = False
        
        # Create settings window
        self.window = tk.Toplevel(parent)
        self.window.title("Death Counter Settings")
        self.window.geometry("700x650")
        self.window.resizable(False, False)
        self.window.transient(parent)  # Keep on top of parent
        self.window.grab_set()  # Modal window
        
        # Variables
        self.vars = {}
        self.detection_vars = {}
        
        # Load config
        self.load_config()
        
        # Create UI
        self.create_ui()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_config(self):
        """Load current configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.original_config = json.load(f)
            else:
                self.original_config = {
                    "settings": {},
                    "games": {},
                    "current_game": None
                }
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.original_config = {
                "settings": {},
                "games": {},
                "current_game": None
            }
    
    def create_ui(self):
        """Create the settings UI."""
        # Main container with scrollbar
        main_container = ttk.Frame(self.window, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        settings = self.original_config.get("settings", {})
        games = self.original_config.get("games", {})
        current_game = self.original_config.get("current_game", "")
        
        row = 0
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Death Counter Settings", font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 20), sticky="w")
        row += 1
        
        # ==========================================
        # DETECTION METHODS
        # ==========================================
        methods_frame = ttk.LabelFrame(scrollable_frame, text="Detection Methods (Requires Restart)", padding="10")
        methods_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        methods_frame.columnconfigure(1, weight=1)
        row += 1
        
        detection_methods = settings.get("detection_methods", {})
        
        # OCR
        self.detection_vars["ocr"] = BooleanVar(value=detection_methods.get("ocr", True))
        ocr_frame = ttk.Frame(methods_frame)
        ocr_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Checkbutton(ocr_frame, text="OCR (Optical Character Recognition)", variable=self.detection_vars["ocr"]).pack(side=tk.LEFT)
        ocr_status_text = "● Active" if detection_methods.get("ocr", True) else "○ Inactive"
        ocr_status_color = "green" if detection_methods.get("ocr", True) else "gray"
        self.ocr_status_label = ttk.Label(ocr_frame, text=ocr_status_text, foreground=ocr_status_color)
        self.ocr_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Log Monitoring
        self.detection_vars["log_monitoring"] = BooleanVar(value=detection_methods.get("log_monitoring", False))
        log_frame = ttk.Frame(methods_frame)
        log_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Checkbutton(log_frame, text="Log File Monitoring", variable=self.detection_vars["log_monitoring"]).pack(side=tk.LEFT)
        log_status_text = "● Active" if detection_methods.get("log_monitoring", False) else "○ Inactive"
        log_status_color = "green" if detection_methods.get("log_monitoring", False) else "gray"
        self.log_status_label = ttk.Label(log_frame, text=log_status_text, foreground=log_status_color)
        self.log_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Memory Scanning
        self.detection_vars["memory_scanning"] = BooleanVar(value=detection_methods.get("memory_scanning", False))
        mem_frame = ttk.Frame(methods_frame)
        mem_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Checkbutton(mem_frame, text="Memory Scanning (Windows Only)", variable=self.detection_vars["memory_scanning"]).pack(side=tk.LEFT)
        mem_status_text = "● Active" if detection_methods.get("memory_scanning", False) else "○ Inactive"
        mem_status_color = "green" if detection_methods.get("memory_scanning", False) else "gray"
        self.mem_status_label = ttk.Label(mem_frame, text=mem_status_text, foreground=mem_status_color)
        self.mem_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Bind to update status labels
        self.detection_vars["ocr"].trace("w", lambda *args: self.update_detection_status_labels())
        self.detection_vars["log_monitoring"].trace("w", lambda *args: self.update_detection_status_labels())
        self.detection_vars["memory_scanning"].trace("w", lambda *args: self.update_detection_status_labels())
        
        # ==========================================
        # OCR SETTINGS
        # ==========================================
        ocr_settings_frame = ttk.LabelFrame(scrollable_frame, text="OCR Settings (Requires Restart)", padding="10")
        ocr_settings_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ocr_settings_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Fuzzy OCR Matching
        fuzzy_value = settings.get("fuzzy_ocr_matching", True)
        self.vars["fuzzy_ocr_matching"] = BooleanVar(value=fuzzy_value)
        fuzzy_frame = ttk.Frame(ocr_settings_frame)
        fuzzy_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Checkbutton(fuzzy_frame, text="Fuzzy OCR Matching (Handles misreadings like Y0UD13D)", variable=self.vars["fuzzy_ocr_matching"]).pack(side=tk.LEFT)
        fuzzy_status_text = "● Enabled" if fuzzy_value else "○ Disabled"
        fuzzy_status_color = "green" if fuzzy_value else "gray"
        self.fuzzy_status_label = ttk.Label(fuzzy_frame, text=fuzzy_status_text, foreground=fuzzy_status_color)
        self.fuzzy_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.vars["fuzzy_ocr_matching"].trace("w", lambda *args: self.update_fuzzy_status())
        
        # ==========================================
        # PERFORMANCE SETTINGS
        # ==========================================
        perf_frame = ttk.LabelFrame(scrollable_frame, text="Performance Settings (Requires Restart)", padding="10")
        perf_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        perf_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Tick Seconds
        ttk.Label(perf_frame, text="Tick Interval (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["tick_seconds"] = DoubleVar(value=settings.get("tick_seconds", 0.3))
        tick_spin = ttk.Spinbox(perf_frame, from_=0.1, to=5.0, increment=0.1, width=10, textvariable=self.vars["tick_seconds"])
        tick_spin.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(perf_frame, text="(Lower = faster detection, higher CPU usage)", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Consecutive Hits
        ttk.Label(perf_frame, text="Consecutive Hits Required:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["consecutive_hits"] = IntVar(value=settings.get("consecutive_hits", 2))
        hits_spin = ttk.Spinbox(perf_frame, from_=1, to=10, increment=1, width=10, textvariable=self.vars["consecutive_hits"])
        hits_spin.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(perf_frame, text="(Number of detections needed to confirm death)", font=("Arial", 8)).grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        
        # Cooldown Seconds
        ttk.Label(perf_frame, text="Cooldown Period (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["cooldown_seconds"] = DoubleVar(value=settings.get("cooldown_seconds", 5.0))
        cooldown_spin = ttk.Spinbox(perf_frame, from_=1.0, to=60.0, increment=0.5, width=10, textvariable=self.vars["cooldown_seconds"])
        cooldown_spin.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(perf_frame, text="(Time to ignore duplicate detections)", font=("Arial", 8)).grid(row=2, column=2, sticky=tk.W, padx=(10, 0))
        
        # Debug Every Ticks
        ttk.Label(perf_frame, text="Debug Log Interval (ticks):").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["debug_every_ticks"] = IntVar(value=settings.get("debug_every_ticks", 30))
        debug_spin = ttk.Spinbox(perf_frame, from_=1, to=1000, increment=10, width=10, textvariable=self.vars["debug_every_ticks"])
        debug_spin.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Label(perf_frame, text="(How often to log debug info)", font=("Arial", 8)).grid(row=3, column=2, sticky=tk.W, padx=(10, 0))
        
        # ==========================================
        # DISPLAY SETTINGS
        # ==========================================
        display_frame = ttk.LabelFrame(scrollable_frame, text="Display Settings (Requires Restart)", padding="10")
        display_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        display_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Default Monitor Index
        ttk.Label(display_frame, text="Default Monitor Index:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["monitor_index"] = IntVar(value=settings.get("monitor_index", 1))
        monitor_spin = ttk.Spinbox(display_frame, from_=0, to=10, increment=1, width=10, textvariable=self.vars["monitor_index"])
        monitor_spin.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Label(display_frame, text="(0 = all monitors, 1+ = specific monitor)", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # ==========================================
        # GAME SELECTION
        # ==========================================
        game_frame = ttk.LabelFrame(scrollable_frame, text="Current Game (Active Immediately)", padding="10")
        game_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        game_frame.columnconfigure(1, weight=1)
        row += 1
        
        ttk.Label(game_frame, text="Default Game:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.vars["current_game"] = StringVar(value=current_game)
        game_combo = ttk.Combobox(game_frame, textvariable=self.vars["current_game"], state="readonly", width=40)
        if games:
            game_combo['values'] = list(games.keys())
        game_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(game_frame, text="(Game used when no process is detected)", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # ==========================================
        # RESTART WARNING
        # ==========================================
        warning_frame = ttk.Frame(scrollable_frame)
        warning_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        row += 1
        
        self.restart_warning = ttk.Label(
            warning_frame,
            text="⚠ Some settings require restarting the daemon to take effect.",
            foreground="orange",
            font=("Arial", 9, "bold")
        )
        self.restart_warning.pack()
        self.restart_warning.pack_forget()  # Hide initially
        
        # ==========================================
        # BUTTONS
        # ==========================================
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(20, 10))
        row += 1
        
        ttk.Button(button_frame, text="Save", command=self.save_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults, width=15).pack(side=tk.LEFT, padx=5)
        
        # Track changes to show restart warning
        for var in self.vars.values():
            if isinstance(var, (BooleanVar, DoubleVar, IntVar)):
                var.trace("w", lambda *args: self.check_restart_needed())
        
        for var in self.detection_vars.values():
            var.trace("w", lambda *args: self.check_restart_needed())
    
    def update_detection_status_labels(self):
        """Update the detection method status labels."""
        status_ocr = "● Active" if self.detection_vars["ocr"].get() else "○ Inactive"
        status_log = "● Active" if self.detection_vars["log_monitoring"].get() else "○ Inactive"
        status_mem = "● Active" if self.detection_vars["memory_scanning"].get() else "○ Inactive"
        
        self.ocr_status_label.config(
            text=status_ocr,
            foreground="green" if self.detection_vars["ocr"].get() else "gray"
        )
        self.log_status_label.config(
            text=status_log,
            foreground="green" if self.detection_vars["log_monitoring"].get() else "gray"
        )
        self.mem_status_label.config(
            text=status_mem,
            foreground="green" if self.detection_vars["memory_scanning"].get() else "gray"
        )
    
    def update_fuzzy_status(self):
        """Update the fuzzy OCR matching status label."""
        status = "● Enabled" if self.vars["fuzzy_ocr_matching"].get() else "○ Disabled"
        self.fuzzy_status_label.config(
            text=status,
            foreground="green" if self.vars["fuzzy_ocr_matching"].get() else "gray"
        )
    
    def check_restart_needed(self):
        """Check if restart is needed and show warning."""
        self.needs_restart = True
        self.restart_warning.pack()
    
    def reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset to Defaults", "Reset all settings to default values?"):
            # Reset detection methods
            self.detection_vars["ocr"].set(True)
            self.detection_vars["log_monitoring"].set(False)
            self.detection_vars["memory_scanning"].set(False)
            
            # Reset OCR settings
            self.vars["fuzzy_ocr_matching"].set(True)
            
            # Reset performance settings
            self.vars["tick_seconds"].set(0.3)
            self.vars["consecutive_hits"].set(2)
            self.vars["cooldown_seconds"].set(5.0)
            self.vars["debug_every_ticks"].set(30)
            
            # Reset display settings
            self.vars["monitor_index"].set(1)
            
            # Reset game selection
            games = self.original_config.get("games", {})
            if games:
                self.vars["current_game"].set(list(games.keys())[0])
            else:
                self.vars["current_game"].set("")
            
            self.check_restart_needed()
            messagebox.showinfo("Defaults Reset", "Settings reset to defaults. Click 'Save' to apply.")
    
    def is_daemon_running(self):
        """Check if daemon is running."""
        lock_file = os.path.join(self.base_dir, "daemon.lock")
        if not os.path.exists(lock_file):
            return False
        
        try:
            import subprocess
            with open(lock_file, "r") as f:
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
                        return True  # If we can't check, assume it's running
        except:
            pass
        return False
    
    def save_settings(self):
        """Save settings to config file."""
        try:
            # Check if daemon is running and restart is needed
            daemon_running = self.is_daemon_running()
            
            # Create new config
            new_config = json.loads(json.dumps(self.original_config))  # Deep copy
            
            # Update settings
            settings = new_config.setdefault("settings", {})
            settings["tick_seconds"] = self.vars["tick_seconds"].get()
            settings["consecutive_hits"] = self.vars["consecutive_hits"].get()
            settings["cooldown_seconds"] = self.vars["cooldown_seconds"].get()
            settings["debug_every_ticks"] = self.vars["debug_every_ticks"].get()
            settings["monitor_index"] = self.vars["monitor_index"].get()
            settings["fuzzy_ocr_matching"] = self.vars["fuzzy_ocr_matching"].get()
            
            # Update detection methods
            settings["detection_methods"] = {
                "ocr": self.detection_vars["ocr"].get(),
                "log_monitoring": self.detection_vars["log_monitoring"].get(),
                "memory_scanning": self.detection_vars["memory_scanning"].get()
            }
            
            # Update current game
            new_config["current_game"] = self.vars["current_game"].get()
            
            # Save to file
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=2)
            
            # Show success message with restart reminder
            if self.needs_restart:
                if daemon_running:
                    messagebox.showwarning(
                        "Settings Saved",
                        "Settings saved successfully!\n\n"
                        "⚠ IMPORTANT: The daemon is currently running.\n"
                        "Please STOP the daemon and START it again for these settings to take effect:\n\n"
                        "Settings requiring restart:\n"
                        "• Detection methods (OCR, Log Monitoring, Memory Scanning)\n"
                        "• OCR settings (Fuzzy Matching)\n"
                        "• Performance settings (Tick Interval, etc.)\n"
                        "• Display settings (Monitor Index)\n\n"
                        "Use the 'Stop Daemon' button, then 'Start Daemon' button."
                    )
                else:
                    messagebox.showwarning(
                        "Settings Saved",
                        "Settings saved successfully!\n\n"
                        "⚠ IMPORTANT: Please start the daemon for these settings to take effect:\n"
                        "- Detection methods\n"
                        "- OCR settings (fuzzy matching)\n"
                        "- Performance settings (tick interval, etc.)\n"
                        "- Display settings (monitor index)\n\n"
                        "Use the 'Start Daemon' button."
                    )
            else:
                if daemon_running:
                    messagebox.showinfo(
                        "Settings Saved",
                        "Settings saved successfully!\n\n"
                        "Note: The current game selection will take effect immediately.\n"
                        "Other changes may require restarting the daemon."
                    )
                else:
                    messagebox.showinfo("Settings Saved", "Settings saved successfully!")
            
            self.original_config = new_config
            self.needs_restart = False
            self.restart_warning.pack_forget()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def cancel(self):
        """Cancel and close without saving."""
        self.window.destroy()
    
    def on_closing(self):
        """Handle window closing."""
        self.cancel()
    
    def show(self):
        """Show the settings window and wait for it to close."""
        self.window.wait_window()
