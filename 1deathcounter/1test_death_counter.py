"""
Simple Test Script for Death Counter
Tests if the death counter is working and updating text files correctly.
"""

import os
import time
import json
from datetime import datetime

BASE_DIR = r"C:\deathcounter"
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")
DEBUG_LOG = os.path.join(BASE_DIR, "debug.log")


def read_text_file(filepath):
    """Read and return content of text file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "FILE NOT FOUND"
    except Exception as e:
        return f"ERROR: {e}"


def read_json_file(filepath):
    """Read and return JSON content."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def get_latest_log_lines(n=10):
    """Get the last N lines from debug log."""
    try:
        if os.path.exists(DEBUG_LOG):
            with open(DEBUG_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return lines[-n:] if len(lines) > n else lines
        return []
    except Exception as e:
        return [f"Error reading log: {e}"]


def monitor_death_counter(duration_seconds=60, check_interval=2):
    """
    Monitor the death counter for a specified duration.
    Shows updates in real-time.
    """
    print("=" * 70)
    print("DEATH COUNTER MONITOR")
    print("=" * 70)
    print(f"Monitoring for {duration_seconds} seconds (checking every {check_interval}s)")
    print("Press Ctrl+C to stop early")
    print("=" * 70)
    
    start_time = time.time()
    last_total = None
    last_game_deaths = {}
    last_game = None
    
    try:
        while time.time() - start_time < duration_seconds:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
            
            print("=" * 70)
            print(f"Time: {int(time.time() - start_time)}s / {duration_seconds}s")
            print("=" * 70)
            
            # Read state
            state = read_json_file(STATE_JSON)
            config = read_json_file(CONFIG_FILE)
            
            # Read text files
            total_deaths_txt = read_text_file(DEATH_TXT)
            
            # Get current game
            current_game = None
            if state:
                current_game = state.get("current_game")
            if not current_game and config:
                current_game = config.get("current_game")
            
            # Get game-specific text file
            game_deaths_txt = "N/A"
            if current_game:
                game_txt = os.path.join(BASE_DIR, f"death_counter_{current_game.replace(' ', '_')}.txt")
                game_deaths_txt = read_text_file(game_txt)
            
            # Display current state
            print(f"\n[STATE] CURRENT STATE:")
            print(f"   Total Deaths (text file): {total_deaths_txt}")
            print(f"   Current Game: {current_game or 'Unknown'}")
            if current_game:
                print(f"   Game Deaths ({current_game}): {game_deaths_txt}")
            
            if state:
                print(f"\n[STATE.JSON] FROM STATE.JSON:")
                print(f"   Total Deaths: {state.get('total_deaths', 0)}")
                print(f"   Current Game: {state.get('current_game', 'Unknown')}")
                print(f"   Tick: {state.get('tick', 0)}")
                print(f"   Streak: {state.get('streak', 0)}")
                
                game_deaths = state.get('game_deaths', {})
                if game_deaths:
                    print(f"   Per-Game Deaths:")
                    for game, deaths in game_deaths.items():
                        print(f"      - {game}: {deaths}")
            
            # Check for changes
            if state:
                current_total = state.get('total_deaths', 0)
                if last_total is not None and current_total != last_total:
                    print(f"\n[!] CHANGE DETECTED!")
                    print(f"   Total deaths changed: {last_total} -> {current_total}")
                
                current_game_deaths = state.get('game_deaths', {})
                for game, deaths in current_game_deaths.items():
                    if game in last_game_deaths and deaths != last_game_deaths[game]:
                        print(f"\n[!] CHANGE DETECTED!")
                        print(f"   {game} deaths changed: {last_game_deaths[game]} -> {deaths}")
                
                if current_game != last_game:
                    print(f"\n[!] GAME CHANGED!")
                    print(f"   {last_game} -> {current_game}")
                
                last_total = current_total
                last_game_deaths = current_game_deaths.copy()
                last_game = current_game
            
            # Show recent log entries
            print(f"\n[LOG] RECENT LOG ENTRIES:")
            log_lines = get_latest_log_lines(5)
            for line in log_lines:
                print(f"   {line.rstrip()}")
            
            print(f"\n{'=' * 70}")
            print(f"Next update in {check_interval} seconds... (Ctrl+C to stop)")
            
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    
    print("\n" + "=" * 70)
    print("MONITORING COMPLETE")
    print("=" * 70)


def show_current_status():
    """Show current status of death counter."""
    print("=" * 70)
    print("DEATH COUNTER STATUS")
    print("=" * 70)
    
    # Check if daemon is running
    lock_file = os.path.join(BASE_DIR, "daemon.lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                pid = f.read().strip()
            print(f"[OK] Daemon is RUNNING (PID: {pid})")
        except:
            print("[OK] Daemon is RUNNING (lock file exists)")
    else:
        print("[X] Daemon is NOT RUNNING (no lock file found)")
    
    print()
    
    # Read files
    state = read_json_file(STATE_JSON)
    config = read_json_file(CONFIG_FILE)
    
    # Text files
    total_deaths_txt = read_text_file(DEATH_TXT)
    print(f"[FILE] death_counter.txt: {total_deaths_txt}")
    
    if state:
        current_game = state.get("current_game")
        if current_game:
            game_txt = os.path.join(BASE_DIR, f"death_counter_{current_game.replace(' ', '_')}.txt")
            game_deaths_txt = read_text_file(game_txt)
            print(f"[FILE] death_counter_{current_game.replace(' ', '_')}.txt: {game_deaths_txt}")
    
    print()
    
    # State info
    if state:
        print("[STATE] STATE.JSON:")
        print(f"   Total Deaths: {state.get('total_deaths', 0)}")
        print(f"   Current Game: {state.get('current_game', 'Unknown')}")
        print(f"   Tick: {state.get('tick', 0)}")
        print(f"   Streak: {state.get('streak', 0)}")
        
        game_deaths = state.get('game_deaths', {})
        if game_deaths:
            print("   Per-Game Deaths:")
            for game, deaths in game_deaths.items():
                print(f"      - {game}: {deaths}")
    else:
        print("[X] STATE.JSON not found")
    
    print()
    
    # Config info
    if config:
        print("[CONFIG] CONFIG:")
        current_game = config.get("current_game", "Not set")
        print(f"   Current Game: {current_game}")
        games = config.get("games", {})
        print(f"   Configured Games: {', '.join(games.keys())}")
    else:
        print("[X] CONFIG.JSON not found")
    
    print()
    
    # Recent log
    print("[LOG] RECENT LOG (last 10 lines):")
    log_lines = get_latest_log_lines(10)
    if log_lines:
        for line in log_lines:
            # Remove emoji characters that can't be displayed in Windows console
            clean_line = line.rstrip().encode('ascii', 'ignore').decode('ascii')
            print(f"   {clean_line}")
    else:
        print("   No log entries found")
    
    print("=" * 70)


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        duration = 60
        if len(sys.argv) > 2:
            try:
                duration = int(sys.argv[2])
            except:
                pass
        monitor_death_counter(duration)
    else:
        show_current_status()
        print("\n[TIP] Run 'python test_death_counter.py monitor [seconds]' to watch for changes")
        print("   Example: python test_death_counter.py monitor 120")


if __name__ == "__main__":
    main()

