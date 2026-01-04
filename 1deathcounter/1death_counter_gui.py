"""
Death Counter GUI Application
A simple GUI to control the death counter daemon and view stats.

To create an .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "DeathCounter" death_counter_gui.py
"""

import os
import sys
import json
import time
import subprocess
import threading
from tkinter import *
from tkinter import ttk, messagebox

BASE_DIR = r"C:\1deathcounter"
CONFIG_FILE = os.path.join(BASE_DIR, "games_config.json")
STATE_JSON = os.path.join(BASE_DIR, "death_state.json")
LOCK_FILE = os.path.join(BASE_DIR, "daemon.lock")
STOP_FILE = os.path.join(BASE_DIR, "STOP")
SCRIPT_PATH = os.path.join(BASE_DIR, "multi_game_death_counter.py")
DEATH_TXT = os.path.join(BASE_DIR, "death_counter.txt")


class DeathCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Death Counter Control")
        self.root.geometry("400x340")
        self.root.resizable(False, False)
        
        # Variables
        self.daemon_process = None
        self.monitoring = False
        
        # Create UI
        self.create_ui()
        
        # Check initial state (after UI is created)
        self.update_status()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Death Counter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        # Status and total deaths in a row
        status_row = ttk.Frame(status_frame)
        status_row.grid(row=0, column=0, sticky=(W, E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_row, text="Checking...", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=W)
        
        # Total deaths label
        self.total_deaths_label = ttk.Label(status_row, text="Total Deaths: 0", font=("Arial", 10, "bold"))
        self.total_deaths_label.grid(row=0, column=1, sticky=E, padx=(20, 0))
        
        # Death count display - Large clickable button
        count_frame = ttk.Frame(main_frame)
        count_frame.grid(row=2, column=0, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        # Create a large button that shows death count and game name
        # Use a frame with label for better text control
        button_container = Frame(count_frame, bg="#f0f0f0", relief=RAISED, bd=3)
        button_container.grid(row=0, column=0, sticky=(W, E), ipadx=10, ipady=10)
        count_frame.columnconfigure(0, weight=1)
        
        # Death count label (large)
        self.death_count_label = Label(
            button_container,
            text="0",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="black"
        )
        self.death_count_label.pack(pady=(10, 5))
        
        # Game name label (smaller, wraps)
        self.game_name_label = Label(
            button_container,
            text="No game selected",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="black",
            wraplength=320,
            justify=CENTER
        )
        self.game_name_label.pack(pady=(0, 10))
        
        # Make the whole container clickable
        self.death_count_button = button_container
        # Use ButtonRelease-1 for better click detection
        button_container.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        button_container.bind("<Enter>", lambda e: self.on_button_enter(button_container))
        button_container.bind("<Leave>", lambda e: self.on_button_leave(button_container))
        self.death_count_label.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        self.game_name_label.bind("<ButtonRelease-1>", lambda e: self.cycle_game())
        button_container.config(cursor="hand2")
        self.death_count_label.config(cursor="hand2")
        self.game_name_label.config(cursor="hand2")
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Control", padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(W, E), pady=(0, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Daemon", command=self.start_daemon, width=18)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Daemon", command=self.stop_daemon, width=18, state=DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(5, 0))
        
        # Load available games
        self.load_games()
    
    def on_button_enter(self, container):
        """Change background on hover."""
        container.config(bg="#e0e0e0")
        self.death_count_label.config(bg="#e0e0e0")
        self.game_name_label.config(bg="#e0e0e0")
    
    def on_button_leave(self, container):
        """Restore background on leave."""
        container.config(bg="#f0f0f0")
        self.death_count_label.config(bg="#f0f0f0")
        self.game_name_label.config(bg="#f0f0f0")
    
    def load_games(self):
        """Load available games from config."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.available_games = list(config.get("games", {}).keys())
            else:
                self.available_games = ["Elden Ring", "Dark Souls 3", "Dark Souls Remastered", "Sekiro"]
        except:
            self.available_games = ["Elden Ring", "Dark Souls 3", "Dark Souls Remastered", "Sekiro"]
        
        if not self.available_games:
            self.available_games = ["No games configured"]
    
    def get_current_game(self):
        """Get current game from state or config."""
        try:
            # Try state file first
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                game = state.get("current_game")
                if game:
                    return game
            
            # Fall back to config
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("current_game", self.available_games[0] if self.available_games else "Unknown")
        except:
            pass
        
        return self.available_games[0] if self.available_games else "Unknown"
    
    def get_death_count(self, game_name):
        """Get death count for a specific game."""
        try:
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                game_deaths = state.get("game_deaths", {})
                return game_deaths.get(game_name, 0)
        except:
            pass
        return 0
    
    def get_total_deaths(self):
        """Get total deaths across all games."""
        try:
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                return state.get("total_deaths", 0)
        except:
            pass
        return 0
    
    def cycle_game(self, event=None):
        """Cycle to the next game in the list."""
        if not self.available_games or len(self.available_games) == 0:
            messagebox.showwarning("No Games", "No games configured.")
            return
        
        current_game = self.get_current_game()
        
        # Find current index
        try:
            current_index = self.available_games.index(current_game)
            next_index = (current_index + 1) % len(self.available_games)
        except:
            next_index = 0
        
        new_game = self.available_games[next_index]
        
        # Switch game using the manual switch script
        try:
            switch_script = os.path.join(BASE_DIR, "switch_game_manual.py")
            if os.path.exists(switch_script):
                result = subprocess.run(
                    [sys.executable, switch_script, new_game],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR
                )
                if result.returncode == 0:
                    self.update_status()
                    # Silently switch - no popup
                else:
                    # Fallback to direct switch if script fails
                    self.switch_game_direct(new_game)
            else:
                # Fallback: directly update config
                self.switch_game_direct(new_game)
        except Exception as e:
            # Fallback to direct switch on any error
            try:
                self.switch_game_direct(new_game)
            except:
                pass
    
    def switch_game_direct(self, game_name):
        """Directly switch game by updating config and state."""
        try:
            # Update config
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                config["current_game"] = game_name
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
            
            # Update state
            if os.path.exists(STATE_JSON):
                with open(STATE_JSON, "r", encoding="utf-8") as f:
                    state = json.load(f)
                state["current_game"] = game_name
                with open(STATE_JSON, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
            
            # Update text file
            game_deaths = self.get_death_count(game_name)
            with open(DEATH_TXT, "w", encoding="utf-8") as f:
                f.write(str(game_deaths))
            
            self.update_status()
            # Silently switch - no popup
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch game: {e}")
    
    def is_daemon_running(self):
        """Check if daemon is running."""
        return os.path.exists(LOCK_FILE)
    
    def start_daemon(self):
        """Start the death counter daemon."""
        if self.is_daemon_running():
            # Silently return - no popup
            return
        
        if not os.path.exists(SCRIPT_PATH):
            # Silently return - no popup
            return
        
        try:
            # Start daemon in background
            if sys.platform == "win32":
                self.daemon_process = subprocess.Popen(
                    [sys.executable, SCRIPT_PATH],
                    cwd=BASE_DIR,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                self.daemon_process = subprocess.Popen(
                    [sys.executable, SCRIPT_PATH],
                    cwd=BASE_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Wait a moment for it to start
            time.sleep(2)
            
            if self.is_daemon_running():
                self.update_status()
                # Silently start - no popup
            else:
                # Silently fail - no popup
                pass
        except Exception as e:
            # Silently fail - no popup
            pass
    
    def stop_daemon(self):
        """Stop the death counter daemon."""
        if not self.is_daemon_running():
            # Silently return - no popup
            return
        
        try:
            # Create STOP file
            with open(STOP_FILE, "w") as f:
                f.write("")
            
            # Wait for daemon to stop
            for i in range(10):
                time.sleep(1)
                if not self.is_daemon_running():
                    break
            
            # If still running, try to kill process
            if self.is_daemon_running():
                try:
                    with open(LOCK_FILE, "r") as f:
                        pid = f.read().strip()
                    if pid:
                        subprocess.run(["taskkill", "/F", "/PID", pid], 
                                     capture_output=True, check=False)
                    if os.path.exists(LOCK_FILE):
                        os.remove(LOCK_FILE)
                except:
                    pass
            
            # Clean up
            if os.path.exists(STOP_FILE):
                os.remove(STOP_FILE)
            
            self.update_status()
            # Silently stop - no popup
        except Exception as e:
            # Silently fail - no popup
            pass
    
    def update_status(self):
        """Update the UI with current status."""
        # Check if UI elements exist (they might not during initialization)
        if not hasattr(self, 'status_label'):
            return
        
        # Update daemon status
        running = self.is_daemon_running()
        if running:
            self.status_label.config(text="Status: Running", foreground="green")
            if hasattr(self, 'start_button'):
                self.start_button.config(state=DISABLED)
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=NORMAL)
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            if hasattr(self, 'start_button'):
                self.start_button.config(state=NORMAL)
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=DISABLED)
        
        # Update game and death count on the button
        current_game = self.get_current_game()
        death_count = self.get_death_count(current_game)
        total_deaths = self.get_total_deaths()
        
        # Update the labels separately
        if hasattr(self, 'death_count_label') and hasattr(self, 'game_name_label'):
            self.death_count_label.config(text=str(death_count))
            self.game_name_label.config(text=current_game)
        
        # Update total deaths display
        if hasattr(self, 'total_deaths_label'):
            self.total_deaths_label.config(text=f"Total Deaths: {total_deaths}")
    
    def start_monitoring(self):
        """Start background thread to monitor status."""
        self.monitoring = True
        
        def monitor():
            while self.monitoring:
                try:
                    self.root.after(0, self.update_status)
                    time.sleep(2)  # Update every 2 seconds
                except:
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window closing."""
        self.monitoring = False
        self.root.destroy()


def main():
    root = Tk()
    app = DeathCounterGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

