"""
Manually Switch Game
Switch the death counter to a specific game manually.

Usage:
    python switch_game_manual.py "Elden Ring"
    python switch_game_manual.py "Dark Souls 3"
"""

import os
import sys
import json

BASE_DIR = r"C:\1deathcounter"
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")


def load_config():
    """Load game configurations from JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Config file not found: {CONFIG_FILE}")
        return None
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return None


def load_state():
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
    except:
        state = {}
    
    state.setdefault("total_deaths", 0)
    state.setdefault("game_deaths", {})
    state.setdefault("tick", 0)
    state.setdefault("streak", 0)
    state.setdefault("last_death_ts", 0.0)
    state.setdefault("current_game", None)
    return state


def save_config(config):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")
        return False


def save_state(state):
    """Save state to JSON file."""
    try:
        with open(STATE_JSON, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save state: {e}")
        return False


def write_text(deaths, game_name):
    """Write death count to text file."""
    try:
        # Write main file
        with open(DEATH_TXT, "w", encoding="utf-8") as f:
            f.write(str(deaths))
        
        # Write per-game file
        if game_name:
            game_txt = os.path.join(BASE_DIR, f"death_counter_{game_name.replace(' ', '_')}.txt")
            try:
                state = load_state()
                game_deaths = state.get("game_deaths", {}).get(game_name, 0)
                with open(game_txt, "w", encoding="utf-8") as f:
                    f.write(str(game_deaths))
            except Exception as e:
                print(f"[WARNING] Could not write per-game file: {e}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write text file: {e}")
        return False


def switch_game(game_name):
    """Switch to the specified game."""
    print("=" * 70)
    print("MANUAL GAME SWITCH")
    print("=" * 70)
    
    # Load config
    config = load_config()
    if not config:
        return False
    
    games = config.get("games", {})
    if not games:
        print("[ERROR] No games configured")
        return False
    
    # Check if game exists
    if game_name not in games:
        print(f"[ERROR] Game '{game_name}' not found in configuration.")
        print(f"\nAvailable games:")
        for name in games.keys():
            print(f"  - {name}")
        return False
    
    # Load state
    state = load_state()
    old_game = state.get("current_game", "Unknown")
    
    # Update state
    state["current_game"] = game_name
    
    # Update config
    config["current_game"] = game_name
    
    # Get the game's death count
    game_deaths = state.get("game_deaths", {}).get(game_name, 0)
    
    # Save files
    if not save_state(state):
        return False
    
    if not save_config(config):
        return False
    
    # Update text files
    write_text(game_deaths, game_name)
    
    # Show info
    game_config = games[game_name]
    print(f"\n[OK] Switched from '{old_game}' to '{game_name}'")
    print(f"\nGame Info:")
    print(f"  Deaths: {game_deaths}")
    print(f"  Monitor: {game_config.get('monitor_index', 'default')}")
    print(f"  Region: {game_config.get('region', {})}")
    print(f"  Keywords: {game_config.get('keywords', [])}")
    
    print(f"\n[OK] Text files updated:")
    print(f"  - {DEATH_TXT} -> {game_deaths}")
    print(f"  - death_counter_{game_name.replace(' ', '_')}.txt -> {game_deaths}")
    
    print("\n" + "=" * 70)
    print("[NOTE] The daemon will continue running with the new game.")
    print("       Auto-detection will override this if it detects a different game.")
    print("=" * 70)
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python switch_game_manual.py \"Game Name\"")
        print("\nExamples:")
        print('  python switch_game_manual.py "Elden Ring"')
        print('  python switch_game_manual.py "Dark Souls 3"')
        print('  python switch_game_manual.py "Dark Souls Remastered"')
        print('  python switch_game_manual.py "Sekiro"')
        return 1
    
    game_name = sys.argv[1]
    
    if switch_game(game_name):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

