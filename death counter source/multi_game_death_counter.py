"""
Multi-Game Death Counter Daemon
Supports multiple games with configurable detection regions and keywords.
Automatically tracks deaths across different games.
Auto-detects which game is running by checking process names.

Requirements:
    pip install mss pillow pytesseract opencv-python numpy psutil
"""

import os
import sys
import time
import ctypes
import json
import traceback
import subprocess
import psutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Windows API types for window detection
try:
    from ctypes import wintypes
except ImportError:
    wintypes = None

import cv2
import numpy as np
from PIL import Image
from mss import mss
import pytesseract

# =========================
# CONFIGURATION
# =========================
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
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
READY_FILE = os.path.join(BASE_DIR, "daemon.ready")  # Signal file created after full initialization
STOP_FILE = os.path.join(BASE_DIR, "STOP")

DEBUG_RAW = os.path.join(BASE_DIR, "debug_capture_raw.png")
DEBUG_OCR = os.path.join(BASE_DIR, "debug_capture.png")
DEBUG_LOG = os.path.join(BASE_DIR, "debug.log")

DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
CURRENT_GAME_TXT = os.path.join(BASE_DIR, "current_game.txt")  # Current game name for Streamer.bot
CURRENT_DEATHS_TXT = os.path.join(BASE_DIR, "current_deaths.txt")  # Current game death count for Streamer.bot
TOTAL_DEATHS_TXT = os.path.join(BASE_DIR, "total_deaths.txt")  # Total deaths across all games for Streamer.bot

# Find Tesseract executable - check common locations
def find_tesseract_executable():
    """Find Tesseract OCR executable in common installation locations."""
    # Common Tesseract installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.getenv('ProgramFiles', r'C:\Program Files'), 'Tesseract-OCR', 'tesseract.exe'),
        os.path.join(os.getenv('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Tesseract-OCR', 'tesseract.exe'),
    ]
    
    # Check if tesseract is in PATH
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return 'tesseract'  # Use command name if in PATH
    except:
        pass
    
    # Check common paths
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Default fallback
    return r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TESSERACT_EXE = find_tesseract_executable()
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

# Default settings
DEFAULT_SETTINGS = {
    "tick_seconds": 0.30,
    "debug_every_ticks": 30,
    "consecutive_hits": 2,
    "cooldown_seconds": 8.0,
    "monitor_index": 1,  # 1-indexed (monitor 1 is primary)
}

