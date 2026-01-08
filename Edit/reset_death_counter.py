"""
Reset Death Counter
Simple script to reset all death counts to 0.
Works with any installation location.
"""

import os
import sys
import json

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
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")


def reset_deaths():
    """Reset all death counts to 0."""
    print("=" * 60)
    print("RESET DEATH COUNTER")
    print("=" * 60)
    print(f"Installation folder: {BASE_DIR}")
    print()
    
    # Reset state JSON
    if os.path.exists(STATE_JSON):
        try:
            # Load existing state to preserve game list structure
            with open(STATE_JSON, "r", encoding="utf-8") as f:
                old_state = json.load(f)
            
            # Create new state with zeros but preserve game structure
            new_state = {
                "total_deaths": 0,
                "game_deaths": {},
                "tick": old_state.get("tick", 0),  # Keep tick count
                "streak": 0,
                "last_death_ts": 0.0,
                "current_game": old_state.get("current_game", None),
            }
            
            # Preserve game names from old state, set all to 0
            if "game_deaths" in old_state:
                for game_name in old_state["game_deaths"].keys():
                    new_state["game_deaths"][game_name] = 0
            
            # Write new state
            with open(STATE_JSON, "w", encoding="utf-8") as f:
                json.dump(new_state, f, indent=2)
            print(f"✓ Reset state file: {len(new_state['game_deaths'])} games reset to 0")
        except Exception as e:
            print(f"✗ Error resetting state file: {e}")
            return False
    else:
        print("ℹ No state file found (will be created on first run)")
    
    # Reset main text file
    try:
        with open(DEATH_TXT, "w", encoding="utf-8") as f:
            f.write("0")
        print("✓ Reset main text file to 0")
    except Exception as e:
        print(f"✗ Error resetting main text file: {e}")
        return False
    
    # Delete per-game text files
    try:
        deleted_count = 0
        if os.path.exists(BASE_DIR):
            for filename in os.listdir(BASE_DIR):
                if filename.startswith("death_counter_") and filename.endswith(".txt") and filename != "death_counter.txt":
                    filepath = os.path.join(BASE_DIR, filename)
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except:
                        pass
        if deleted_count > 0:
            print(f"✓ Deleted {deleted_count} per-game text file(s)")
    except Exception as e:
        print(f"⚠ Could not clean up per-game files: {e}")
    
    print()
    print("=" * 60)
    print("SUCCESS! All death counts reset to 0.")
    print("=" * 60)
    print()
    print("Note: The daemon will automatically pick up the changes.")
    print("      No need to restart the daemon.")
    
    return True


if __name__ == "__main__":
    try:
        success = reset_deaths()
        if not success:
            print("\nPress Enter to exit...")
            input()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nReset cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

