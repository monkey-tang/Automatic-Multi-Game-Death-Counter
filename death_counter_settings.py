"""
Multi-Game Soulsborne Death Counter Settings GUI
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
        self.window.title("Multi-Game Soulsborne Death Counter Settings")
        self.window.geometry("800x750")
        self.window.resizable(True, True)
        self.window.transient(parent)  # Keep on top of parent
        self.window.grab_set()  # Modal window
        
        # Variables
        self.vars = {}
        self.detection_vars = {}
        self.game_region_vars = {}  # Store region variables for each game
        self._loading_game = False  # Flag to prevent auto-conversion when loading
        self._last_use_percentages = None  # Track last coordinate type for conversion
        
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
                    content = f.read().strip()
                    if not content:
                        # Empty file
                        self.original_config = {
                            "settings": {},
                            "games": {},
                            "current_game": None
                        }
                    else:
                        self.original_config = json.loads(content)
            else:
                self.original_config = {
                    "settings": {},
                    "games": {},
                    "current_game": None
                }
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file:\nLine {e.lineno}, Column {e.colno}: {e.msg}\n\nUsing default configuration."
            messagebox.showerror("Config Error", error_msg)
            self.original_config = {
                "settings": {},
                "games": {},
                "current_game": None
            }
        except Exception as e:
            error_msg = f"Failed to load config: {e}\n\nUsing default configuration."
            messagebox.showerror("Error", error_msg)
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
        title_label = ttk.Label(scrollable_frame, text="Multi-Game Soulsborne Death Counter Settings", font=("Arial", 14, "bold"))
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
        # PER-GAME OCR REGION SETTINGS
        # ==========================================
        region_frame = ttk.LabelFrame(scrollable_frame, text="Per-Game OCR Region Settings (Requires Restart)", padding="10")
        region_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        region_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Game selection for region editing
        ttk.Label(region_frame, text="Select Game:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10), padx=(0, 10))
        self.vars["selected_game_for_region"] = StringVar(value="")
        self.game_region_combo = ttk.Combobox(region_frame, textvariable=self.vars["selected_game_for_region"], state="readonly", width=40)
        if games:
            self.game_region_combo['values'] = list(games.keys())
        self.game_region_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        self.game_region_combo.bind("<<ComboboxSelected>>", self.on_game_selected_for_region)
        
        # Coordinate type toggle
        coord_type_frame = ttk.Frame(region_frame)
        coord_type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(coord_type_frame, text="Coordinate Type:").pack(side=tk.LEFT, padx=(0, 10))
        self.vars["use_percentages_for_region"] = BooleanVar(value=True)
        self.percent_toggle = ttk.Checkbutton(
            coord_type_frame, 
            text="Use Percentage-Based (0.0-1.0) - Recommended for multi-resolution",
            variable=self.vars["use_percentages_for_region"],
            command=self.on_coordinate_type_changed
        )
        self.percent_toggle.pack(side=tk.LEFT)
        
        # Region inputs frame
        region_inputs_frame = ttk.LabelFrame(region_frame, text="OCR Capture Region", padding="10")
        region_inputs_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        region_inputs_frame.columnconfigure(1, weight=1)
        
        # Left
        ttk.Label(region_inputs_frame, text="Left:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.game_region_vars["left"] = DoubleVar(value=0.0)
        self.left_spin = ttk.Spinbox(region_inputs_frame, from_=0.0, to=10000.0, increment=1.0, width=15, 
                                     textvariable=self.game_region_vars["left"])
        self.left_spin.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.left_label = ttk.Label(region_inputs_frame, text="(0.0-1.0 for %, or pixels)", font=("Arial", 8))
        self.left_label.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Top
        ttk.Label(region_inputs_frame, text="Top:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.game_region_vars["top"] = DoubleVar(value=0.0)
        self.top_spin = ttk.Spinbox(region_inputs_frame, from_=0.0, to=10000.0, increment=1.0, width=15,
                                    textvariable=self.game_region_vars["top"])
        self.top_spin.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.top_label = ttk.Label(region_inputs_frame, text="(0.0-1.0 for %, or pixels)", font=("Arial", 8))
        self.top_label.grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        
        # Width
        ttk.Label(region_inputs_frame, text="Width:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.game_region_vars["width"] = DoubleVar(value=0.0)
        self.width_spin = ttk.Spinbox(region_inputs_frame, from_=0.0, to=10000.0, increment=1.0, width=15,
                                      textvariable=self.game_region_vars["width"])
        self.width_spin.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.width_label = ttk.Label(region_inputs_frame, text="(0.0-1.0 for %, or pixels)", font=("Arial", 8))
        self.width_label.grid(row=2, column=2, sticky=tk.W, padx=(10, 0))
        
        # Height
        ttk.Label(region_inputs_frame, text="Height:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.game_region_vars["height"] = DoubleVar(value=0.0)
        self.height_spin = ttk.Spinbox(region_inputs_frame, from_=0.0, to=10000.0, increment=1.0, width=15,
                                       textvariable=self.game_region_vars["height"])
        self.height_spin.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.height_label = ttk.Label(region_inputs_frame, text="(0.0-1.0 for %, or pixels)", font=("Arial", 8))
        self.height_label.grid(row=3, column=2, sticky=tk.W, padx=(10, 0))
        
        # Help text
        help_text = ttk.Label(region_inputs_frame, 
                             text="Tip: Use percentages (0.0-1.0) for multi-resolution support, or pixels for specific resolution.",
                             font=("Arial", 8), foreground="gray")
        help_text.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Initialize with first game if available
        if games and list(games.keys()):
            self.vars["selected_game_for_region"].set(list(games.keys())[0])
            self.on_game_selected_for_region()
        
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
        
        # Track region variable changes
        for var in self.game_region_vars.values():
            if isinstance(var, (DoubleVar, IntVar)):
                var.trace("w", lambda *args: self.check_restart_needed())
    
    def on_game_selected_for_region(self, event=None):
        """Load OCR region settings for the selected game."""
        selected_game = self.vars["selected_game_for_region"].get()
        if not selected_game:
            return
        
        games = self.original_config.get("games", {})
        if selected_game not in games:
            return
        
        game_config = games[selected_game]
        region = game_config.get("region", {})
        
        # Check if using percentages
        use_percentages = region.get("use_percentages", False)
        
        # Store original values before setting toggle (to prevent auto-conversion)
        self._loading_game = True
        self.vars["use_percentages_for_region"].set(use_percentages)
        
        # Load region values
        self.game_region_vars["left"].set(region.get("left", 0.0))
        self.game_region_vars["top"].set(region.get("top", 0.0))
        self.game_region_vars["width"].set(region.get("width", 0.0))
        self.game_region_vars["height"].set(region.get("height", 0.0))
        
        # Update coordinate type and labels (without conversion)
        self._loading_game = False
        self.update_coordinate_type_ui()
    
    def update_coordinate_type_ui(self):
        """Update UI based on coordinate type without conversion."""
        use_percentages = self.vars["use_percentages_for_region"].get()
        
        if use_percentages:
            # Update spinbox ranges for percentages (0.0-1.0)
            self.left_spin.config(from_=0.0, to=1.0, increment=0.001)
            self.top_spin.config(from_=0.0, to=1.0, increment=0.001)
            self.width_spin.config(from_=0.0, to=1.0, increment=0.001)
            self.height_spin.config(from_=0.0, to=1.0, increment=0.001)
            
            # Update help labels
            self.left_label.config(text="(0.0-1.0 = 0-100% of screen width)")
            self.top_label.config(text="(0.0-1.0 = 0-100% of screen height)")
            self.width_label.config(text="(0.0-1.0 = 0-100% of screen width)")
            self.height_label.config(text="(0.0-1.0 = 0-100% of screen height)")
        else:
            # Update spinbox ranges for pixels (0-10000)
            self.left_spin.config(from_=0.0, to=10000.0, increment=1.0)
            self.top_spin.config(from_=0.0, to=10000.0, increment=1.0)
            self.width_spin.config(from_=0.0, to=10000.0, increment=1.0)
            self.height_spin.config(from_=0.0, to=10000.0, increment=1.0)
            
            # Update help labels
            self.left_label.config(text="(pixels from left edge)")
            self.top_label.config(text="(pixels from top edge)")
            self.width_label.config(text="(pixels width)")
            self.height_label.config(text="(pixels height)")
    
    def on_coordinate_type_changed(self):
        """Update UI when coordinate type changes - with conversion if needed."""
        # Update UI first
        old_use_percentages = getattr(self, '_last_use_percentages', None)
        use_percentages = self.vars["use_percentages_for_region"].get()
        
        # If we're loading a game, don't convert
        if getattr(self, '_loading_game', False):
            self._last_use_percentages = use_percentages
            self.update_coordinate_type_ui()
            return
        
        # Update UI
        self.update_coordinate_type_ui()
        
        # If type changed and we have values, convert them
        if old_use_percentages is not None and old_use_percentages != use_percentages:
            # Get current values
            left = self.game_region_vars["left"].get()
            top = self.game_region_vars["top"].get()
            width = self.game_region_vars["width"].get()
            height = self.game_region_vars["height"].get()
            
            # Ask user if they want to convert
            if left > 0 or top > 0 or width > 0 or height > 0:
                if messagebox.askyesno(
                    "Convert Coordinates?",
                    f"Would you like to convert the current values from {'percentage' if old_use_percentages else 'pixel'} to {'pixel' if use_percentages else 'percentage'} coordinates?\n\n"
                    f"(Assumes 1920x1080 resolution for conversion)\n\n"
                    f"Current: left={left}, top={top}, width={width}, height={height}"
                ):
                    # Assume 1920x1080 for conversion
                    if old_use_percentages and not use_percentages:
                        # Converting from % to pixels (assume 1920x1080)
                        self.game_region_vars["left"].set(round(left * 1920))
                        self.game_region_vars["top"].set(round(top * 1080))
                        self.game_region_vars["width"].set(round(width * 1920))
                        self.game_region_vars["height"].set(round(height * 1080))
                    elif not old_use_percentages and use_percentages:
                        # Converting from pixels to % (assume 1920x1080)
                        if left > 0 and top > 0:
                            self.game_region_vars["left"].set(round(left / 1920, 4))
                            self.game_region_vars["top"].set(round(top / 1080, 4))
                        if width > 0 and height > 0:
                            self.game_region_vars["width"].set(round(width / 1920, 4))
                            self.game_region_vars["height"].set(round(height / 1080, 4))
        
        self._last_use_percentages = use_percentages
    
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
            
            # Reset OCR region settings if UI is initialized
            if "selected_game_for_region" in self.vars and self.vars["selected_game_for_region"].get():
                # Reset to default percentage-based with centered region
                self.vars["use_percentages_for_region"].set(True)
                self.game_region_vars["left"].set(0.25)
                self.game_region_vars["top"].set(0.4)
                self.game_region_vars["width"].set(0.5)
                self.game_region_vars["height"].set(0.2)
                self.update_coordinate_type_ui()
            
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
                        import sys
                        if sys.platform == "win32":
                            CREATE_NO_WINDOW = 0x08000000
                            result = subprocess.run(
                                ["tasklist", "/FI", f"PID eq {pid}"],
                                capture_output=True,
                                text=True,
                                timeout=2,
                                creationflags=CREATE_NO_WINDOW,
                                shell=False
                            )
                        else:
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
            
            # Update OCR region for selected game (if a game is selected)
            if "selected_game_for_region" in self.vars:
                selected_game = self.vars["selected_game_for_region"].get()
                if selected_game and selected_game in new_config.get("games", {}):
                    game_config = new_config["games"][selected_game]
                    
                    # Get region values (if they exist)
                    if "use_percentages_for_region" in self.vars and all(key in self.game_region_vars for key in ["left", "top", "width", "height"]):
                        use_percentages = self.vars["use_percentages_for_region"].get()
                        left = self.game_region_vars["left"].get()
                        top = self.game_region_vars["top"].get()
                        width = self.game_region_vars["width"].get()
                        height = self.game_region_vars["height"].get()
                        
                        # Validate values
                        if use_percentages:
                            # Percentages should be 0.0-1.0
                            left = max(0.0, min(1.0, left))
                            top = max(0.0, min(1.0, top))
                            width = max(0.0, min(1.0, width))
                            height = max(0.0, min(1.0, height))
                            
                            # Warn if values seem invalid
                            if width <= 0 or height <= 0:
                                messagebox.showwarning(
                                    "Invalid Region",
                                    f"Warning: Region width or height is zero or negative.\n"
                                    f"This may prevent OCR from working correctly."
                                )
                        else:
                            # Pixels should be positive and reasonable
                            left = max(0.0, left)
                            top = max(0.0, top)
                            width = max(1.0, width)  # At least 1 pixel
                            height = max(1.0, height)  # At least 1 pixel
                            
                            # Warn if region seems too large (likely invalid)
                            if width > 8000 or height > 6000:
                                if not messagebox.askyesno(
                                    "Large Region Warning",
                                    f"Warning: The specified region is very large:\n"
                                    f"Width: {width}px, Height: {height}px\n\n"
                                    f"Is this correct? Large regions may impact performance."
                                ):
                                    return  # Cancel save if user says no
                        
                        # Update region
                        game_config["region"] = {
                            "use_percentages": use_percentages,
                            "left": left,
                            "top": top,
                            "width": width,
                            "height": height
                        }
                        
                        # Mark that we need restart for region changes
                        self.needs_restart = True
            
            # Save to file (with backup)
            try:
                # Create backup if file exists
                if os.path.exists(self.config_file):
                    backup_file = self.config_file + ".backup"
                    try:
                        import shutil
                        shutil.copy2(self.config_file, backup_file)
                    except:
                        pass  # If backup fails, continue anyway
                
                # Write new config
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
            except Exception as save_error:
                messagebox.showerror("Save Error", f"Failed to save settings: {save_error}")
                return  # Don't close window on save error
            
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
                        "• OCR Region settings (Per-game capture regions)\n"
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
                        "- OCR Region settings (per-game capture regions)\n"
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