# =========================
# DEFAULT GAME CONFIGS
# =========================
DEFAULT_GAMES = {
    "Elden Ring": {
        "region": {"use_percentages": True, "left": 0.2708, "top": 0.4352, "width": 0.4583, "height": 0.1852},
        "keywords": ["YOUDIED", "YOUDIE", "DIED"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["eldenring.exe", "elden ring.exe"],  # Process names to detect
    },
    "Dark Souls 3": {
        "region": {"use_percentages": True, "left": 0.2708, "top": 0.4352, "width": 0.4583, "height": 0.1852},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsiii.exe", "dark souls iii.exe"],
    },
    "Dark Souls Remastered": {
        "region": {"use_percentages": True, "left": 0.2708, "top": 0.4352, "width": 0.4583, "height": 0.1852},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsremastered.exe", "dark souls remastered.exe"],
    },
    "Dark Souls II: Scholar of the First Sin": {
        "region": {"use_percentages": True, "left": 0.2708, "top": 0.4352, "width": 0.4583, "height": 0.1852},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsii.exe", "dark souls ii.exe", "darksouls2.exe"],
    },
    "Sekiro": {
        "region": {"use_percentages": True, "left": 0.3802, "top": 0.2685, "width": 0.2240, "height": 0.4074},
        "keywords": ["DEATH", "死"],
        "tesseract_config": "--oem 3 --psm 7",
        "tesseract_lang": "jpn+eng",
        "monitor_index": 2,
        "process_names": ["sekiro.exe"],
    },
}


# =========================
# DPI AWARENESS
# =========================
def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def move_console_to_top_right():
    """Move console window to top right corner so it doesn't interfere with capture."""
    try:
        import sys
        if sys.platform == "win32":
            import os
            # Get console window handle
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # Get console window
            hwnd = kernel32.GetConsoleWindow()
            if hwnd:
                # Get screen dimensions
                screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                
                # Console window size (approximate)
                window_width = 800
                window_height = 600
                
                # Position in top right corner
                x = screen_width - window_width - 20  # 20px margin from right
                y = 20  # 20px margin from top
                
                # Move window
                user32.SetWindowPos(hwnd, 0, x, y, window_width, window_height, 0x0040)  # SWP_SHOWWINDOW
    except Exception:
        pass  # Silently fail if we can't move the window


# =========================
# LOGGING
# =========================
def log(msg: str):
    os.makedirs(BASE_DIR, exist_ok=True)
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8", errors='replace') as f:
            f.write(f"{ts} {msg}\n")
        # Print to console with error handling for Unicode
        try:
            print(msg)
        except UnicodeEncodeError:
            # If console can't handle Unicode, print ASCII version
            print(msg.encode('ascii', errors='replace').decode('ascii'))
    except Exception as e:
        # Silently fail if we can't write to log
        pass


# =========================
# CONFIGURATION MANAGEMENT
# =========================
def load_config() -> Dict:
    """Load game configurations from JSON file, or create default."""
    os.makedirs(BASE_DIR, exist_ok=True)
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            settings = {**DEFAULT_SETTINGS, **config.get("settings", {})}
            games = {**DEFAULT_GAMES, **config.get("games", {})}
            return {"settings": settings, "games": games}
        except Exception as e:
            log(f"Error loading config: {e}. Using defaults.")
    
    # Create default config file
    default_config = {
        "settings": DEFAULT_SETTINGS,
        "games": DEFAULT_GAMES,
        "current_game": list(DEFAULT_GAMES.keys())[0] if DEFAULT_GAMES else None
    }
    save_config(default_config)
    return default_config


def save_config(config: Dict):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log(f"Error saving config: {e}")


# =========================
# LOCK HANDLING
# =========================
def acquire_lock() -> bool:
    """Create lock file immediately - this is the first thing we do."""
    os.makedirs(BASE_DIR, exist_ok=True)
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                pid = f.read().strip()
            log(f"LOCK EXISTS: daemon.lock present (PID: {pid}). Exiting to avoid duplicates.")
        except:
            log("LOCK EXISTS: daemon.lock present. Exiting to avoid duplicates.")
        return False
    try:
        # Create lock file immediately - before any other initialization
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        # Force file system flush
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        log(f"LOCK CREATED: daemon.lock created with PID {os.getpid()}")
        return True
    except Exception as e:
        log(f"LOCK ERROR: {e}")
        return False


def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        if os.path.exists(READY_FILE):
            os.remove(READY_FILE)
    except Exception:
        pass


# =========================
# STATE MANAGEMENT
# =========================
def load_state() -> Dict:
    """Load state from JSON file."""
    if not os.path.exists(STATE_JSON):
        return {
            "total_deaths": 0,
            "game_deaths": {},
            "tick": 0,
            "streak": 0,
            "last_death_ts": 0.0,
            "current_game": None,
        }
    try:
        with open(STATE_JSON, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}
    
    state.setdefault("total_deaths", 0)
    state.setdefault("game_deaths", {})
    state.setdefault("tick", 0)
    state.setdefault("streak", 0)
    state.setdefault("last_death_ts", 0.0)
    state.setdefault("current_game", None)
    return state


def save_state(state: Dict):
    """Save state to JSON file."""
    try:
        with open(STATE_JSON, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Error saving state: {e}")


def write_text(deaths: int, game_name: str = None):
    """Write death count to text file for OBS."""
    try:
        # Write total deaths
        with open(DEATH_TXT, "w", encoding="utf-8") as f:
            f.write(str(deaths))
        
        # Also write per-game file if game name provided
        if game_name:
            game_txt = os.path.join(BASE_DIR, f"death_counter_{game_name.replace(' ', '_')}.txt")
            try:
                state = load_state()
                game_deaths = state.get("game_deaths", {}).get(game_name, 0)
                with open(game_txt, "w", encoding="utf-8") as f:
                    f.write(str(game_deaths))
            except Exception as e:
                log(f"Error writing game text file: {e}")
    except Exception as e:
        log(f"Error writing death text: {e}")


def write_chat_info(game_name: str, death_count: int):
    """Write simple text files for Streamer.bot chat command.
    Creates two separate files:
    - current_game.txt: Just the game name
    - current_deaths.txt: Just the death count
    This makes it easier for Streamer.bot to read.
    """
    try:
        # Write game name to separate file
        with open(CURRENT_GAME_TXT, "w", encoding="utf-8") as f:
            f.write(game_name)
        
        # Write death count to separate file
        with open(CURRENT_DEATHS_TXT, "w", encoding="utf-8") as f:
            f.write(str(death_count))
    except Exception as e:
        log(f"Error writing chat info: {e}")


def write_total_deaths(total_deaths: int):
    """Write total deaths across all games to a separate file for Streamer.bot."""
    try:
        with open(TOTAL_DEATHS_TXT, "w", encoding="utf-8") as f:
            f.write(str(total_deaths))
    except Exception as e:
        log(f"Error writing total deaths: {e}")


# =========================
# GAME DETECTION
# =========================
def get_running_processes() -> List[str]:
    """Get list of all running process names (lowercase, without .exe)."""
    processes = []
    try:
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                # Remove .exe extension for matching
                if proc_name.endswith('.exe'):
                    proc_name = proc_name[:-4]
                processes.append(proc_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        log(f"Error getting processes: {e}")
    return processes


def get_game_process(game_config: Dict) -> Optional[psutil.Process]:
    """Get the process object for the current game."""
    process_names = game_config.get("process_names", [])
    if not process_names:
        return None
    
    try:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower()
                if proc_name.endswith('.exe'):
                    proc_name = proc_name[:-4]
                
                for game_proc_name in process_names:
                    normalized = game_proc_name.lower()
                    if normalized.endswith('.exe'):
                        normalized = normalized[:-4]
                    
                    if normalized == proc_name:
                        return psutil.Process(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        log(f"Error finding game process: {e}")
    return None


def get_window_rect(process: psutil.Process) -> Optional[dict]:
    """Get the window rectangle for a process using Windows API."""
    try:
        # Windows API constants
        GW_OWNER = 4
        
        # Find window by process ID
        windows = []
        
        def enum_windows_callback(hwnd, lParam):
            try:
                if ctypes.windll.user32.IsWindowVisible(hwnd):
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value == process.pid:
                        # Check if it's not a child window
                        owner = ctypes.windll.user32.GetWindow(hwnd, GW_OWNER)
                        if owner == 0:
                            windows.append(hwnd)
            except:
                pass
            return True
        
        # Define callback type
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        callback = EnumWindowsProc(enum_windows_callback)
        
        # Find all windows for this process
        ctypes.windll.user32.EnumWindows(callback, None)
        
        if not windows:
            return None
        
        # Use the first (main) window
        hwnd = windows[0]
        
        # Get window rectangle
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long)]
        
        rect = RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        return {
            'left': rect.left,
            'top': rect.top,
            'right': rect.right,
            'bottom': rect.bottom,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top
        }
    except Exception:
        # Silently fail - will fall back to configured monitor
        return None


def find_monitor_for_window(window_rect: dict, monitors: List[dict]) -> Optional[int]:
    """Find which monitor contains the center of the window."""
    if not window_rect:
        return None
    
    # Get window center
    center_x = window_rect['left'] + window_rect['width'] // 2
    center_y = window_rect['top'] + window_rect['height'] // 2
    
    # Find monitor that contains this point
    for i, mon in enumerate(monitors):
        if (mon['left'] <= center_x < mon['left'] + mon['width'] and
            mon['top'] <= center_y < mon['top'] + mon['height']):
            return i
    
    return None


def detect_game(games: Dict) -> Optional[str]:
    """
    Auto-detect which game is currently running by checking process names.
    Returns the game name if detected, None otherwise.
    """
    running_procs = get_running_processes()
    
    # Check each game's process names
    for game_name, game_config in games.items():
        process_names = game_config.get("process_names", [])
        if not process_names:
            continue
        
        # Check if any of this game's process names are running
        for proc_name in process_names:
            # Normalize: remove .exe, lowercase
            normalized = proc_name.lower()
            if normalized.endswith('.exe'):
                normalized = normalized[:-4]
            
            # Check if this process is running
            if normalized in running_procs:
                log(f"Auto-detected game: {game_name} (process: {proc_name})")
                return game_name
    
    return None


# =========================
# IMAGE PROCESSING
# =========================
def grab_region(sct: mss, monitor_index: int, region: dict, game_config: Dict = None) -> Image.Image:
    """
    Capture a region from the specified monitor.
    Supports both absolute pixel coordinates and percentage-based coordinates for multi-resolution support.
    Note: Monitor auto-detection is now handled in the main loop with throttling
    to prevent race conditions. This function just uses the provided monitor_index.
    """
    
    # mss uses 0-indexed monitors (0 is all monitors, 1+ are individual)
    # Validate monitor index before using it
    num_monitors = len(sct.monitors)
    max_valid_index = num_monitors - 1
    
    if monitor_index < 0 or monitor_index > max_valid_index:
        # Invalid monitor index - use monitor 1 (primary) as fallback
        log(f"WARNING: Monitor {monitor_index} is invalid (valid range: 0-{max_valid_index}). Using monitor 1.")
        actual_index = 1
    else:
        actual_index = monitor_index
    
    mon = sct.monitors[actual_index]
    mon_width = mon["width"]
    mon_height = mon["height"]
    
    # Check if region uses percentage-based coordinates (0.0-1.0) or absolute pixels
    use_percentages = False
    if "use_percentages" in region:
        use_percentages = bool(region["use_percentages"])
    else:
        # Auto-detect: if left/top/width/height are all <= 1.0, assume percentages
        # Otherwise, if they're reasonable pixel values (> 10), use absolute
        left_val = region.get("left", 0)
        top_val = region.get("top", 0)
        width_val = region.get("width", 0)
        height_val = region.get("height", 0)
        
        # If all values are between 0 and 1, they're percentages
        # But exclude 0.0 values as they could be valid pixel coordinates
        if (0 < left_val <= 1 and 0 < top_val <= 1 and 
            0 < width_val <= 1 and 0 < height_val <= 1):
            use_percentages = True
    
    if use_percentages:
        # Convert percentage-based coordinates to absolute pixels
        # Percentages are relative to monitor resolution - works on ANY resolution including ultrawide!
        abs_region = {
            "left": int(mon["left"] + region["left"] * mon_width),
            "top": int(mon["top"] + region["top"] * mon_height),
            "width": int(region["width"] * mon_width),
            "height": int(region["height"] * mon_height),
        }
        # Only log on first use or when monitor resolution changes (to avoid spam)
        # This will be logged elsewhere if needed for debugging
    else:
        # Use absolute pixel coordinates (legacy mode)
        # Scale based on a reference resolution (1920x1080) if base_resolution is provided
        base_width = region.get("base_resolution_width", None)
        base_height = region.get("base_resolution_height", None)
        
        if base_width and base_height:
            # Scale region proportionally from base resolution to actual monitor resolution
            scale_x = mon_width / base_width
            scale_y = mon_height / base_height
            abs_region = {
                "left": int(mon["left"] + region["left"] * scale_x),
                "top": int(mon["top"] + region["top"] * scale_y),
                "width": int(region["width"] * scale_x),
                "height": int(region["height"] * scale_y),
            }
            log(f"Scaled region from {base_width}x{base_height} to {mon_width}x{mon_height}: {region} -> {abs_region}")
        else:
            # No scaling - use absolute coordinates as-is (legacy behavior)
            abs_region = {
                "left": mon["left"] + region["left"],
                "top": mon["top"] + region["top"],
                "width": region["width"],
                "height": region["height"],
            }
    
    # Capture at full quality (mss captures at native resolution)
    grab = sct.grab(abs_region)
    img = Image.frombytes("RGB", grab.size, grab.rgb)
    
    # If the captured region is very small, upscale it immediately to improve quality
    # This helps with pixelated text from small capture regions
    if img.size[0] < 200 or img.size[1] < 100:
        # Small region - upscale using high-quality resampling
        new_width = img.size[0] * 2
        new_height = img.size[1] * 2
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img


def preprocess_for_ocr(img_rgb: Image.Image) -> Tuple[Image.Image, Dict]:
    """
    Preprocess image for OCR with multiple fallback strategies.
    Improved upscaling and sharpening for better OCR accuracy and reduced pixelation.
    """
    # Convert PIL to numpy array
    rgb = np.array(img_rgb)
    
    # If image is very small, upscale it first before processing
    if rgb.shape[0] < 150 or rgb.shape[1] < 300:
        # Very small image - upscale using high-quality method
        scale_factor = max(300 / rgb.shape[1], 150 / rgb.shape[0])
        new_width = int(rgb.shape[1] * scale_factor)
        new_height = int(rgb.shape[0] * scale_factor)
        # Use PIL's LANCZOS for better quality upscaling
        img_rgb = img_rgb.resize((new_width, new_height), Image.Resampling.LANCZOS)
        rgb = np.array(img_rgb)
    
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def upscale(img_cv):
        """Upscale image 3x for better OCR quality and reduced pixelation."""
        # Use LANCZOS interpolation for better quality (slower but much better for text)
        # 3x upscale gives better results than 2x for pixelated text
        return cv2.resize(img_cv, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_LANCZOS4)
    
    # Strategy 1: Try HSV red mask (for "YOU DIED" red text)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    # Wide red thresholds (both low and high hue ranges)
    lower1 = np.array([0, 30, 30], dtype=np.uint8)
    upper1 = np.array([15, 255, 255], dtype=np.uint8)
    lower2 = np.array([165, 30, 30], dtype=np.uint8)
    upper2 = np.array([180, 255, 255], dtype=np.uint8)
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # Strategy 1b: Also detect white/bright text (for Sekiro white death message)
    # White/bright colors have high value (brightness) and low saturation
    white_lower = np.array([0, 0, 200], dtype=np.uint8)  # Low saturation, high brightness
    white_upper = np.array([180, 30, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    
    # Combine red and white masks
    mask = cv2.bitwise_or(red_mask, white_mask)
    
    # Clean noise with better morphology operations
    # Use smaller kernel for less aggressive cleaning (preserves text better)
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    # Gentle dilation to connect text characters
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    white = int(cv2.countNonZero(mask))
    total = int(mask.shape[0] * mask.shape[1])
    coverage = white / max(1, total)
    
    info = {"mode": "HSV_RED_WHITE", "coverage": coverage}
    
    # Use red/white mask if coverage is reasonable (at least 0.3% of image - lowered threshold)
    if coverage >= 0.003:
        # Invert mask: white text on black background -> black text on white
        inv = cv2.bitwise_not(mask)
        # Apply slight sharpening to improve text clarity
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
        inv = cv2.filter2D(inv, -1, kernel_sharpen)
        out = upscale(inv)
        return Image.fromarray(out), info
    
    # Strategy 2: Grayscale with adaptive threshold (works for any text color)
    # This fallback ensures we NEVER get a black image - adaptive threshold always produces output
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Use less blur to preserve text details
    gray_blur = cv2.GaussianBlur(gray, (3, 3), 0)
    # Apply unsharp mask for better text clarity
    gaussian = cv2.GaussianBlur(gray_blur, (0, 0), 2.0)
    unsharp = cv2.addWeighted(gray_blur, 1.5, gaussian, -0.5, 0)
    
    thr_adapt = cv2.adaptiveThreshold(
        unsharp, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    # Invert: make text dark on light background (Tesseract prefers dark text on light)
    thr_adapt_inv = cv2.bitwise_not(thr_adapt)
    # Apply slight sharpening to improve text clarity
    kernel_sharpen = np.array([[-1, -1, -1],
                               [-1,  9, -1],
                               [-1, -1, -1]])
    thr_adapt_inv = cv2.filter2D(thr_adapt_inv, -1, kernel_sharpen)
    out = upscale(thr_adapt_inv)
    info["mode"] = "ADAPTIVE_THRESHOLD"
    info["coverage"] = 0.0  # Set coverage for consistency
    return Image.fromarray(out), info


def ocr_text(img_for_ocr: Image.Image, tesseract_config: str, tesseract_lang: str = "eng") -> str:
    """Extract text from image using OCR. Supports multiple languages including Japanese."""
    try:
        text = pytesseract.image_to_string(img_for_ocr, lang=tesseract_lang, config=tesseract_config)
        # For English-only, remove non-alphabetic and uppercase
        # For Japanese/multi-language, keep all characters (including Japanese) but remove spaces
        if tesseract_lang == "eng" or (tesseract_lang.startswith("eng") and "+" not in tesseract_lang):
            clean = "".join(c for c in text.upper() if c.isalpha())
        else:
            # For Japanese/multi-language: keep all characters including Japanese, Chinese, etc.
            # Remove spaces and newlines, but keep all other characters
            clean = "".join(c for c in text if not c.isspace())
        return clean
    except Exception as e:
        log(f"OCR error: {e}")
        return ""


def contains_keyword(clean_text: str, keywords: List[str]) -> bool:
    """Check if cleaned text contains any keyword."""
    # Exclude false positives: enemy felled, target destroyed, etc.
    exclude_keywords = ["ENEMYFELLED", "ENEMYFELLE", "TARGETDESTROYED", "TARGETDESTROYE"]
    for exclude in exclude_keywords:
        if exclude in clean_text:
            return False
    
    return any(k in clean_text for k in keywords)


# =========================
# MAIN LOOP
# =========================
def main_loop():
    os.makedirs(BASE_DIR, exist_ok=True)
    enable_dpi_awareness()
    move_console_to_top_right()  # Move console window out of capture area
    
    # Check if Tesseract is available (either as file path or command)
    tesseract_available = False
    if TESSERACT_EXE == 'tesseract':
        # Check if command is available
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, timeout=2)
            tesseract_available = (result.returncode == 0)
        except:
            tesseract_available = False
    else:
        tesseract_available = os.path.exists(TESSERACT_EXE)
    
    if not tesseract_available:
        log(f"ERROR: Tesseract not found at: {TESSERACT_EXE}")
        log("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        log("Or ensure Tesseract is in your PATH.")
        log("Daemon will exit - Tesseract is required.")
        # Don't create ready file - daemon is not ready
        return
    
    config = load_config()
    settings = config["settings"]
    games = config["games"]
    
    if not games:
        log("ERROR: No games configured!")
        log("Daemon will exit - games configuration is required.")
        # Don't create ready file - daemon is not ready
        return
    
    # Create ready file EARLY - right after critical checks pass
    # This ensures GUI knows daemon is ready even if something later hangs
    # DO THIS BEFORE ANY LOGGING to avoid encoding issues
    ready_file_created = False
    try:
        # Ensure directory exists
        os.makedirs(BASE_DIR, exist_ok=True)
        # Create ready file
        ready_file_path = os.path.abspath(READY_FILE)  # Use absolute path
        with open(ready_file_path, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
            f.flush()  # Force write to disk
        # Force OS to sync file to disk
        import sys
        sys.stdout.flush()
        sys.stderr.flush()
        # Verify it was created
        if os.path.exists(ready_file_path):
            ready_file_created = True
            # Now safe to log (file is already created)
            try:
                log("Ready file created EARLY - critical checks passed.")
            except:
                pass  # If logging fails, that's OK - file is created
            print(f"Ready file created: {ready_file_path}")
            print(f"Ready file absolute path: {os.path.abspath(ready_file_path)}")
        else:
            print(f"WARNING: Ready file write succeeded but file doesn't exist!")
            print(f"Attempted path: {ready_file_path}")
            print(f"BASE_DIR: {BASE_DIR}")
            print(f"BASE_DIR exists: {os.path.exists(BASE_DIR)}")
    except Exception as e:
        error_msg = f"CRITICAL: Could not create ready file: {e}"
        # Try to log, but don't fail if logging fails
        try:
            log(error_msg)
        except:
            pass
        print(error_msg)
        # Write to startup error file
        try:
            STARTUP_ERROR_FILE = os.path.join(BASE_DIR, "daemon_startup_error.txt")
            with open(STARTUP_ERROR_FILE, "w", encoding="utf-8") as f:
                f.write(f"Failed to create ready file: {e}\n")
                f.write(f"BASE_DIR: {BASE_DIR}\n")
                f.write(f"READY_FILE: {READY_FILE}\n")
                f.write(f"BASE_DIR exists: {os.path.exists(BASE_DIR)}\n")
                f.write(f"BASE_DIR writable: {os.access(BASE_DIR, os.W_OK)}\n")
        except:
            pass
        # Don't continue - ready file is critical
        return
    
    if not ready_file_created:
        print("ERROR: Ready file was not created successfully!")
        return
    
    state = load_state()
    
    # Try auto-detection first
    detected_game = detect_game(games)
    if detected_game and detected_game in games:
        current_game_name = detected_game
        log(f"Auto-detected game: {current_game_name}")
    else:
        # Fall back to saved game or first game
        current_game_name = state.get("current_game") or config.get("current_game") or list(games.keys())[0]
        if detected_game is None:
            log(f"No game detected running. Using saved game: {current_game_name}")
    
    if current_game_name not in games:
        current_game_name = list(games.keys())[0]
    
    game_config = games[current_game_name]
    state["current_game"] = current_game_name
    
    # Get the current game's death count (not total)
    game_deaths = state.get("game_deaths", {}).get(current_game_name, 0)
    # Write initial text file so OBS has current game's count on startup
    write_text(game_deaths, current_game_name)
    # Write initial chat info file
    write_chat_info(current_game_name, game_deaths)
    # Write initial total deaths file
    write_total_deaths(state.get("total_deaths", 0))
    
    log("=" * 60)
    log("Multi-Game Death Counter Daemon Started")
    log(f"Current Game: {current_game_name}")
    log(f"Monitor: {game_config.get('monitor_index', settings['monitor_index'])}")
    log(f"Region: {game_config.get('region', {})}")
    log(f"Keywords: {game_config.get('keywords', [])}")
    log(f"Current Deaths - Total: {state['total_deaths']}, {current_game_name}: {state['game_deaths'].get(current_game_name, 0)}")
    log("=" * 60)
    
    # Ready file already created above - just verify it exists
    if os.path.exists(READY_FILE):
        log(f"READY_FILE verified: {READY_FILE}")
    else:
        log(f"WARNING: READY_FILE missing, recreating...")
        try:
            with open(READY_FILE, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            log(f"READY_FILE recreated: {READY_FILE}")
        except Exception as e:
            log(f"ERROR: Could not recreate ready file: {e}")
    
    # Now enter mss context - if this hangs, ready file already exists
    with mss() as sct:
        num_monitors = len(sct.monitors)
        log(f"Available monitors: {num_monitors}")
        for i, mon in enumerate(sct.monitors):
            log(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
        
        # Get configured monitor index and validate it
        monitor_index = game_config.get("monitor_index", settings["monitor_index"])
        
        # Validate monitor index - mss uses 0-indexed where 0 is "all monitors"
        # Valid indices are 0 (all) and 1 to (num_monitors-1) for individual monitors
        max_valid_index = num_monitors - 1
        if monitor_index < 0 or monitor_index > max_valid_index:
            log(f"WARNING: Configured monitor_index {monitor_index} is invalid (valid range: 0-{max_valid_index}). Using monitor 1.")
            monitor_index = 1  # Default to monitor 1 (primary display)
            # Update the config to save the corrected value
            game_config["monitor_index"] = monitor_index
            config["games"][current_game_name] = game_config
            save_config(config)
        
        region = game_config.get("region", {})
        keywords = game_config.get("keywords", ["YOUDIED"])
        tesseract_config = game_config.get("tesseract_config", "--oem 3 --psm 7")
        tesseract_lang = game_config.get("tesseract_lang", "eng")
        
        # Auto-detection check interval (check every 30 ticks = ~9 seconds at 0.3s tick)
        auto_detect_interval = 30
        last_auto_detect_tick = 0
        last_monitor_detect_tick = 0
        cached_monitor_index = monitor_index  # Cache the detected monitor
        
        # Flag to track if daemon has fully started (only run monitor detection after this)
        daemon_started = False
        startup_ticks = 10  # Wait 10 ticks (~3 seconds) after initialization before starting monitor detection
        
        while True:
            if os.path.exists(STOP_FILE):
                log("STOP file detected. Exiting cleanly.")
                break
            
            state["tick"] += 1
            now = time.time()
            
            # Mark daemon as started after initial startup period
            if not daemon_started and state["tick"] >= startup_ticks:
                daemon_started = True
                log("Monitor auto-detection enabled.")
            
            # Auto-detect game periodically
            if state["tick"] - last_auto_detect_tick >= auto_detect_interval:
                detected_game = detect_game(games)
                if detected_game and detected_game in games and detected_game != current_game_name:
                    log(f"Game changed detected: {current_game_name} -> {detected_game}")
                    current_game_name = detected_game
                    game_config = games[current_game_name]
                    state["current_game"] = current_game_name
                    # Update config file
                    config["current_game"] = current_game_name
                    save_config(config)
                    # Get the new game's death count
                    game_deaths = state.get("game_deaths", {}).get(current_game_name, 0)
                    # Write updated text files with the new game's count
                    write_text(game_deaths, current_game_name)
                    # Write updated chat info
                    write_chat_info(current_game_name, game_deaths)
                    # Write updated total deaths
                    write_total_deaths(state.get("total_deaths", 0))
                    # Update monitor and region settings - validate monitor index
                    monitor_index = game_config.get("monitor_index", settings["monitor_index"])
                    max_valid_index = len(sct.monitors) - 1
                    if monitor_index < 0 or monitor_index > max_valid_index:
                        log(f"WARNING: Monitor {monitor_index} invalid for {current_game_name} (valid: 0-{max_valid_index}). Using monitor 1.")
                        monitor_index = 1
                        game_config["monitor_index"] = monitor_index
                        config["games"][current_game_name] = game_config
                        save_config(config)
                    cached_monitor_index = monitor_index  # Reset cache when game changes
                    region = game_config.get("region", {})
                    keywords = game_config.get("keywords", ["YOUDIED"])
                    tesseract_config = game_config.get("tesseract_config", "--oem 3 --psm 7")
                    log(f"Switched to: {current_game_name} | Monitor: {monitor_index} | Region: {region} | Deaths: {game_deaths}")
                last_auto_detect_tick = state["tick"]
            
            # Auto-detect monitor periodically (throttled to prevent race conditions)
            # Only run after daemon has fully started to avoid race conditions during initialization
            if daemon_started and state["tick"] - last_monitor_detect_tick >= auto_detect_interval:
                try:
                    game_process = get_game_process(game_config)
                    if game_process:
                        window_rect = get_window_rect(game_process)
                        if window_rect:
                            detected_monitor = find_monitor_for_window(window_rect, sct.monitors)
                            if detected_monitor is not None and detected_monitor != cached_monitor_index:
                                log(f"Auto-detected monitor {detected_monitor} for game window (was using {cached_monitor_index})")
                                cached_monitor_index = detected_monitor
                except Exception:
                    # Fall back to configured monitor if auto-detection fails
                    pass
                last_monitor_detect_tick = state["tick"]
            
            try:
                # Capture region using cached monitor index (no EnumWindows call here)
                img_rgb = grab_region(sct, cached_monitor_index, region)
                
                # Save debug images periodically
                save_debug = (state["tick"] % settings["debug_every_ticks"] == 0)
                if save_debug:
                    try:
                        img_rgb.save(DEBUG_RAW)
                    except Exception as e:
                        log(f"DEBUG RAW SAVE ERROR: {e}")
                
                # Preprocess + OCR
                ocr_img, info = preprocess_for_ocr(img_rgb)
                
                if save_debug:
                    try:
                        ocr_img.save(DEBUG_OCR)
                    except Exception as e:
                        log(f"DEBUG OCR SAVE ERROR: {e}")
                
                clean = ocr_text(ocr_img, tesseract_config, tesseract_lang)
                detected = contains_keyword(clean, keywords)
                state["streak"] = (state["streak"] + 1) if detected else 0
                
                # Log periodically
                if state["tick"] % 10 == 0 or save_debug:
                    coverage = info.get('coverage', 0.0)
                    log(f"Tick={state['tick']} Game={current_game_name} Mode={info['mode']} "
                        f"Coverage={coverage:.4f} OCR='{clean}' "
                        f"Detected={detected} Streak={state['streak']}/{settings['consecutive_hits']}")
                
                # Count death: stable detection + cooldown
                cooldown_passed = (now - float(state["last_death_ts"])) >= settings["cooldown_seconds"]
                if state["streak"] >= settings["consecutive_hits"] and cooldown_passed:
                    state["total_deaths"] = int(state["total_deaths"]) + 1
                    state["game_deaths"].setdefault(current_game_name, 0)
                    state["game_deaths"][current_game_name] = int(state["game_deaths"][current_game_name]) + 1
                    state["last_death_ts"] = now
                    state["streak"] = 0
                    
                    # Save state and write text file
                    save_state(state)
                    # Write the current game's death count (not total)
                    game_deaths = state["game_deaths"].get(current_game_name, 0)
                    write_text(game_deaths, current_game_name)
                    # Write updated chat info
                    write_chat_info(current_game_name, game_deaths)
                    # Write updated total deaths
                    write_total_deaths(state["total_deaths"])
                    log(f"DEATH COUNTED -> Total: {state['total_deaths']} | "
                        f"{current_game_name}: {state['game_deaths'][current_game_name]}")
                
                # Save state periodically (every 10 ticks to reduce I/O)
                if state["tick"] % 10 == 0:
                    save_state(state)
                
            except Exception as e:
                log(f"Error in main loop: {e}")
                log(traceback.format_exc())
            
            time.sleep(settings["tick_seconds"])


# =========================
# ENTRYPOINT
# =========================
if __name__ == "__main__":
    # Create lock file FIRST - before anything else
    if not acquire_lock():
        print("Another instance is already running. Exiting.")
        raise SystemExit(0)
    
    # Create a startup error file to capture any immediate errors
    STARTUP_ERROR_FILE = os.path.join(BASE_DIR, "daemon_startup_error.txt")
    try:
        with open(STARTUP_ERROR_FILE, "w") as f:
            f.write("")  # Clear any old errors
    except:
        pass
    
    # Log startup immediately - use both log() and print() for visibility
    startup_msg = "=" * 70 + "\nDEATH COUNTER DAEMON STARTING\n" + "=" * 70
    print(startup_msg)
    log(startup_msg)
    log(f"PID: {os.getpid()}")
    log(f"BASE_DIR: {BASE_DIR}")
    log(f"LOCK_FILE: {LOCK_FILE}")
    log(f"READY_FILE: {READY_FILE}")
    log(f"Python: {sys.executable}")
    log(f"Script: {__file__}")
    
    # Also print critical info to stdout (visible in console)
    print(f"PID: {os.getpid()}")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"LOCK_FILE: {LOCK_FILE}")
    print(f"READY_FILE: {READY_FILE}")
    
    initialization_complete = False
    try:
        # Small delay to ensure lock file is written to disk
        time.sleep(0.1)
        print("Starting main_loop()...")
        log("Starting main_loop()...")
        # Call main_loop and track if it completes initialization
        main_loop()
        initialization_complete = True
        print("main_loop() completed normally")
        log("main_loop() completed normally")
    except KeyboardInterrupt:
        print("Daemon stopped (KeyboardInterrupt).")
        log("Daemon stopped (KeyboardInterrupt).")
    except Exception as e:
        error_msg = f"FATAL ERROR: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        log(error_msg)
        # Write error to startup error file
        try:
            with open(STARTUP_ERROR_FILE, "w", encoding="utf-8") as f:
                f.write(error_msg)
        except:
            pass
        # If we got here, initialization failed - remove ready file if it exists
        if os.path.exists(READY_FILE):
            try:
                os.remove(READY_FILE)
                print("Removed ready file due to error")
            except:
                pass
    finally:
        print("Releasing lock and shutting down...")
        release_lock()
        log("Daemon shutdown complete.")
        print("Daemon shutdown complete.")

