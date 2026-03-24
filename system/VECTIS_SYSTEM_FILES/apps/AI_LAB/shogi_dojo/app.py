import customtkinter as ctk
import os
import sys
import subprocess
import datetime
import threading
from PIL import Image

# SYSTEM PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from EGO_SYSTEM_FILES.modules.unified_llm import UnifiedLLM

# CONFIG
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

FONT_HEADER = ("Impact", 24)
FONT_MAIN = ("Arial", 14)
FONT_MONO = ("Consolas", 12)

# PATHS
BASE_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
GUI_PATH = os.path.join(RESOURCES_DIR, "ShogiGUIv0.0.8.3/ShogiGUI/ShogiGUI.exe")
ENGINE_PATH = os.path.join(RESOURCES_DIR, "水匠5(211123)/水匠5/Suisho5-AVX2.exe")
LOG_FILE = os.path.join(BASE_DIR, "../../HISTORY_LOG.md")

import textwrap

from usi_client import USIEngine

class ShogiDojoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SHOGI DOJO - SUISHO SLAYER")
        self.geometry("1100x800")
        
        # LLM Client
        self.llm = UnifiedLLM(provider="ollama", model_name="phi4")
        self.engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/水匠5(211123)/水匠5/Suisho5-AVX2.exe"))
        
        # Tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_launch = self.tabs.add("🚀 LAUNCHER")
        self.tab_analysis = self.tabs.add("🧠 STRATEGY ROOM")
        self.tab_train = self.tabs.add("⚔️ DOJO TRAINING")
        self.tab_archive = self.tabs.add("📜 WINNING LOGS")
        
        self._init_launcher_tab()
        self._init_analysis_tab()
        self._init_training_tab()
        self._init_archive_tab()
        
    def _init_archive_tab(self):
        f = self.tab_archive
        
        # Left: File List
        self.log_list = ctk.CTkScrollableFrame(f, width=300, label_text="MATCH HISTORY")
        self.log_list.pack(side="left", fill="y", padx=10, pady=10)
        
        # Right: Viewer
        viewer = ctk.CTkFrame(f)
        viewer.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(viewer, text="GAME RECORD (SFEN)", font=FONT_HEADER).pack(pady=10)
        
        self.archive_text = ctk.CTkTextbox(viewer, font=FONT_MONO, height=150)
        self.archive_text.pack(fill="x", padx=10, pady=5)
        
        btn_box = ctk.CTkFrame(viewer, fg_color="transparent")
        btn_box.pack(pady=10)
        
        ctk.CTkButton(btn_box, text="📋 COPY SFEN TO CLIPBOARD", command=self.copy_archive_sfen, width=200, fg_color="#00afff").pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="🔄 REFRESH LIST", command=self.load_archive_list, width=150, fg_color="#333").pack(side="left", padx=10)
        
        self.lbl_archive_info = ctk.CTkLabel(viewer, text="Select a game to view details.", font=FONT_MAIN, text_color="gray")
        self.lbl_archive_info.pack(pady=20)
        
        self.load_archive_list()
        
    def load_archive_list(self):
        # Clear
        for widget in self.log_list.winfo_children():
            widget.destroy()
            
        log_dir = os.path.join(os.path.dirname(__file__), "training_logs")
        if not os.path.exists(log_dir):
            ctk.CTkLabel(self.log_list, text="No logs found.").pack()
            return
            
        files = sorted(os.listdir(log_dir), reverse=True)
        
        for fname in files:
            if not fname.endswith(".sfen"): continue
            
            # Color code by winner
            color = "#444"
            if "EGO" in fname: color = "#00ff41" # Win
            elif "SUISHO" in fname: color = "#ff5555" # Loss
            elif "DRAW" in fname: color = "#aaaaaa"
            
            btn = ctk.CTkButton(self.log_list, text=fname, fg_color="transparent", hover_color=color, border_width=1, border_color=color,
                                anchor="w", command=lambda f=fname: self.load_game_log(f))
            btn.pack(fill="x", pady=2)

    def load_game_log(self, filename):
        path = os.path.join(os.path.dirname(__file__), "training_logs", filename)
        try:
            with open(path, "r") as f:
                content = f.read()
            self.archive_text.delete("0.0", "end")
            self.archive_text.insert("0.0", content)
            self.lbl_archive_info.configure(text=f"Loaded: {int(len(content.split())/2)} Moves")
        except:
            self.lbl_archive_info.configure(text="Error reading file.")

    def copy_archive_sfen(self):
        content = self.archive_text.get("0.0", "end").strip()
        if content:
            # Format for ShogiGUI (USI command style)
            if content.startswith("startpos"):
                content = "position " + content
                
            self.clipboard_clear()
            self.clipboard_append(content)
            self.lbl_archive_info.configure(text="COPIED USI STRING! Paste in ShogiGUI as 'SFEN/Command'.", text_color="#00afff")
        
    def _init_training_tab(self):
        f = self.tab_train
        
        # Controls
        ctrl = ctk.CTkFrame(f, fg_color="#222")
        ctrl.pack(fill="x", padx=10, pady=10)
        
        self.btn_train = ctk.CTkButton(ctrl, text="▶ START SELF-PLAY (RL CYCLE)", width=200, fg_color="#ff5555", 
                                       command=self.toggle_training)
        self.btn_train.pack(side="left", padx=10, pady=10)
        
        self.lbl_train_status = ctk.CTkLabel(ctrl, text="STATUS: IDLE", font=("Consolas", 12))
        self.lbl_train_status.pack(side="left", padx=10)

        # Monitor
        self.train_log = ctk.CTkTextbox(f, font=FONT_MONO, fg_color="#000", text_color="#0f0")
        self.train_log.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.is_training = False
    
    def toggle_training(self):
        if not self.is_training:
            self.is_training = True
            self.btn_train.configure(text="⏹ STOP TRAINING")
            self.lbl_train_status.configure(text="STATUS: THINKING (USI)...")
            threading.Thread(target=self.training_loop, daemon=True).start()
        else:
            self.is_training = False
            self.btn_train.configure(text="▶ START SELF-PLAY (RL CYCLE)")
            self.lbl_train_status.configure(text="STATUS: STOPPING...")

