"""
Multi-Game Death Counter Daemon
Supports multiple games with configurable detection regions and keywords.
Automatically tracks deaths across different games.
Auto-detects which game is running by checking process names.

Requirements:
    pip install mss pillow pytesseract opencv-python numpy psutil
"""

import os
import time
import ctypes
import json
import traceback
import psutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
from PIL import Image
from mss import mss
import pytesseract

# =========================
# CONFIGURATION
# =========================
BASE_DIR = r"C:\1deathcounter"
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
STOP_FILE = os.path.join(BASE_DIR, "STOP")

DEBUG_RAW = os.path.join(BASE_DIR, "debug_capture_raw.png")
DEBUG_OCR = os.path.join(BASE_DIR, "debug_capture.png")
DEBUG_LOG = os.path.join(BASE_DIR, "debug.log")

DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
CURRENT_GAME_TXT = os.path.join(BASE_DIR, "current_game.txt")  # Current game name for Streamer.bot
CURRENT_DEATHS_TXT = os.path.join(BASE_DIR, "current_deaths.txt")  # Current game death count for Streamer.bot
TOTAL_DEATHS_TXT = os.path.join(BASE_DIR, "total_deaths.txt")  # Total deaths across all games for Streamer.bot

TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
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
        "region": {"left": 520, "top": 470, "width": 880, "height": 200},
        "keywords": ["YOUDIED", "YOUDIE", "DIED"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["eldenring.exe", "elden ring.exe"],  # Process names to detect
    },
    "Dark Souls 3": {
        "region": {"left": 520, "top": 470, "width": 880, "height": 200},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsiii.exe", "dark souls iii.exe"],
    },
    "Dark Souls Remastered": {
        "region": {"left": 520, "top": 470, "width": 880, "height": 200},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsremastered.exe", "dark souls remastered.exe"],
    },
    "Dark Souls II: Scholar of the First Sin": {
        "region": {"left": 520, "top": 470, "width": 880, "height": 200},
        "keywords": ["YOUDIED", "YOUDIE", "YOUD1ED", "YOUDlED", "YOUDI", "OUDIED", "YOUDIE0"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
        "monitor_index": 2,
        "process_names": ["darksoulsii.exe", "dark souls ii.exe", "darksouls2.exe"],
    },
    "Sekiro": {
        "region": {"left": 520, "top": 470, "width": 880, "height": 200},
        "keywords": ["YOUDIED", "YOUDIE", "DEATH"],
        "tesseract_config": "--oem 3 --psm 7 -c tessedit_char_whitelist=YOUDIEADFT",
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
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(f"{ts} {msg}\n")
    print(msg)  # Also print to console


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
        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        log(f"LOCK ERROR: {e}")
        return False


def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
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
def grab_region(sct: mss, monitor_index: int, region: dict) -> Image.Image:
    """Capture a region from the specified monitor."""
    # mss uses 0-indexed monitors (0 is all monitors, 1+ are individual)
    # But we'll use 1-indexed for user convenience
    actual_index = monitor_index if monitor_index == 0 else monitor_index
    
    if actual_index >= len(sct.monitors):
        log(f"WARNING: Monitor {monitor_index} not found. Using monitor 1.")
        actual_index = 1
    
    mon = sct.monitors[actual_index]
    abs_region = {
        "left": mon["left"] + region["left"],
        "top": mon["top"] + region["top"],
        "width": region["width"],
        "height": region["height"],
    }
    grab = sct.grab(abs_region)
    return Image.frombytes("RGB", grab.size, grab.rgb)


def preprocess_for_ocr(img_rgb: Image.Image) -> Tuple[Image.Image, Dict]:
    """
    Preprocess image for OCR with multiple fallback strategies.
    Fixes the black image issue by using robust preprocessing methods.
    """
    rgb = np.array(img_rgb)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    
    def upscale(img_cv):
        """Upscale image 2x for better OCR."""
        return cv2.resize(img_cv, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # Strategy 1: Try HSV red mask (for "YOU DIED" red text)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    # Wide red thresholds (both low and high hue ranges)
    lower1 = np.array([0, 30, 30], dtype=np.uint8)
    upper1 = np.array([15, 255, 255], dtype=np.uint8)
    lower2 = np.array([165, 30, 30], dtype=np.uint8)
    upper2 = np.array([180, 255, 255], dtype=np.uint8)
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Clean noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    white = int(cv2.countNonZero(mask))
    total = int(mask.shape[0] * mask.shape[1])
    coverage = white / max(1, total)
    
    info = {"mode": "HSV_RED", "coverage": coverage}
    
    # Use red mask if coverage is reasonable (at least 0.5% of image)
    if coverage >= 0.005:
        # Invert mask: white text on black background -> black text on white
        inv = cv2.bitwise_not(mask)
        out = upscale(inv)
        return Image.fromarray(out), info
    
    # Strategy 2: Grayscale with adaptive threshold (works for any text color)
    # This fallback ensures we NEVER get a black image - adaptive threshold always produces output
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thr_adapt = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    # Invert: make text dark on light background (Tesseract prefers dark text on light)
    thr_adapt_inv = cv2.bitwise_not(thr_adapt)
    out = upscale(thr_adapt_inv)
    info["mode"] = "ADAPTIVE_THRESHOLD"
    info["coverage"] = 0.0  # Set coverage for consistency
    return Image.fromarray(out), info


def ocr_text(img_for_ocr: Image.Image, tesseract_config: str) -> str:
    """Extract text from image using OCR."""
    try:
        text = pytesseract.image_to_string(img_for_ocr, lang="eng", config=tesseract_config)
        # Remove all non-alphabetic characters and uppercase
        clean = "".join(c for c in text.upper() if c.isalpha())
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
    
    if not os.path.exists(TESSERACT_EXE):
        log(f"ERROR: Tesseract not found at: {TESSERACT_EXE}")
        log("Please install Tesseract OCR or update TESSERACT_EXE path.")
        return
    
    config = load_config()
    settings = config["settings"]
    games = config["games"]
    
    if not games:
        log("ERROR: No games configured!")
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
    
    with mss() as sct:
        log(f"Available monitors: {len(sct.monitors)}")
        for i, mon in enumerate(sct.monitors):
            log(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
        
        monitor_index = game_config.get("monitor_index", settings["monitor_index"])
        region = game_config.get("region", {})
        keywords = game_config.get("keywords", ["YOUDIED"])
        tesseract_config = game_config.get("tesseract_config", "--oem 3 --psm 7")
        
        # Auto-detection check interval (check every 30 ticks = ~9 seconds at 0.3s tick)
        auto_detect_interval = 30
        last_auto_detect_tick = 0
        
        while True:
            if os.path.exists(STOP_FILE):
                log("STOP file detected. Exiting cleanly.")
                break
            
            state["tick"] += 1
            now = time.time()
            
            # Auto-detect game periodically
            if state["tick"] - last_auto_detect_tick >= auto_detect_interval:
                detected_game = detect_game(games)
                if detected_game and detected_game in games and detected_game != current_game_name:
                    log(f"🔄 Game changed detected: {current_game_name} → {detected_game}")
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
                    # Update monitor and region settings
                    monitor_index = game_config.get("monitor_index", settings["monitor_index"])
                    region = game_config.get("region", {})
                    keywords = game_config.get("keywords", ["YOUDIED"])
                    tesseract_config = game_config.get("tesseract_config", "--oem 3 --psm 7")
                    log(f"Switched to: {current_game_name} | Monitor: {monitor_index} | Region: {region} | Deaths: {game_deaths}")
                last_auto_detect_tick = state["tick"]
            
            try:
                # Capture region
                img_rgb = grab_region(sct, monitor_index, region)
                
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
                
                clean = ocr_text(ocr_img, tesseract_config)
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
                    log(f"💀 DEATH COUNTED → Total: {state['total_deaths']} | "
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
    if not acquire_lock():
        print("Another instance is already running. Exiting.")
        raise SystemExit(0)
    
    try:
        main_loop()
    except KeyboardInterrupt:
        log("Daemon stopped (KeyboardInterrupt).")
    except Exception as e:
        log("FATAL ERROR: " + str(e))
        log(traceback.format_exc())
    finally:
        release_lock()
        log("Daemon shutdown complete.")

