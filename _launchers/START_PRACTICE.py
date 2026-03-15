import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import webbrowser

class PracticeLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Thought OS - Interview Control Panel")
        self.root.geometry("400x550")
        self.root.configure(bg="#0a0f1e")

        # タイトル
        label = tk.Label(root, text="INTERVIEW CONTROL", fg="#00ffcc", bg="#0a0f1e", font=("Arial", 16, "bold"))
        label.pack(pady=20)

        # モード選択セクション
        self.create_button("練習モード (カンペあり)", self.start_practice_on, "#00ffcc", "#0a0f1e")
        self.create_button("実戦モード (カンペなし)", self.start_practice_off, "#ffcc00", "#0a0f1e")
        
        # セパレーター
        tk.Frame(root, height=2, bd=1, relief="sunken", bg="#333").pack(fill="x", padx=20, pady=20)

        # ツールセクション
        self.create_button("映像録画 (Recorder)", self.launch_video, "#ffffff", "#333")
        self.create_button("音声録音 (Audio Only)", self.launch_audio, "#ffffff", "#333")
        
        # ログ確認
        self.create_button("戦略ログ (Intel Log) を開く", self.open_log, "#aaaaaa", "#222")

        # ステータスバー
        self.status = tk.Label(root, text="READY: Optimizer Engine Online", fg="#555", bg="#0a0f1e", font=("Arial", 8))
        self.status.pack(side="bottom", pady=10)

    def create_button(self, text, command, fg, bg):
        btn = tk.Button(self.root, text=text, command=command, fg=fg, bg=bg, 
                        font=("Arial", 11, "bold"), width=30, height=2, relief="flat",
                        activebackground=fg, activeforeground=bg)
        btn.pack(pady=10)

    def start_practice_on(self):
        self.status.config(text="MODE: PROMPTER ON / RECORDING...")
        webbrowser.open(os.path.join(os.getcwd(), "INTERVIEW_PROMPTER.html"))
        subprocess.Popen(["python", "interview_recorder.py"])

    def start_practice_off(self):
        self.status.config(text="MODE: PROMPTER OFF / RECORDING...")
        subprocess.Popen(["python", "interview_recorder.py"])

    def launch_video(self):
        subprocess.Popen(["python", "interview_recorder.py"])

    def launch_audio(self):
        # 新しいコマンドプロンプトウィンドウで実行
        subprocess.Popen(["start", "cmd", "/k", "python", "audio_recorder.py"], shell=True)

    def open_log(self):
        os.startfile("STRATEGIC_INTEL_LOG.md")

if __name__ == "__main__":
    root = tk.Tk()
    app = PracticeLauncher(root)
    root.mainloop()
