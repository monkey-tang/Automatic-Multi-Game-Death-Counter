"""
Log File Monitoring Module for Death Detection
Monitors game log files for death-related entries using file system watchers.

Requirements:
    pip install watchdog

Compatible with Windows 10/11.
"""

import os
import re
import time
import threading
from typing import Dict, List, Optional, Callable

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Fallback file polling if watchdog not available
DEFAULT_POLL_INTERVAL = 0.5  # seconds


if WATCHDOG_AVAILABLE:
    class LogFileHandler(FileSystemEventHandler):
        """Handles file system events for log monitoring."""
        
        def __init__(self, callback: Callable[[], None], patterns: List[str], encoding: str = "utf-8", log_paths: Optional[List[str]] = None):
            super().__init__()
            self.callback = callback
            self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            self.encoding = encoding
            self.last_position = {}  # Track file position per file
            # Store normalized log paths for filtering (watchdog watches directories, not files)
            self.log_paths_normalized = set()
            if log_paths:
                for path in log_paths:
                    try:
                        self.log_paths_normalized.add(os.path.normpath(os.path.abspath(path)))
                    except Exception:
                        pass
        
        def on_modified(self, event):
            """Handle file modification events."""
            if not event.is_directory and hasattr(event, 'src_path'):
                self._check_file(event.src_path)
        
        def on_created(self, event):
            """Handle file creation events (e.g., log rotation)."""
            if not event.is_directory and hasattr(event, 'src_path'):
                self._check_file(event.src_path)
                # Reset position tracking for new file
                filepath_normalized = os.path.normpath(os.path.abspath(event.src_path))
                if filepath_normalized in self.last_position:
                    del self.last_position[filepath_normalized]
        
        def _check_file(self, filepath: str):
            """Check file for new content matching patterns."""
            try:
                # Normalize path for comparison (Windows path handling)
                filepath_normalized = os.path.normpath(os.path.abspath(filepath))
                
                # Filter: Only process files that are in our watch list
                # (watchdog watches entire directories, so we need to filter by specific files)
                if self.log_paths_normalized and filepath_normalized not in self.log_paths_normalized:
                    return  # Not a file we're watching
                
                if not os.path.exists(filepath_normalized) or not os.path.isfile(filepath_normalized):
                    return
                
                # Get current file size
                current_size = os.path.getsize(filepath_normalized)
                
                # Get last read position (use normalized path as key)
                last_pos = self.last_position.get(filepath_normalized, 0)
                
                # Only read new content
                if current_size <= last_pos:
                    return
                
                # Read new content
                with open(filepath_normalized, 'r', encoding=self.encoding, errors='ignore') as f:
                    f.seek(last_pos)
                    new_content = f.read()
                    self.last_position[filepath_normalized] = current_size
                
                # Check for patterns in new content
                for line in new_content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    for pattern in self.patterns:
                        if pattern.search(line):
                            self.callback()  # Callback takes no arguments
                            break  # Only trigger once per line
                            
            except (PermissionError, IOError, UnicodeDecodeError) as e:
                # Silently handle file access errors
                pass
            except Exception:
                # Silently handle other errors to prevent crashes
                pass
else:
    # Dummy class when watchdog not available (only used for type hints)
    class LogFileHandler:
        """Dummy class when watchdog not available."""
        pass


