import sys
import os
import threading
import subprocess

# Path Setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../modules")))

from modules.vectis_ui import VectisWindow, VectisButton, ConsolePanel, GlassCard
import customtkinter as ctk

class IntelligenceApp(VectisWindow):
    def __init__(self):
        super().__init__(title="INTELLIGENCE PATROL", width=1100, height=750)
        
        # --- Layout ---
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(1, weight=2)
        self.main_area.grid_rowconfigure(0, weight=1)
        
        # LEFT: Control Panel
        self.left_panel = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # RIGHT: Console / Bookshelf Preview
        self.right_panel = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        self.setup_controls()
        self.setup_console()
        
    def setup_controls(self):
        # Card 1: Operations
        self.card_ops = GlassCard(self.left_panel, title="OPERATIONS", height=200)
        self.card_ops.pack(fill="x", pady=(0, 10))
        
        VectisButton(self.card_ops.content, text="START MANUAL PATROL", command=self.run_manual).pack(fill="x", pady=5)
        VectisButton(self.card_ops.content, text="START CHAOS PATROL", command=self.run_chaos, type="danger").pack(fill="x", pady=5)
        
        # Card 2: Configuration
        self.card_cfg = GlassCard(self.left_panel, title="CONFIGURATION", height=200)
        self.card_cfg.pack(fill="x", pady=10)
        
        self.chk_var = ctk.StringVar(value="on")
        ctk.CTkCheckBox(self.card_cfg.content, text="Auto-Save to Universe", variable=self.chk_var, onvalue="on", offvalue="off").pack(anchor="w", pady=5)
        
        VectisButton(self.card_cfg.content, text="EDIT CHANNELS (JSON)", command=lambda: self.console.log("Not implemented yet"), type="ghost").pack(fill="x", pady=5)

    def setup_console(self):
        self.console_card = GlassCard(self.right_panel, title="LIVE TERMINAL OUTPUT")
        self.console_card.pack(fill="both", expand=True)
        
        self.console = ConsolePanel(self.console_card.content)
        self.console.pack(fill="both", expand=True)
        self.console.log("VECTIS Intelligence System [ONLINE]")
        self.console.log("Ready for instructions...")

    def run_worker(self, cmd_args, mode_name):
        self.console.clear()
        self.console.log(f"Initializing {mode_name}...")
        self.set_status(f"RUNNING: {mode_name}")
        
        def task():
            # Construct path to run_cli.py
            cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "run_cli.py"))
            cmd = [sys.executable, cli_path] + cmd_args
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1, 
                encoding='utf-8' # Force utf-8
            )
            
            for line in process.stdout:
                self.console.log(line.strip())
            
            process.wait()
            self.console.log(f"--- {mode_name} COMPLETE ---")
            self.set_status("READY")
            
        threading.Thread(target=task).start()

    def run_manual(self):
        self.run_worker(["--patrol"], "MANUAL PATROL")

    def run_chaos(self):
        self.run_worker(["--patrol", "--chaos"], "CHAOS PATROL")

if __name__ == "__main__":
    app = IntelligenceApp()
    app.mainloop()
