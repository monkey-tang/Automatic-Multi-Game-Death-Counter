"""
One-time debug image capture script.
Captures the current game's region and saves both raw and preprocessed images.
Run this anytime to see what the OCR is seeing.
"""

import os
import sys
import subprocess
import ctypes
import json
from typing import Dict, Tuple

import cv2
import numpy as np
from PIL import Image
from mss import mss
import pytesseract

# Get the directory where this script is located
def get_base_dir():
    """Get the base directory - same folder as this script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")

# Try to find Tesseract - check common locations and PATH
def find_tesseract():
    """Find Tesseract OCR executable."""
    # Check if tesseract is in PATH
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return 'tesseract'  # Use command name if in PATH
    except:
        pass
    
    # Check common installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.getenv('ProgramFiles', r'C:\Program Files'), 'Tesseract-OCR', 'tesseract.exe'),
        os.path.join(os.getenv('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Tesseract-OCR', 'tesseract.exe'),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Default fallback
    return r"C:\Program Files\Tesseract-OCR\tesseract.exe"

tesseract_path = find_tesseract()
pytesseract.pytesseract.tesseract_cmd = tesseract_path

DEBUG_RAW = os.path.join(BASE_DIR, "debug_capture_raw.png")
DEBUG_OCR = os.path.join(BASE_DIR, "debug_capture.png")


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


# =========================
# CONFIGURATION MANAGEMENT
# =========================
def load_config() -> Dict:
    """Load game configurations from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"ERROR: Config file not found: {CONFIG_FILE}")
        return None
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


# =========================
# IMAGE PROCESSING
# =========================
def grab_region(sct: mss, monitor_index: int, region: dict) -> Image.Image:
    """Capture a region from the specified monitor."""
    actual_index = monitor_index if monitor_index == 0 else monitor_index
    
    if actual_index >= len(sct.monitors):
        print(f"WARNING: Monitor {monitor_index} not found. Using monitor 1.")
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
    Same as the main daemon script.
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
    info["coverage"] = 0.0
    return Image.fromarray(out), info


# =========================
# MAIN
# =========================
def main():
    enable_dpi_awareness()
    
    if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
        print(f"WARNING: Tesseract not found at: {pytesseract.pytesseract.tesseract_cmd}")
        print("OCR won't work, but images will still be captured.")
    
    config = load_config()
    if not config:
        return
    
    games = config.get("games", {})
    current_game = config.get("current_game")
    
    if not current_game or current_game not in games:
        print(f"ERROR: Current game '{current_game}' not found in config.")
        print(f"Available games: {list(games.keys())}")
        return
    
    game_config = games[current_game]
    region = game_config.get("region", {})
    monitor_index = game_config.get("monitor_index", config.get("settings", {}).get("monitor_index", 1))
    
    print("=" * 60)
    print("Debug Image Capture")
    print("=" * 60)
    print(f"Game: {current_game}")
    print(f"Monitor: {monitor_index}")
    print(f"Region: {region}")
    print()
    
    with mss() as sct:
        print(f"Available monitors: {len(sct.monitors)}")
        for i, mon in enumerate(sct.monitors):
            print(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
        print()
        
        # Capture region
        print("Capturing region...")
        img_rgb = grab_region(sct, monitor_index, region)
        
        # Save raw image
        img_rgb.save(DEBUG_RAW)
        print(f"✓ Raw image saved: {DEBUG_RAW}")
        print(f"  Size: {img_rgb.size[0]}x{img_rgb.size[1]}")
        
        # Preprocess
        print("Preprocessing for OCR...")
        ocr_img, info = preprocess_for_ocr(img_rgb)
        
        # Save processed image
        ocr_img.save(DEBUG_OCR)
        print(f"✓ Processed image saved: {DEBUG_OCR}")
        print(f"  Size: {ocr_img.size[0]}x{ocr_img.size[1]}")
        print(f"  Mode: {info['mode']}")
        if 'coverage' in info:
            print(f"  Coverage: {info['coverage']:.4f}")
        
        print()
        print("Done! Open the images to see what OCR is processing.")


if __name__ == "__main__":
    main()

