import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import glob
import threading
import queue
import time
from datetime import datetime

# =================================================================================
# CONFIGURATION
# =================================================================================
SYSTEM_NAME = "EGO PROFESSIONAL WORKSTATION"
VERSION = "v2.0.0 (Command Center)"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(ROOT_DIR, "apps")

# Theme Colors (Hacker / Cyberpunk Style)
COLOR_BG = "#1e1e1e"        # Main Background (Dark Gray)
COLOR_SIDEBAR = "#252526"   # Sidebar Background
COLOR_FG = "#cccccc"        # Default Text
COLOR_ACCENT = "#00ff99"    # Neon Green Accent
COLOR_ACCENT_HOVER = "#00cc7a"
COLOR_BTN_BG = "#333333"    # Button Background
COLOR_CONSOLE_BG = "#0f0f0f"# Console Background
COLOR_CONSOLE_FG = "#00ff00"# Console Text (Matrix Green)

# Font Settings
FONT_TITLE = ("Consolas", 16, "bold")
FONT_HEADER = ("Consolas", 12, "bold")
FONT_NORMAL = ("Meiryo UI", 10)
FONT_CONSOLE = ("Consolas", 9)

# =================================================================================
# APP SCANNING LOGIC (ENHANCED)
# =================================================================================
def scan_apps():
    """
    Scans the APPS_DIR for applications.
    Returns a dictionary: { "CATEGORY": [ {name, path, type, dir}, ... ], ... }
    """
    apps_data = {}
    
    if not os.path.exists(APPS_DIR):
        return apps_data

    # Scan top-level directories in APPS_DIR
    for category in os.listdir(APPS_DIR):
        cat_path_full = os.path.join(APPS_DIR, category)
        if os.path.isdir(cat_path_full) and not category.startswith("_"):
            apps_list = []
            
            # Scan subdirectories (Actual Apps)
            for app_name in os.listdir(cat_path_full):
                app_path_full = os.path.join(cat_path_full, app_name)
                if not os.path.isdir(app_path_full):
                    continue

                entry_point = None
                app_type = "unknown"
                
                # --- DETECTION STRATEGY (Priority Order) ---
                
                # 1. Standard Python Entry Points
                if os.path.exists(os.path.join(app_path_full, "app.py")):
                    entry_point = os.path.join(app_path_full, "app.py")
                    # Check if Streamlit
                    try:
                        with open(entry_point, "r", encoding="utf-8", errors="ignore") as f:
                            if "streamlit" in f.read(500):
                                app_type = "streamlit"
                            else:
                                app_type = "python"
                    except: app_type = "python"

                elif os.path.exists(os.path.join(app_path_full, "main.py")):
                    entry_point = os.path.join(app_path_full, "main.py")
                    app_type = "python"

                # 2. Web Apps (HTML)
                elif os.path.exists(os.path.join(app_path_full, "index.html")):
                    entry_point = os.path.join(app_path_full, "index.html")
                    app_type = "html"

                # 3. Smart Python Detection (Folder Name Match e.g. gemini_cli/gemini_terminal.py)
                else:
                    py_files = glob.glob(os.path.join(app_path_full, "*.py"))
                    # Filter out test files or configs
                    valid_pys = [p for p in py_files if "test" not in p and "config" not in p]
                    
                    if valid_pys:
                        # Find best match (contains app name or ends with _app.py / _tk.py)
                        best_match = None
                        for p in valid_pys:
                            fname = os.path.basename(p)
                            if app_name in fname or fname.endswith("_app.py") or fname.endswith("_tk.py") or fname.endswith("_cli.py"):
                                best_match = p
                                break
                        
                        if best_match:
                            entry_point = best_match
                            app_type = "python"
                        elif len(valid_pys) == 1:
                            # If only one python file, assume it's the one
                            entry_point = valid_pys[0]
                            app_type = "python"

                # 4. Batch Files
                if not entry_point and glob.glob(os.path.join(app_path_full, "*.bat")):
                    entry_point = glob.glob(os.path.join(app_path_full, "*.bat"))[0]
                    app_type = "batch"

                # 5. Project Configs (Node / Rust) - Just open folder
                if not entry_point:
                    if os.path.exists(os.path.join(app_path_full, "package.json")):
                        entry_point = app_path_full
                        app_type = "node_project"
                    elif os.path.exists(os.path.join(app_path_full, "Cargo.toml")):
                        entry_point = app_path_full
                        app_type = "rust_project"

                # --- REGISTER APP ---
                if entry_point:
                    apps_list.append({
                        "name": app_name,
                        "path": entry_point,
                        "type": app_type,
                        "dir": app_path_full
                    })
            
            if apps_list:
                apps_data[category] = sorted(apps_list, key=lambda x: x['name'])
                
    return apps_data

