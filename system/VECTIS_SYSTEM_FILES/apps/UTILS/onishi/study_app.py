import tkinter as tk
from tkinter import ttk
import random
import time
import json

# --- CONFIG ---
# Physical (QWERTY) to Logical (ONISHI)
KEY_MAP = {
    # Top
    'q': 'q', 'w': 'l', 'e': 'u', 'r': ',', 't': '.',
    'y': 'f', 'u': 'w', 'i': 'r', 'o': 'y', 'p': 'p',
    # Home
    'a': 'e', 's': 'i', 'd': 'a', 'f': 'o', 'g': '-',
    'h': 'k', 'j': 't', 'k': 'n', 'l': 's', ';': 'h',
    # Bottom
    'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': ';',
    'n': 'g', 'm': 'd', ',': 'm', '.': 'j', '/': 'b'
}
INVERTED_MAP = {v: k for k, v in KEY_MAP.items()} # Logical -> Physical

# Row Definitions for Level Progression
LEVELS = {
    1: {'name': "Level 1: Home Row (Basic)", 'chars': "eiaoktnhs-"},
    2: {'name': "Level 2: Top Row (Vowels & Common)", 'chars': "lu, .fwryp"},
    3: {'name': "Level 3: Bottom Row", 'chars': "zxcv;gdmjb"},
    4: {'name': "Level 4: All Keys (Mastery)", 'chars': "".join(KEY_MAP.values())},
}