from usi_client import USIEngine
from vectis_zero import VectisZero

class ShogiDojoApp(ctk.CTk):
    # ... (init remains similar)

    def training_loop(self):
        self.log_train("⚔️ PREPARING MATCH: EGO ZERO vs SUISHO 5 (ORIGINAL)")
        
        # 1. Init EGO ZERO (Challenger)
        player_A = VectisZero(self.engine_path)
        if not player_A.start():
            self.log_train("Failed to init EGO ZERO.")
            self.is_training = False
            return
        
        # 2. Init TARGET (Suisho 5)
        player_B = USIEngine(self.engine_path)
        if not player_B.start():
            self.log_train("Failed to init TARGET ENGINE.")
            player_A.stop()
            self.is_training = False
            return

        self.log_train("Match Started. EGO ZERO (Black) vs SUISHO 5 (White)")
        
        moves = []
        turn_count = 0
        
        while self.is_training:
            turn_count += 1
            is_black = (turn_count % 2 != 0)
            
            # Select Active Player
            active_player = player_A if is_black else player_B
            name = "EGO ZERO" if is_black else "SUISHO 5"
            
            self.log_train(f"Turn {turn_count}: {name} Thinking...")
            
            # Get Move
            if is_black:
                # Vectis Wrapper Logic
                best = active_player.get_move("startpos", moves, time_limit=800)
            else:
                # Raw Engine
                best = active_player.go("startpos", moves, time_limit=800)
            
            if not best or best == "resign":
                self.log_train(f"GAMEOVER: {name} Resigned. Winner: {'SUISHO 5' if is_black else 'EGO ZERO'}")
                break
                
            moves.append(best)
            self.log_train(f"{name} plays {best}")
            
            if len(moves) > 150:
                self.log_train("Draw (Repetition/Length).")
                break
                
        player_A.stop()
        player_B.stop()
        self.is_training = False
        self.log_train("Match Cycle Finished.")

        # SAVE GAME LOG
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        winner_tag = "DRAW"
        if len(moves) < 150: # Assume resign if not draw
             # If A (Black) moved last, then B (White) resigned? No, 'moves' contains the last move made.
             # If loop broke on 'resign' check, the last move was 'resign'.
             # But we don't append 'resign' to moves list.
             # If turn_count matches moves length:
             # Last player to move was 'Active Player'.
             # If Active Player resigned, they LOST.
             # turn_count is incremented at start of loop.
             # is_black based on turn_count.
             # 'best' is the move.
             # If best is resign/None, no move appended.
             # So winner is the OTHER player.
             
             last_turn_black = (turn_count % 2 != 0)
             # If Black was thinking and resigned, White (SUISHO) won.
             if last_turn_black:
                 winner_tag = "SUISHO"
             else:
                 winner_tag = "EGO"
        
        filename = f"game_{timestamp}_{winner_tag}.sfen"
        save_path = os.path.join(os.path.dirname(__file__), "training_logs", filename)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Construct USI String
        game_content = "startpos moves " + " ".join(moves)
        
        try:
            with open(save_path, "w") as f:
                f.write(game_content)
            self.log_train(f"Saved Game: {filename}")
            
            # Refresh List safely
            self.after(100, self.load_archive_list)
        except Exception as e:
            self.log_train(f"Error Saving: {e}")
        
    def log_train(self, text):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.train_log.insert("end", f"[{ts}] {text}\n")
        self.train_log.see("end")

    # ... (Keep Launcher and Analysis Tabs)
        
    def _init_launcher_tab(self):
        # ... (Previous Launcher Layout adapted to Tab)
        f = self.tab_launch
        
        # Title
        ctk.CTkLabel(f, text="VS SUISHO 5 - BATTLE STATION", font=FONT_HEADER, text_color="#ff5555").pack(pady=30)
        
        # Launch Button
        btn = ctk.CTkButton(f, text="LAUNCH SHOGI GUI", command=self.launch_shogi_gui, 
                            width=300, height=60, font=FONT_HEADER, fg_color="#ff9900")
        btn.pack(pady=20)
        
        ctk.CTkLabel(f, text="Target: 打倒 水匠5", font=FONT_MAIN).pack()

        # Simple Log for launcher
        self.launch_log = ctk.CTkTextbox(f, height=200)
        self.launch_log.pack(fill="x", padx=50, pady=20)
        self.log_launch("System ready. Engine: Suisho 5 (AVX2).")

    def _init_analysis_tab(self):
        f = self.tab_analysis
        
        # Layout: Left (Input), Right (Output)
        f.grid_columnconfigure(0, weight=1)
        f.grid_columnconfigure(1, weight=1)
        f.grid_rowconfigure(1, weight=1)
        
        # INPUT
        ctk.CTkLabel(f, text="INPUT SFEN (Board State)", font=FONT_MAIN).grid(row=0, column=0, pady=10)
        self.sfen_input = ctk.CTkTextbox(f, height=100)
        self.sfen_input.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.sfen_input.insert("0.0", "Paste SFEN here from ShogiGUI (Edit -> Copy SFEN)...")
        
        # BUTTON
        btn_explain = ctk.CTkButton(f, text="Explain Strategy \n(Phi-4/Gemini)", command=self.start_explanation,
                                    fg_color="#00ff41", text_color="black", height=50)
        btn_explain.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # OUPUT
        ctk.CTkLabel(f, text="TACTICAL BREAKDOWN", font=FONT_MAIN).grid(row=0, column=1, pady=10)
        self.explanation_box = ctk.CTkTextbox(f, font=FONT_MONO, state="normal")
        self.explanation_box.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        
    def start_explanation(self):
        sfen = self.sfen_input.get("0.0", "end").strip()
        if len(sfen) < 10:
            self.explanation_box.insert("end", "[ERR] Invalid SFEN.\n")
            return
            
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", "Constructing strategic analysis...\nTurning on Neural Engines...\n")
        
        threading.Thread(target=self._run_llm_analysis, args=(sfen,), daemon=True).start()
        
    def _run_llm_analysis(self, sfen):
        prompt = f"""
        【ROLE: Professional Shogi Coach】
        The user is trying to defeat the AI engine 'Suisho 5'.
        Analyze the following Shogi board state (SFEN string):
        
        {sfen}
        
        Please provide:
        1. **Current Situation**: Who has the initiative? What are the threats?
        2. **Candidate Moves**: List top 2-3 moves.
        3. **Deep Reasoning**: Explain WHY the best move is chosen. Focus on the flow of the pieces (Sabaki), safety of the King, and material advantage. Make it explicable for a human trying to understand computer logic.
        
        Format the output clearly in Markdown.
        """
        try:
            # Try Gemini first for complex analysis if available in Auto mode, else Phi4
            # We'll stick to UnifiedLLM default which handles this
            response = self.llm.generate(prompt)
            
            self.explanation_box.delete("0.0", "end")
            self.explanation_box.insert("0.0", response)
        except Exception as e:
            self.explanation_box.insert("end", f"\n[ERROR] Analysis failed: {e}")

    def log_launch(self, text):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.launch_log.insert("end", f"[{ts}] {text}\n")
        self.launch_log.see("end")

    # ... (Keep existing methods like check_engine, launch_shogi_gui but updated to use new layout refs)
    
    def launch_shogi_gui(self):
        if os.path.exists(GUI_PATH):
            self.log_launch("🚀 Launching ShogiGUI...")
            threading.Thread(target=self._run_process, args=(GUI_PATH,), daemon=True).start()
            self._log_history("SHOGI_LAUNCH", "Launched ShogiGUI for training.")
        else:
            self.log_launch("❌ ShogiGUI executable not found.")

    def _run_process(self, path):
        try:
            subprocess.Popen([path], cwd=os.path.dirname(path))
        except Exception as e:
            self.log_launch(f"Error launching: {e}")

    # ... (Keep _log_history, remove init logic from old class structure)


    def _log_history(self, event, details):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"| {ts} | {event} | {details} |\n"
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
        except: pass

if __name__ == "__main__":
    app = ShogiDojoApp()
    app.mainloop()