# ... (GUI Class remains same until launch_app) ...

    def launch_app(self, app):
        self.log(f"Launching {app['name']} ({app['type']})...")
        
        try:
            if app['type'] == 'streamlit':
                # Determine python executable (prefer venv)
                venv_python = os.path.join(ROOT_DIR, "..", ".venv", "Scripts", "python.exe")
                if not os.path.exists(venv_python):
                     venv_python = os.path.join(ROOT_DIR, "..", "..", ".venv", "Scripts", "python.exe")
                
                streamlit_exe = venv_python.replace("python.exe", "streamlit.exe") if os.path.exists(venv_python) else "streamlit"
                cmd = [streamlit_exe, "run", app['path']]
                subprocess.Popen(cmd, cwd=app['dir'], shell=True)

            elif app['type'] == 'python':
                venv_python = os.path.join(ROOT_DIR, "..", ".venv", "Scripts", "python.exe")
                if not os.path.exists(venv_python):
                     venv_python = os.path.join(ROOT_DIR, "..", "..", ".venv", "Scripts", "python.exe")
                
                python_exe = venv_python if os.path.exists(venv_python) else sys.executable
                cmd = [python_exe, app['path']]
                # Open in new console window
                subprocess.Popen(cmd, cwd=app['dir'], creationflags=subprocess.CREATE_NEW_CONSOLE)

            elif app['type'] == 'batch':
                subprocess.Popen([app['path']], cwd=app['dir'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

            elif app['type'] == 'html':
                os.startfile(app['path']) # Opens in default browser

            elif app['type'] in ['node_project', 'rust_project']:
                # Open folder
                os.startfile(app['path'])
                self.log(f"Opened project folder for {app['name']}")

            else:
                self.log(f"Unknown app type: {app['type']}")
                return

            self.log(f"Successfully launched {app['name']}")
            
        except Exception as e:
            self.log(f"Failed to launch {app['name']}: {e}")
            messagebox.showerror("Execution Error", str(e))

# =================================================================================
# HELPER FUNCTIONS
# =================================================================================
def format_app_name(raw_name):
    """
    Converts snake_case or kebab-case to Title Case.
    e.g. "base64_loom" -> "Base64 Loom"
    """
    # Replace common separators
    name = raw_name.replace("_", " ").replace("-", " ")
    # Capitalize words
    return name.title()

# =================================================================================
# MAIN GUI CLASS
# =================================================================================
class VectisHub(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(SYSTEM_NAME)
        self.geometry("1000x700")
        self.configure(bg=COLOR_BG)
        # self.iconbitmap("icon.ico") # Optional: Add icon if available
        
        self.apps_data = {}
        self.current_category = None
        
        # Configure Layout Grid
        self.grid_columnconfigure(1, weight=1) # Main content expands
        self.grid_rowconfigure(1, weight=1)    # Main content expands
        
        # Initialize logging first
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        
        # Start scanning in background
        self.after(100, self.process_log_queue)
        threading.Thread(target=self.load_apps, daemon=True).start()

    def setup_ui(self):
        # --- HEADER ---
        self.header_frame = tk.Frame(self, bg=COLOR_SIDEBAR, height=50)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        lbl_title = tk.Label(self.header_frame, text=SYSTEM_NAME, font=FONT_TITLE, fg=COLOR_ACCENT, bg=COLOR_SIDEBAR)
        lbl_title.pack(side="left", padx=20, pady=10)
        
        lbl_ver = tk.Label(self.header_frame, text=VERSION, font=("Consolas", 10), fg="#666", bg=COLOR_SIDEBAR)
        lbl_ver.pack(side="right", padx=20)

        # --- SIDEBAR (Categories) ---
        self.sidebar_frame = tk.Frame(self, bg=COLOR_SIDEBAR, width=200)
        self.sidebar_frame.grid(row=1, column=0, sticky="ns")
        self.sidebar_frame.grid_propagate(False) # Fixed width
        
        tk.Label(self.sidebar_frame, text="カテゴリー", font=FONT_HEADER, fg="#888", bg=COLOR_SIDEBAR).pack(pady=(20, 10), anchor="w", padx=20)
        
        self.category_buttons_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR)
        self.category_buttons_frame.pack(fill="x", padx=10)

        # --- MASTER CONTROLS ---
        tk.Label(self.sidebar_frame, text="マスターコントロール", font=FONT_HEADER, fg="#888", bg=COLOR_SIDEBAR).pack(pady=(20, 10), anchor="w", padx=20)
        
        btn_intel = tk.Button(self.sidebar_frame, text="[!] インテリジェンス起動",
                              font=("Consolas", 11, "bold"), bg=COLOR_BTN_BG, fg=COLOR_ACCENT,
                              activebackground=COLOR_ACCENT, activeforeground="#000",
                              bd=0, anchor="w", cursor="hand2", padx=10, pady=5,
                              command=self.launch_intelligence)
        btn_intel.pack(fill="x", padx=10, pady=2)

        # --- MAIN CONTENT (Tabs) ---
        self.main_content = tk.Frame(self, bg=COLOR_BG)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        
        # Style for Notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_SIDEBAR, foreground=COLOR_FG, padding=[10, 5], font=FONT_HEADER)
        style.map("TNotebook.Tab", background=[("selected", COLOR_ACCENT)], foreground=[("selected", "#000")])

        self.notebook = ttk.Notebook(self.main_content, style="TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: App Launcher
        self.tab_launcher = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_launcher, text=" アプリランチャー ")
        
        self.lbl_category_title = tk.Label(self.tab_launcher, text="Initialize...", font=FONT_HEADER, fg=COLOR_FG, bg=COLOR_BG)
        self.lbl_category_title.pack(anchor="w", pady=(0, 20))
        
        self.canvas = tk.Canvas(self.tab_launcher, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.tab_launcher, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Tab 2: Calendar
        self.tab_calendar = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_calendar, text=" ミッションカレンダー ")
        self.setup_calendar_tab()
        
        # Mousewheel scroll support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def setup_calendar_tab(self):
        # Load Tasks
        import json
        tasks_map = {}
        schedule_path = os.path.join(ROOT_DIR, "data", "SCHEDULE.json")
        try:
            if os.path.exists(schedule_path):
                with open(schedule_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for t in data.get("tasks", []):
                        d_str = t.get("date")
                        if d_str not in tasks_map: tasks_map[d_str] = []
                        tasks_map[d_str].append(t)
        except Exception as e:
            self.log(f"Calendar Error: {e}")

        import calendar
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Header (Refreshable)
        for w in self.tab_calendar.winfo_children():
            w.destroy()

        cal_header = tk.Frame(self.tab_calendar, bg=COLOR_BG)
        cal_header.pack(fill="x", pady=10)
        
        tk.Label(cal_header, text=f"{year}年 {month}月", font=("Consolas", 24, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG).pack(side="left")
        
        tk.Button(cal_header, text="↻ Refresh", bg=COLOR_BTN_BG, fg=COLOR_FG, bd=0, command=self.setup_calendar_tab).pack(side="right", padx=10)

        # Grid
        cal_frame = tk.Frame(self.tab_calendar, bg=COLOR_BG)
        cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Days of week
        days = ["月", "火", "水", "木", "金", "土", "日"]
        for i, day in enumerate(days):
            tk.Label(cal_frame, text=day, font=("Meiryo UI", 12, "bold"), fg="#888", bg=COLOR_BG).grid(row=0, column=i, sticky="ew", padx=2)
            cal_frame.grid_columnconfigure(i, weight=1)
            
        # Calendar Matrix
        cal = calendar.monthcalendar(year, month)
        today_day = now.day
        
        for r, week in enumerate(cal):
            cal_frame.grid_rowconfigure(r+1, weight=1)
            for c, day_num in enumerate(week):
                if day_num == 0:
                    continue
                
                bg_color = COLOR_BTN_BG
                fg_color = COLOR_FG
                
                # Check for tasks
                date_key = f"{year}-{month:02d}-{day_num:02d}"
                day_tasks = tasks_map.get(date_key, [])
                
                if day_num == today_day:
                    bg_color = COLOR_ACCENT
                    fg_color = "#000"
                elif day_tasks:
                    bg_color = "#334155" # Highlight days with tasks
                
                # Day Cell
                cell = tk.Frame(cal_frame, bg=bg_color, bd=1, relief="solid")
                cell.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)
                
                tk.Label(cell, text=str(day_num), font=("Consolas", 14, "bold"), bg=bg_color, fg=fg_color).pack(anchor="nw", padx=5, pady=5)
                
                # Display Tasks
                for t in day_tasks:
                     tk.Label(cell, text=f"• {t['title']}", font=("Meiryo UI", 8), bg=bg_color, fg=fg_color, anchor="w").pack(fill="x", padx=2)



        # --- CONSOLE (Log) ---
        self.console_frame = tk.Frame(self, bg=COLOR_CONSOLE_BG, height=120)
        self.console_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.console_frame.grid_propagate(False)
        
        self.console_text = tk.Text(self.console_frame, bg=COLOR_CONSOLE_BG, fg=COLOR_CONSOLE_FG, font=FONT_CONSOLE, state="disabled")
        self.console_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log(f"System booting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        self.log(f"Root Directory: {ROOT_DIR}")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def log(self, message):
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def process_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.console_text.config(state="normal")
            self.console_text.insert("end", msg + "\n")
            self.console_text.see("end")
            self.console_text.config(state="disabled")
        self.after(100, self.process_log_queue)

    def load_apps(self):
        self.log("Scanning apps directory...")
        try:
            self.apps_data = scan_apps()
            self.log(f"Scan complete. Found {sum(len(v) for v in self.apps_data.values())} apps in {len(self.apps_data)} categories.")
            
            # Update UI on main thread
            self.after(0, self.refresh_categories)
        except Exception as e:
            self.log(f"Error scanning apps: {e}")

    def refresh_categories(self):
        # Clear existing buttons
        for widget in self.category_buttons_frame.winfo_children():
            widget.destroy()
            
        categories = sorted(self.apps_data.keys())
        first_cat = None
        
        for cat in categories:
            if not first_cat: first_cat = cat
            btn = tk.Button(self.category_buttons_frame, text=f"> {cat}",
                            font=("Consolas", 11), bg=COLOR_SIDEBAR, fg=COLOR_FG,
                            activebackground=COLOR_BG, activeforeground=COLOR_ACCENT,
                            bd=0, anchor="w", cursor="hand2", padx=10, pady=5,
                            command=lambda c=cat: self.show_category(c))
            btn.pack(fill="x", pady=2)
            
        if first_cat:
            self.show_category(first_cat)
        else:
            self.lbl_category_title.config(text="No Apps Found")
            self.log("WARNING: No applications found in apps/ directory.")

    def show_category(self, category):
        self.current_category = category
        self.lbl_category_title.config(text=f"SECTOR: {category}")
        
        # Clear main area
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        apps = self.apps_data.get(category, [])
        
        # Grid layout for app cards
        row = 0
        col = 0
        max_cols = 4  # Increased for compact layout
        
        for app in apps:
            self.create_app_card(app, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_app_card(self, app, row, col):
        card_frame = tk.Frame(self.scrollable_frame, bg=COLOR_BTN_BG, padx=2, pady=2)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Main Button
        display_name = format_app_name(app['name'])
        btn_text = f"{display_name}\n({app['type']})"
        
        btn = tk.Button(card_frame, text=btn_text, font=FONT_NORMAL,
                        bg=COLOR_BTN_BG, fg=COLOR_FG,
                        activebackground=COLOR_ACCENT, activeforeground="#000",
                        width=25, height=2, bd=0, cursor="hand2", # Reduced height
                        command=lambda a=app: self.launch_app(a))
        btn.pack(fill="both", expand=True)
        
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.config(bg="#444", fg=COLOR_ACCENT))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_BTN_BG, fg=COLOR_FG))

    def launch_app(self, app):
        self.log(f"Launching {app['name']} ({app['type']})...")
        
        try:
            # Determine python executable (prefer venv)
            venv_python = os.path.join(ROOT_DIR, "..", ".venv", "Scripts", "python.exe")
            if not os.path.exists(venv_python):
                 venv_python = os.path.join(ROOT_DIR, "..", "..", ".venv", "Scripts", "python.exe")
            
            python_exe = venv_python if os.path.exists(venv_python) else sys.executable
            
            cmd = []
            cwd = app['dir']
            
            if app['type'] == 'streamlit':
                # Use python -m streamlit run to reliably find streamlit
                cmd = [python_exe, "-m", "streamlit", "run", app['path']]
                subprocess.Popen(cmd, cwd=cwd, shell=True) # shell=True allows streamlit to run in bg properly

            elif app['type'] == 'python':
                cmd = [python_exe, app['path']]
                # Open in new console window
                subprocess.Popen(cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)

            elif app['type'] == 'batch':
                subprocess.Popen([app['path']], cwd=cwd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

            elif app['type'] == 'html':
                # Open in default browser
                os.startfile(app['path'])

            elif app['type'] in ['node_project', 'rust_project']:
                # Open folder
                os.startfile(app['path'])
                self.log(f"Opened project folder for {app['name']}")

            else:
                self.log(f"Unknown app type: {app['type']}")
                return

            self.log(f"Successfully launched {app['name']}")
            
        except Exception as e:
            self.log(f"Failed to launch {app['name']}: {e}")
            messagebox.showerror("Execution Error", str(e))

    def launch_intelligence(self):
        """
        Launches the RUN_ALL_INTELLIGENCE.bat file in a new console window.
        """
        self.log("Initializing Intelligence Systems...")
        try:
            # Path to batch file (2 levels up from EGO_SYSTEM_FILES)
            bat_path = os.path.abspath(os.path.join(ROOT_DIR, "..", "RUN_ALL_INTELLIGENCE.bat"))
            
            if not os.path.exists(bat_path):
                self.log(f"ERROR: Intelligence launcher not found at {bat_path}")
                messagebox.showerror("Error", f"Launcher not found:\n{bat_path}")
                return

            # Run in new console
            cwd = os.path.dirname(bat_path)
            subprocess.Popen([bat_path], cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log("Intelligence System Launched Successfully.")
            
        except Exception as e:
            self.log(f"Failed to launch intelligence: {e}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = VectisHub()
    app.mainloop()