class LogMonitor:
    """
    Monitors log files for death-related entries.
    Supports file watching and polling fallback.
    """
    
    def __init__(self, game_config: Dict, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize log monitor for a game configuration.
        
        Args:
            game_config: Game configuration dict with optional 'log_monitoring' section
            log_callback: Optional callback function for logging (for debugging)
        """
        self.game_config = game_config
        self.log_callback = log_callback or (lambda msg: None)
        
        # Get log monitoring config
        self.config = game_config.get("log_monitoring", {})
        self.enabled = self.config.get("enabled", False)
        
        if not self.enabled:
            return
        
        # Get log paths (support environment variable expansion)
        self.log_paths = []
        raw_paths = self.config.get("log_paths", [])
        for path in raw_paths:
            # Expand environment variables (e.g., %USERPROFILE%)
            expanded = os.path.expandvars(os.path.expanduser(path))
            if os.path.exists(expanded) or os.path.exists(os.path.dirname(expanded)):
                self.log_paths.append(expanded)
        
        # Get patterns
        self.patterns = self.config.get("patterns", ["YOU DIED", "Death", "died"])
        self.encoding = self.config.get("encoding", "utf-8")
        self.watch_from_end = self.config.get("watch_from_end", True)
        
        # Detection callback
        self.detection_callback = None
        
        # File handler and observer
        self.handler = None
        self.observer = None
        self.poll_thread = None
        self.stop_polling = False
        self.lock = threading.Lock()
        
        # File positions for polling mode
        self.file_positions = {}
        
        # Initialize if paths are configured
        if self.log_paths:
            self._initialize()
    
    def _initialize(self):
        """Initialize file watchers."""
        if not self.log_paths:
            return
        
        # Initialize file positions if watching from end
        if self.watch_from_end:
            for path in self.log_paths:
                try:
                    if os.path.exists(path):
                        self.file_positions[path] = os.path.getsize(path)
                    else:
                        self.file_positions[path] = 0
                except:
                    self.file_positions[path] = 0
        
        # Use watchdog if available
        if WATCHDOG_AVAILABLE:
            try:
                # Create handler with log paths for file filtering
                self.handler = LogFileHandler(
                    callback=self._on_detection,
                    patterns=self.patterns,
                    encoding=self.encoding,
                    log_paths=self.log_paths  # Pass log paths for filtering
                )
                self.observer = Observer()
                
                # Watch directories (watchdog watches directories, not individual files)
                watched_dirs = set()
                for path in self.log_paths:
                    dir_path = os.path.dirname(os.path.abspath(path))
                    if os.path.exists(dir_path) and dir_path not in watched_dirs:
                        watched_dirs.add(dir_path)
                        try:
                            self.observer.schedule(self.handler, dir_path, recursive=False)
                        except Exception as e:
                            self.log_callback(f"LogMonitor: Failed to watch directory {dir_path}: {e}")
                
                if watched_dirs:
                    self.observer.start()
                    self.log_callback(f"LogMonitor: Watching {len(watched_dirs)} directory(ies) with {len(self.log_paths)} log file(s)")
            except Exception as e:
                self.log_callback(f"LogMonitor: Failed to initialize watchdog: {e}")
                # Fall back to polling
                self._start_polling()
        else:
            # Use polling fallback
            self._start_polling()
    
    def _start_polling(self):
        """Start polling mode (fallback when watchdog not available)."""
        self.log_callback("LogMonitor: Using polling mode (watchdog not available)")
        self.stop_polling = False
        
        def poll_files():
            poll_interval = self.config.get("poll_interval", DEFAULT_POLL_INTERVAL)
            while not self.stop_polling:
                try:
                    self._poll_files()
                except Exception:
                    pass  # Silently handle errors
                time.sleep(poll_interval)
        
        self.poll_thread = threading.Thread(target=poll_files, daemon=True)
        self.poll_thread.start()
    
    def _poll_files(self):
        """Poll log files for new content."""
        with self.lock:
            for path in self.log_paths:
                try:
                    if not os.path.exists(path):
                        continue
                    
                    current_size = os.path.getsize(path)
                    last_pos = self.file_positions.get(path, 0)
                    
                    if current_size <= last_pos:
                        continue
                    
                    # Read new content
                    with open(path, 'r', encoding=self.encoding, errors='ignore') as f:
                        f.seek(last_pos)
                        new_content = f.read()
                        self.file_positions[path] = current_size
                    
                    # Check for patterns
                    for line in new_content.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        
                        for pattern in self.patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self._on_detection()  # No argument needed
                                break
                                
                except (PermissionError, IOError, UnicodeDecodeError):
                    pass
                except Exception:
                    pass
    
    def _on_detection(self):
        """Handle detection of death pattern in log."""
        if self.detection_callback:
            try:
                # Callback takes no arguments (just signals detection)
                self.detection_callback()
            except Exception:
                pass  # Silently handle callback errors
    
    def set_detection_callback(self, callback: Callable[[], None]):
        """
        Set callback function to call when death is detected.
        
        Args:
            callback: Function to call (no arguments) - called when pattern is found in log
        """
        self.detection_callback = callback
    
    def start(self):
        """Start monitoring (if not already started)."""
        if not self.enabled or not self.log_paths:
            return
        
        # Already initialized in __init__, just ensure it's running
        if WATCHDOG_AVAILABLE and self.observer and not self.observer.is_alive():
            try:
                self.observer.start()
            except Exception:
                pass
    
    def stop(self):
        """Stop monitoring."""
        with self.lock:
            self.stop_polling = True
            
            if self.observer:
                try:
                    self.observer.stop()
                    self.observer.join(timeout=2.0)
                except Exception:
                    pass
                self.observer = None
            
            if self.poll_thread and self.poll_thread.is_alive():
                # Wait for polling thread to stop
                time.sleep(0.5)
            
            self.handler = None
            self.detection_callback = None
    
    def is_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self.enabled and bool(self.log_paths)
    
    def update_config(self, game_config: Dict):
        """
        Update configuration when game switches.
        Stops current monitoring and restarts with new config.
        """
        self.stop()
        self.game_config = game_config
        self.config = game_config.get("log_monitoring", {})
        self.enabled = self.config.get("enabled", False)
        
        if self.enabled:
            raw_paths = self.config.get("log_paths", [])
            self.log_paths = []
            for path in raw_paths:
                expanded = os.path.expandvars(os.path.expanduser(path))
                if os.path.exists(expanded) or os.path.exists(os.path.dirname(expanded)):
                    self.log_paths.append(expanded)
            
            self.patterns = self.config.get("patterns", ["YOU DIED", "Death", "died"])
            self.encoding = self.config.get("encoding", "utf-8")
            self.watch_from_end = self.config.get("watch_from_end", True)
            self.file_positions = {}
            
            if self.log_paths:
                self._initialize()
                self.start()
