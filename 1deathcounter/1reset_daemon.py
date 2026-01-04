"""
Reset Death Counter Daemon
Stops the daemon, resets all death counts to 0, then restarts it.
"""

import os
import sys
import json
import time
import subprocess

BASE_DIR = r"C:\deathcounter"
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
STOP_FILE = os.path.join(BASE_DIR, "STOP")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")
SCRIPT_PATH = os.path.join(BASE_DIR, "multi_game_death_counter.py")


def stop_daemon():
    """Stop the running daemon."""
    print("Stopping daemon...")
    
    # Check if daemon is running
    if not os.path.exists(LOCK_FILE):
        print("[INFO] Daemon is not running.")
        return True
    
    # Read PID from lock file
    try:
        with open(LOCK_FILE, "r") as f:
            pid = f.read().strip()
        print(f"Found daemon process (PID: {pid})")
    except:
        print("Could not read lock file, but it exists.")
        pid = None
    
    # Create STOP file
    try:
        with open(STOP_FILE, "w") as f:
            f.write("")
        print("STOP file created.")
    except Exception as e:
        print(f"Error creating STOP file: {e}")
        return False
    
    # Wait for daemon to stop
    print("Waiting for daemon to stop...")
    for i in range(10):  # Wait up to 10 seconds
        time.sleep(1)
        if not os.path.exists(LOCK_FILE):
            print("[OK] Daemon stopped successfully.")
            return True
        print(f"  Still waiting... ({i+1}/10)")
    
    # If still running, try to kill the process
    if os.path.exists(LOCK_FILE) and pid:
        print(f"Daemon didn't stop automatically. Attempting to kill process {pid}...")
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", pid], 
                             capture_output=True, check=False)
            else:
                subprocess.run(["kill", "-9", pid], 
                             capture_output=True, check=False)
            time.sleep(1)
        except Exception as e:
            print(f"Error killing process: {e}")
    
    # Clean up lock file if it still exists
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("[OK] Lock file removed.")
        except Exception as e:
            print(f"Warning: Could not remove lock file: {e}")
    
    # Remove STOP file
    if os.path.exists(STOP_FILE):
        try:
            os.remove(STOP_FILE)
            print("[OK] STOP file removed")
        except:
            pass
    
    return True


def reset_state():
    """Reset all death counts to 0."""
    print("\nResetting death counts...")
    
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
                "tick": 0,
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
            print(f"[OK] State file reset: {len(new_state['game_deaths'])} games reset to 0")
        except Exception as e:
            print(f"[ERROR] Failed to reset state file: {e}")
            return False
    else:
        print("[INFO] No state file found (will be created on first run)")
    
    # Reset main text file
    try:
        with open(DEATH_TXT, "w", encoding="utf-8") as f:
            f.write("0")
        print("[OK] Main text file reset to 0")
    except Exception as e:
        print(f"[WARNING] Could not reset main text file: {e}")
    
    # Delete per-game text files
    try:
        deleted_count = 0
        for filename in os.listdir(BASE_DIR):
            if filename.startswith("death_counter_") and filename.endswith(".txt") and filename != "death_counter.txt":
                filepath = os.path.join(BASE_DIR, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except:
                    pass
        if deleted_count > 0:
            print(f"[OK] Deleted {deleted_count} per-game text file(s)")
    except Exception as e:
        print(f"[WARNING] Could not clean up per-game files: {e}")
    
    return True


def start_daemon():
    """Start the daemon."""
    print("\nStarting daemon...")
    
    # Make sure STOP file is removed
    if os.path.exists(STOP_FILE):
        try:
            os.remove(STOP_FILE)
            print("[OK] Removed any leftover STOP file")
        except:
            pass
    
    if not os.path.exists(SCRIPT_PATH):
        print(f"[ERROR] Script not found: {SCRIPT_PATH}")
        return False
    
    try:
        # Start daemon in background (detached process on Windows)
        if sys.platform == "win32":
            # Use START command to run in new window, or run detached
            subprocess.Popen(
                [sys.executable, SCRIPT_PATH],
                cwd=BASE_DIR,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        else:
            subprocess.Popen(
                [sys.executable, SCRIPT_PATH],
                cwd=BASE_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Wait a moment for it to start
        time.sleep(2)
        
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, "r") as f:
                    pid = f.read().strip()
                print(f"[OK] Daemon started successfully (PID: {pid})")
                return True
            except:
                print("[OK] Daemon started successfully")
                return True
        else:
            print("[WARNING] Daemon may not have started (no lock file found)")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to start daemon: {e}")
        return False


def main():
    print("=" * 70)
    print("RESET DEATH COUNTER DAEMON")
    print("=" * 70)
    print("This will:")
    print("  1. Stop the daemon")
    print("  2. Reset ALL death counts to 0")
    print("  3. Restart the daemon")
    print("=" * 70)
    
    # Confirm reset
    response = input("\nAre you sure you want to reset all death counts? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Reset cancelled.")
        return 0
    
    # Stop daemon
    if not stop_daemon():
        print("\n[ERROR] Failed to stop daemon. Aborting.")
        return 1
    
    # Reset state
    if not reset_state():
        print("\n[ERROR] Failed to reset state.")
        return 1
    
    # Start daemon
    if not start_daemon():
        print("\n[ERROR] Failed to start daemon.")
        return 1
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Daemon reset and restarted successfully!")
    print("=" * 70)
    print("\nAll death counts have been reset to 0.")
    print("The daemon will auto-detect which game is running.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