class OnishiDojo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VECTIS ONISHI DOJO - Type Mastery")
        self.geometry("900x600")
        self.configure(bg="#0f172a") # Slate 900
        
        self.current_level = 1
        self.current_target = ""
        self.correct_count = 0
        self.total_count = 0
        self.start_time = time.time()
        
        self.setup_ui()
        self.setup_keyboard_visual()
        
        # Binds
        self.bind('<Key>', self.on_key)
        
        self.next_drill()

    def setup_ui(self):
        # Header Frame
        frame_top = tk.Frame(self, bg="#1e293b", height=80)
        frame_top.pack(fill="x", pady=(0, 20))
        
        self.lbl_title = tk.Label(frame_top, text="ONISHI LAYOUT DOJO", font=("Impact", 24), fg="#38bdf8", bg="#1e293b")
        self.lbl_title.pack(side="left", padx=20, pady=20)
        
        # Stats
        self.lbl_stats = tk.Label(frame_top, text="Accuracy: 100% | WPM: 0", font=("Consolas", 14), fg="#94a3b8", bg="#1e293b")
        self.lbl_stats.pack(side="right", padx=20)

        # Toggle Button
        self.is_layout_active = False
        self.btn_toggle = tk.Button(frame_top, text="Enable Onishi Layout", font=("Arial", 10, "bold"), 
                                    bg="#334155", fg="white", activebackground="#475569", 
                                    command=self.toggle_layout)
        self.btn_toggle.pack(side="right", padx=10, pady=20)

        # Level Selector Frame
        frame_level = tk.Frame(self, bg="#0f172a")
        frame_level.pack(pady=10)
        
        tk.Label(frame_level, text="Select Course:", fg="white", bg="#0f172a", font=("Arial", 10)).pack(side="left")
        
        self.combo_level = ttk.Combobox(frame_level, values=[LEVELS[i]['name'] for i in range(1, 5)], state="readonly")
        self.combo_level.current(0)
        self.combo_level.pack(side="left", padx=10)
        self.combo_level.bind("<<ComboboxSelected>>", self.change_level)

        # Main Display Targets
        self.lbl_target = tk.Label(self, text="READY", font=("Consolas", 80, "bold"), fg="#ffffff", bg="#0f172a")
        self.lbl_target.pack(pady=20)
        
        self.lbl_hint = tk.Label(self, text="Press [SPACE] to Start", font=("Arial", 16), fg="#64748b", bg="#0f172a")
        self.lbl_hint.pack(pady=10)

        # Visual Keyboard Canvas
        self.canvas = tk.Canvas(self, width=800, height=250, bg="#1e293b", highlightthickness=0)
        self.canvas.pack(pady=30)

    def toggle_layout(self):
        import subprocess
        import os
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if not self.is_layout_active:
            # Turn ON
            bat_path = os.path.join(base_dir, "01_大西配列を開始する.bat")
            try:
                subprocess.Popen(bat_path, shell=True, cwd=base_dir)
                self.is_layout_active = True
                self.btn_toggle.config(text="DISABLE Onishi Layout", bg="#22c55e", fg="black") # Cayan/Green
                self.focus_force() # Keep focus on trainer
            except Exception as e:
                print(f"Error starting layout: {e}")
        else:
            # Turn OFF
            bat_path = os.path.join(base_dir, "02_大西配列を終了して元に戻す.bat")
            try:
                subprocess.Popen(bat_path, shell=True, cwd=base_dir)
                self.is_layout_active = False
                self.btn_toggle.config(text="Enable Onishi Layout", bg="#334155", fg="white")
                self.focus_force()
            except Exception as e:
                print(f"Error stopping layout: {e}")

    def setup_keyboard_visual(self):
        self.keys_visual = {} # Store rectangle IDs by PHYSICAL key
        
        # Simple QWERTY Layout for visual reference
        rows = [
            "qwertyuiop",
            "asdfghjkl;",
            "zxcvbnm,./"
        ]
        
        start_x = 50
        start_y = 20
        key_w = 60
        key_h = 60
        gap = 10
        
        for r_idx, row_str in enumerate(rows):
            x_offset = r_idx * 20 # Stagger
            for c_idx, char in enumerate(row_str):
                x = start_x + x_offset + c_idx * (key_w + gap)
                y = start_y + r_idx * (key_h + gap)
                
                # Draw Key
                rect = self.canvas.create_rectangle(x, y, x+key_w, y+key_h, fill="#334155", outline="#475569", width=2)
                
                # Draw Labels
                # Physical (Small, Top Left)
                self.canvas.create_text(x+10, y+15, text=char.upper(), fill="#64748b", font=("Arial", 8))
                
                # Logical (Large, Center) - What it maps to
                logical_char = KEY_MAP.get(char, "?").upper()
                txt = self.canvas.create_text(x+30, y+35, text=logical_char, fill="#f8fafc", font=("Arial", 16, "bold"))
                
                self.keys_visual[char] = {'rect': rect, 'text': txt, 'default_fill': "#334155"}

        # Spacebar
        self.canvas.create_rectangle(200, 240, 600, 290, fill="#334155", outline="#475569")

    def change_level(self, event):
        idx = self.combo_level.current() + 1
        self.current_level = idx
        self.correct_count = 0
        self.total_count = 0
        self.next_drill()

    def highlight_key(self, logical_char):
        # Reset all
        for k, v in self.keys_visual.items():
            self.canvas.itemconfig(v['rect'], fill=v['default_fill'])
            
        # Find Physical key for this Logical char
        phys = INVERTED_MAP.get(logical_char.lower())
        if phys and phys in self.keys_visual:
            visual = self.keys_visual[phys]
            self.canvas.itemconfig(visual['rect'], fill="#0ea5e9") # Highlight Blue

    def next_drill(self):
        # Generate Target
        pool = LEVELS[self.current_level]['chars']
        # Bias towards least practiced? For now random
        self.current_target = random.choice(pool)
        
        self.lbl_target.config(text=self.current_target.upper(), fg="#ffffff")
        
        # Show Hint
        phys = INVERTED_MAP.get(self.current_target, "?")
        self.lbl_hint.config(text=f"Physical Key: [{phys.upper()}] -> Onishi: [{self.current_target.upper()}]")
        
        self.highlight_key(self.current_target)

    def on_key(self, event):
        char = event.char.lower()
        if not char: return # Modifier keys
        
        # Special check for ; / etc
        
        # Check correctness (Assuming AHK is active OR user is typing on QWERTY but mentally mapping)
        # Actually, if the user has AHK active, 'event.char' is the LOGICAL char.
        # If AHK is NOT active, 'event.char' is the PHYSICAL char.
        # We should assume user might have AHK On or Off. 
        # But this is a trainer... let's assume AHK IS ON, so we receive the LOGICAL char.
        
        if char == self.current_target:
            self.flash_feedback(True)
            self.correct_count += 1
            self.next_drill()
        else:
            self.flash_feedback(False)
        
        self.total_count += 1
        self.update_stats()

    def flash_feedback(self, correct):
        color = "#22c55e" if correct else "#ef4444"
        self.lbl_target.config(fg=color)
        if not correct:
            self.after(200, lambda: self.lbl_target.config(fg="#ffffff"))
            
    def update_stats(self):
        if self.total_count == 0: return
        acc = (self.correct_count / self.total_count) * 100
        # Simple WPM approximation
        elapsed_min = (time.time() - self.start_time) / 60
        wpm = (self.correct_count / 5) / elapsed_min if elapsed_min > 0 else 0
        
        self.lbl_stats.config(text=f"Accuracy: {acc:.1f}% | WPM: {wpm:.0f}")

if __name__ == "__main__":
    app = OnishiDojo()
    app.mainloop()
