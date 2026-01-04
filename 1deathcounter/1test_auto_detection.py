"""
Test Auto-Detection of Games
Shows which games are currently detected and their process names.
"""

import os
import sys
import json
import psutil

BASE_DIR = r"C:\deathcounter"
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")


def get_running_processes():
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
        print(f"Error getting processes: {e}")
    return processes


def detect_game(games):
    """
    Auto-detect which game is currently running by checking process names.
    Returns the game name if detected, None otherwise.
    """
    running_procs = get_running_processes()
    
    detected_games = []
    
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
                detected_games.append({
                    "game": game_name,
                    "process": proc_name,
                    "matched_process": normalized
                })
                break  # Found a match for this game, move to next
    
    return detected_games


def main():
    print("=" * 70)
    print("AUTO-DETECTION TEST")
    print("=" * 70)
    
    # Load config
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Config file not found: {CONFIG_FILE}")
        return 1
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return 1
    
    games = config.get("games", {})
    if not games:
        print("[ERROR] No games configured")
        return 1
    
    print("\n[CONFIGURED GAMES]")
    print("-" * 70)
    for game_name, game_config in games.items():
        process_names = game_config.get("process_names", [])
        print(f"\n{game_name}:")
        if process_names:
            for proc in process_names:
                print(f"  - {proc}")
        else:
            print("  - No process names configured")
    
    print("\n" + "=" * 70)
    print("[CURRENT DETECTION]")
    print("-" * 70)
    
    # Get all running processes (for reference)
    all_procs = get_running_processes()
    
    # Detect games
    detected = detect_game(games)
    
    if detected:
        print(f"\n[OK] Detected {len(detected)} game(s) running:\n")
        for item in detected:
            print(f"  -> {item['game']}")
            print(f"     Process: {item['process']}")
            print(f"     Matched: {item['matched_process']}")
            print()
    else:
        print("\n[X] No games detected running")
        print("\n[INFO] Make sure one of the configured games is running.")
    
    # Show current game from config
    current_game = config.get("current_game")
    if current_game:
        print(f"\n[CURRENT GAME IN CONFIG]")
        print(f"  {current_game}")
        if detected and current_game not in [d['game'] for d in detected]:
            print(f"  [WARNING] Config says '{current_game}' but it's not detected running!")
            print(f"  The daemon will auto-switch when it detects a different game.")
    
    print("\n" + "=" * 70)
    print("[HOW IT WORKS]")
    print("-" * 70)
    print("The daemon checks for running processes every ~9 seconds (30 ticks).")
    print("When it detects a game process, it automatically switches to that game's")
    print("configuration (region, keywords, monitor, etc.).")
    print("\nTo test auto-detection:")
    print("  1. Start the daemon")
    print("  2. Launch a game (e.g., Elden Ring)")
    print("  3. Wait ~9 seconds")
    print("  4. Check the log or status - should show the game name")
    print("  5. Close the game, launch a different one")
    print("  6. Wait ~9 seconds - daemon should auto-switch")
    
    print("\n" + "=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

