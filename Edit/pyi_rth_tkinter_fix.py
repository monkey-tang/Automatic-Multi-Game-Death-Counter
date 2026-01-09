"""
Runtime hook to fix Tcl/Tk version conflicts by using system Tcl/Tk when available.
This ensures the installer works with Python 3.8-3.13 regardless of Tcl version.
"""
import os
import sys

# Only run this fix if we're in a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    try:
        import tkinter
        import _tkinter
        
        # Try to find system Tcl/Tk from Python installation
        python_exe = sys.executable
        if python_exe:
            # Get Python installation directory
            python_dir = os.path.dirname(python_exe)
            python_lib = os.path.join(python_dir, 'Lib')
            tkinter_path = os.path.join(python_lib, 'tkinter')
            
            # Check if system tkinter exists
            if os.path.exists(tkinter_path):
                tcl_path = os.path.join(tkinter_path, 'tcl')
                tk_path = os.path.join(tkinter_path, 'tk')
                
                # If system Tcl/Tk exists, prefer it over bundled version
                if os.path.exists(tcl_path) and os.path.exists(tk_path):
                    # Set environment variables to use system Tcl/Tk
                    # This will be picked up by tkinter when it initializes
                    os.environ['TCL_LIBRARY'] = tcl_path
                    os.environ['TK_LIBRARY'] = tk_path
    except Exception:
        # If anything fails, just continue - bundled Tcl/Tk will be used
        pass
