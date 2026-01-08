"""
Script to easily change the monitor ID for games in the config.
Helps when auto-detection isn't working or you want to manually set it.
"""

import os
import sys
import json

# Get the directory where this script is located
def get_base_dir():
    """Get the base directory - same folder as this script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")


def load_config():
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


def save_config(config):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def list_monitors():
    """List available monitors."""
    try:
        from mss import mss
        with mss() as sct:
            print("\nAvailable monitors:")
            for i, mon in enumerate(sct.monitors):
                print(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']}, {mon['top']})")
            return len(sct.monitors)
    except Exception as e:
        print(f"Error listing monitors: {e}")
        return 0


def main():
    config = load_config()
    if not config:
        return
    
    games = config.get("games", {})
    if not games:
        print("No games configured!")
        return
    
    print("=" * 60)
    print("Monitor ID Changer")
    print("=" * 60)
    
    # List available monitors
    num_monitors = list_monitors()
    
    # List games
    print("\nConfigured games:")
    game_list = list(games.keys())
    for i, game_name in enumerate(game_list, 1):
        current_monitor = games[game_name].get("monitor_index", config.get("settings", {}).get("monitor_index", 1))
        print(f"  {i}. {game_name} (Monitor: {current_monitor})")
    
    # Get game selection
    print()
    try:
        choice = input("Enter game number to change (or 'all' for all games): ").strip().lower()
        
        if choice == 'all':
            selected_games = game_list
        else:
            game_idx = int(choice) - 1
            if 0 <= game_idx < len(game_list):
                selected_games = [game_list[game_idx]]
            else:
                print("Invalid selection!")
                return
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return
    
    # Get monitor ID
    print()
    try:
        monitor_id = input(f"Enter monitor ID (0-{num_monitors-1}): ").strip()
        monitor_id = int(monitor_id)
        
        if monitor_id < 0 or monitor_id >= num_monitors:
            print(f"Invalid monitor ID! Must be between 0 and {num_monitors-1}")
            return
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return
    
    # Update monitor IDs
    print()
    for game_name in selected_games:
        games[game_name]["monitor_index"] = monitor_id
        print(f"✓ Set {game_name} to monitor {monitor_id}")
    
    # Save config
    if save_config(config):
        print(f"\n✓ Config saved to {CONFIG_FILE}")
        print("\nNote: The daemon will auto-detect the monitor, but this setting")
        print("will be used as a fallback if auto-detection fails.")
    else:
        print("\n✗ Failed to save config!")


if __name__ == "__main__":
    main()

