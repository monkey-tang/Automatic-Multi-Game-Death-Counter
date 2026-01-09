"""
Runtime hook to fix Tcl/Tk version conflicts by using system Tcl/Tk when available.
This ensures the installer works with Python 3.8-3.13 regardless of Tcl version.
This runs early in the PyInstaller boot process.
"""
import os
import sys

# Only run this fix if we're in a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    try:
        import subprocess
        import shutil
        
        # Try to find system Python's Tcl/Tk
        python_exe = None
        
        # Check if Python is in PATH
        try:
            python_exe = shutil.which('python')
        except:
            pass
        
        # Check common Python installation locations
        if not python_exe:
            common_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'Python'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Python'),
            ]
            
            for base_path in common_paths:
                if os.path.exists(base_path):
                    for item in os.listdir(base_path):
                        python_dir = os.path.join(base_path, item)
                        if os.path.isdir(python_dir):
                            exe = os.path.join(python_dir, 'python.exe')
                            if os.path.exists(exe):
                                python_exe = exe
                                break
                    if python_exe:
                        break
        
        # If we found Python, try to use its Tcl/Tk
        if python_exe and os.path.exists(python_exe):
            python_dir = os.path.dirname(python_exe)
            python_lib = os.path.join(python_dir, 'Lib')
            tkinter_path = os.path.join(python_lib, 'tkinter')
            
            if os.path.exists(tkinter_path):
                tcl_path = os.path.join(tkinter_path, 'tcl')
                tk_path = os.path.join(tkinter_path, 'tk')
                
                # Verify Tcl/Tk directories exist
                if os.path.exists(tcl_path) and os.path.exists(tk_path):
                    init_tcl = os.path.join(tcl_path, 'init.tcl')
                    if os.path.exists(init_tcl):
                        # Use system Tcl/Tk with absolute paths
                        tcl_abs = os.path.abspath(tcl_path)
                        tk_abs = os.path.abspath(tk_path)
                        os.environ['TCL_LIBRARY'] = tcl_abs
                        os.environ['TK_LIBRARY'] = tk_abs
                        os.environ['TCL_LIBRARY_PATH'] = tcl_abs
                        os.environ['TK_LIBRARY_PATH'] = tk_abs
    except Exception:
        # If anything fails, just continue - bundled Tcl/Tk will be used
        pass
