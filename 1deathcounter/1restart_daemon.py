"""
Restart Death Counter Daemon
Stops the daemon and starts it again, preserving all death counts.
"""

import os
import sys
import time
import subprocess

BASE_DIR = r"C:\deathcounter"
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
STOP_FILE = os.path.join(BASE_DIR, "STOP")
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
    """Start the daemon."""
    print("\nStarting daemon...")
    
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
    print("RESTART DEATH COUNTER DAEMON")
    print("=" * 70)
    print("This will stop and restart the daemon, preserving all death counts.")
    print("=" * 70)
    
    # Stop daemon
    if not stop_daemon():
        print("\n[ERROR] Failed to stop daemon. Aborting.")
        return 1
    
    # Start daemon
    if not start_daemon():
        print("\n[ERROR] Failed to start daemon.")
        return 1
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Daemon restarted successfully!")
    print("=" * 70)
    print("\nNote: All death counts are preserved.")
    print("The daemon will auto-detect which game is running.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

