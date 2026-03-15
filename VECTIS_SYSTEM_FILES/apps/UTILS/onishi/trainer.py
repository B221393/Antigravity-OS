
import tkinter as tk
import random
import os
import re

class OnishiTrainer:
    def __init__(self):
        # Resolve AHK path relative to this script file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ahk_path = os.path.join(base_dir, "onishi_layout.ahk")
        
        self.mapping = self.load_mapping()
        self.target_char = ""
        self.score = 0
        self.total = 0
        
        # Setup GUI
        self.root = tk.Tk()
        self.root.title("Onishi Layout Trainer")
        self.root.geometry("600x400")
        self.root.config(bg="#222")
        self.setup_ui()
        self.next_question()

        # Keyboard bind
        self.root.bind('<Key>', self.on_key_press)

    def load_mapping(self):
        """Parse AHK file to create Logical(Onishi) -> Physical(Qwerty) map."""
        phys_to_log = {}
        
        if os.path.exists(self.ahk_path):
            with open(self.ahk_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    match = re.match(r'^([a-z0-9,./;-]+)::([a-z0-9,./;-]+)', line, re.IGNORECASE)
                    if match:
                        phys = match.group(1).lower()
                        log = match.group(2).lower()
                        if "sc027" in phys: phys = ";"
                        if "sc027" in log: log = ";" 
                        phys_to_log[phys] = log
        else:
            print(f"AHK file not found at: {self.ahk_path}")
        
        # Invert to Logical -> Physical
        log_to_phys = {}
        for p, l in phys_to_log.items():
            log_to_phys[l] = p
            
        return log_to_phys

    def setup_ui(self):
        self.info_lbl = tk.Label(self.root, text="Type the character shown below using Onishi Layout", font=("Arial", 12), fg="white", bg="#222")
        self.info_lbl.pack(pady=20)
        
        self.target_lbl = tk.Label(self.root, text="?", font=("Arial", 64, "bold"), fg="#00ff99", bg="#222")
        self.target_lbl.pack(pady=20)
        
        self.hint_lbl = tk.Label(self.root, text="Hint: Press [?]", font=("Arial", 18), fg="#aaaaaa", bg="#222")
        self.hint_lbl.pack(pady=10)
        
        self.score_lbl = tk.Label(self.root, text="Score: 0 / 0", font=("Arial", 12), fg="white", bg="#222")
        self.score_lbl.pack(pady=20)

    def next_question(self):
        available_chars = list(self.mapping.keys())
        available_chars = [c for c in available_chars if c.isalpha()]
        
        if not available_chars:
            self.target_char = "a"
            self.hint_lbl.config(text="(Mapping not found)")
        else:
            self.target_char = random.choice(available_chars)
            
        phys_key = self.mapping.get(self.target_char, "?").upper()
        
        self.target_lbl.config(text=self.target_char.upper())
        self.hint_lbl.config(text=f"Hint: Press Physical [{phys_key}]")

    def on_key_press(self, event):
        entered = event.char
        if not entered: return

        if entered.lower() == self.target_char.lower():
            self.score += 1
            self.info_lbl.config(text="Correct!", fg="#00ff99")
            self.next_question()
        else:
            self.info_lbl.config(text=f"Wrong... You typed '{entered}'", fg="red")
            
        self.total += 1
        self.score_lbl.config(text=f"Score: {self.score} / {self.total}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    t = OnishiTrainer()
    t.run()
