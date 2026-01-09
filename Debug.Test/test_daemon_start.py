"""
Test script to verify daemon can start properly.
Run this directly to see what errors occur.
"""
import os
import sys
import subprocess
import time

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DAEMON_SCRIPT = os.path.join(BASE_DIR, "multi_game_death_counter.py")
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
READY_FILE = os.path.join(BASE_DIR, "daemon.ready")

def find_python():
    """Find Python executable."""
    # Try sys.executable first
    if sys.executable and sys.executable.endswith('python.exe'):
        return sys.executable
    
    # Try common locations
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Python\PythonCore", 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        try:
            version = winreg.EnumKey(key, 0)
            install_path_key = winreg.OpenKey(key, f"{version}\\InstallPath")
            install_path = winreg.QueryValueEx(install_path_key, "")[0]
            python_exe = os.path.join(install_path, "python.exe")
            if os.path.exists(python_exe):
                return python_exe
        except:
            pass
    except:
        pass
    
    # Try PATH
    try:
        result = subprocess.run(['where', 'python'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def main():
    print("=" * 70)
    print("DAEMON STARTUP TEST")
    print("=" * 70)
    print(f"Base directory: {BASE_DIR}")
    print(f"Daemon script: {DAEMON_SCRIPT}")
    print(f"Script exists: {os.path.exists(DAEMON_SCRIPT)}")
    print()
    
    # Clean up old files
    if os.path.exists(LOCK_FILE):
        print(f"Removing old lock file: {LOCK_FILE}")
        os.remove(LOCK_FILE)
    if os.path.exists(READY_FILE):
        print(f"Removing old ready file: {READY_FILE}")
        os.remove(READY_FILE)
    print()
    
    # Find Python
    python_exe = find_python()
    if not python_exe:
        print("ERROR: Could not find Python executable!")
        return
    print(f"Python executable: {python_exe}")
    print(f"Python exists: {os.path.exists(python_exe)}")
    print()
    
    # Check if script exists
    if not os.path.exists(DAEMON_SCRIPT):
        print(f"ERROR: Daemon script not found: {DAEMON_SCRIPT}")
        return
    
    # Test Python can import required modules
    print("Testing Python imports...")
    test_imports = [
        "import sys",
        "import os",
        "import json",
        "import time",
        "import subprocess",
        "import psutil",
        "import cv2",
        "import numpy",
        "from PIL import Image",
        "from mss import mss",
        "import pytesseract"
    ]
    
    for import_stmt in test_imports:
        try:
            result = subprocess.run(
                [python_exe, "-c", import_stmt],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✓ {import_stmt}")
            else:
                print(f"  ✗ {import_stmt} - Error: {result.stderr[:100]}")
        except Exception as e:
            print(f"  ✗ {import_stmt} - Exception: {e}")
    print()
    
    # Try to run daemon script directly (will show errors)
    print("Attempting to start daemon (will show any errors)...")
    print("=" * 70)
    try:
        process = subprocess.Popen(
            [python_exe, DAEMON_SCRIPT],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait a bit and check status
        time.sleep(3)
        
        if process.poll() is None:
            print("✓ Daemon process is running")
        else:
            print(f"✗ Daemon process exited with code: {process.returncode}")
            stdout, _ = process.communicate(timeout=1)
            if stdout:
                print("\nOutput:")
                print(stdout[:1000])
        
        # Check for lock file
        if os.path.exists(LOCK_FILE):
            print(f"✓ Lock file created: {LOCK_FILE}")
            with open(LOCK_FILE, 'r') as f:
                pid = f.read().strip()
            print(f"  PID in lock file: {pid}")
        else:
            print(f"✗ Lock file NOT created: {LOCK_FILE}")
        
        # Check for ready file
        if os.path.exists(READY_FILE):
            print(f"✓ Ready file created: {READY_FILE}")
            with open(READY_FILE, 'r') as f:
                pid = f.read().strip()
            print(f"  PID in ready file: {pid}")
        else:
            print(f"✗ Ready file NOT created: {READY_FILE}")
        
        # Check debug.log
        debug_log = os.path.join(BASE_DIR, "debug.log")
        if os.path.exists(debug_log):
            print(f"\n✓ Debug log exists: {debug_log}")
            with open(debug_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print(f"  Last 10 lines:")
                for line in lines[-10:]:
                    print(f"    {line.rstrip()}")
        else:
            print(f"\n✗ Debug log NOT created: {debug_log}")
        
        # Stop the daemon
        if process.poll() is None:
            print("\nStopping daemon...")
            stop_file = os.path.join(BASE_DIR, "STOP")
            with open(stop_file, 'w') as f:
                f.write("")
            time.sleep(1)
            if process.poll() is None:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
        
    except Exception as e:
        print(f"ERROR running daemon: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
