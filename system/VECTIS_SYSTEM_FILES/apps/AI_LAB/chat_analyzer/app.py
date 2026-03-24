"""
CHAT ANALYZER - チャット会話解析・保存ツール
会話ログをコピペして、自分と相手の発言を自動判別して保存
"""

import tkinter
# EGO共通UIモジュール
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from vectis_ui_modules import VectisUIFactory, setup_style
except ImportError:
    pass as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from datetime import datetime
import json
import os
import re

class ChatAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("CHAT ANALYZER - 会話解析ツール")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0e27")
        
        # データ保存用ディレクトリ
        self.save_dir = "saved_conversations"
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Diary連携用ディレクトリ（オプション）
        self.diary_chat_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "diary", 
            "data", 
            "chat_logs"
        ))
        os.makedirs(self.diary_chat_dir, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # タイトル
        title = tk.Label(
            self.root,
            text="💬 CHAT ANALYZER",
            font=("Arial", 24, "bold"),
            bg="#0a0e27",
            fg="#00ffff"
        )
        title.pack(pady=20)
        
        # メインコンテナ
        main_container = tk.Frame(self.root, bg="#0a0e27")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左側 - 入力エリア
        left_frame = tk.Frame(main_container, bg="#0a0e27")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📋 会話をここに貼り付け:",
            font=("Arial", 14, "bold"),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(anchor="w", pady=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1f3a",
            fg="#ffffff",
            insertbackground="#00ffff",
            relief=tk.FLAT
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 設定フレーム
        settings_frame = tk.Frame(left_frame, bg="#0a0e27")
        settings_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            settings_frame,
            text="あなたの名前:",
            font=("Arial", 10),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.user_name = tk.Entry(
            settings_frame,
            font=("Arial", 10),
            bg="#1a1f3a",
            fg="#ffffff",
            insertbackground="#00ffff",
            relief=tk.FLAT
        )
        self.user_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_name.insert(0, "自分")
        
        tk.Label(
            settings_frame,
            text="相手の名前:",
            font=("Arial", 10),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.other_name = tk.Entry(
            settings_frame,
            font=("Arial", 10),
            bg="#1a1f3a",
            fg="#ffffff",
            insertbackground="#00ffff",
            relief=tk.FLAT
        )
        self.other_name.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.other_name.insert(0, "相手")
        
        # ボタンフレーム
        btn_frame = tk.Frame(left_frame, bg="#0a0e27")
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.create_button(btn_frame, "🔍 解析開始", self.analyze_chat, "#00ff88")
        self.create_button(btn_frame, "💾 保存", self.save_chat, "#0088ff")
        self.create_button(btn_frame, "🗑️ クリア", self.clear_all, "#ff4444")
        
        # 右側 - 解析結果エリア
        right_frame = tk.Frame(main_container, bg="#0a0e27")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            right_frame,
            text="📊 解析結果:",
            font=("Arial", 14, "bold"),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(anchor="w", pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1f3a",
            fg="#ffffff",
            insertbackground="#00ffff",
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 統計情報
        stats_frame = tk.Frame(right_frame, bg="#0a0e27")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="統計: --",
            font=("Arial", 10),
            bg="#0a0e27",
            fg="#00ffff"
        )
        self.stats_label.pack(anchor="w")
        
        # 保存済み会話リスト
        tk.Label(
            right_frame,
            text="📚 保存済み会話:",
            font=("Arial", 12, "bold"),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(anchor="w", pady=(10, 5))
        
        list_frame = tk.Frame(right_frame, bg="#1a1f3a")
        list_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.saved_list = tk.Listbox(
            list_frame,
            height=6,
            font=("Consolas", 9),
            bg="#1a1f3a",
            fg="#ffffff",
            selectbackground="#0088ff",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.saved_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.saved_list.yview)
        
        self.saved_list.bind("<Double-Button-1>", self.load_conversation)
        
        self.refresh_saved_list()
        
        # データ構造
        self.current_conversation = None
        
    def create_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 11, "bold"),
            bg=color,
            fg="#000000",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # ホバー効果
        def on_enter(e):
            btn.config(bg=self.lighten_color(color))
        def on_leave(e):
            btn.config(bg=color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def lighten_color(self, color):
        """色を明るくする"""
        return color  # 簡易版
        
    def analyze_chat(self):
        """会話を解析して発言者を判別"""
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "会話テキストを入力してください")
            return
        
        user = self.user_name.get().strip()
        other = self.other_name.get().strip()
        
        # 会話を解析
        lines = text.split("\n")
        messages = []
        current_speaker = None
        current_message = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 発言者を検出（様々なパターンに対応）
            # パターン1: "名前: メッセージ"
            # パターン2: "[名前] メッセージ"
            # パターン3: "名前 > メッセージ"
            # パターン4: タイムスタンプ付き
            
            speaker_detected = False
            
            # パターン検出
            patterns = [
                rf"^({re.escape(user)}|{re.escape(other)})\s*[:：]\s*(.+)$",
                rf"^\[({re.escape(user)}|{re.escape(other)})\]\s*(.+)$",
                rf"^({re.escape(user)}|{re.escape(other)})\s*[>＞]\s*(.+)$",
                rf"^\d{{1,2}}:\d{{2}}\s*({re.escape(user)}|{re.escape(other)})\s*[:：]\s*(.+)$",
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # 前のメッセージを保存
                    if current_speaker and current_message:
                        messages.append({
                            "speaker": current_speaker,
                            "message": "\n".join(current_message)
                        })
                    
                    # 新しいメッセージ開始
                    current_speaker = match.group(1)
                    current_message = [match.group(2)]
                    speaker_detected = True
                    break
            
            # 発言者が検出されなかった場合は前の発言の続き
            if not speaker_detected:
                if current_speaker:
                    current_message.append(line)
                else:
                    # 最初の発言者が不明な場合は自分とする
                    current_speaker = user
                    current_message = [line]
        
        # 最後のメッセージを保存
        if current_speaker and current_message:
            messages.append({
                "speaker": current_speaker,
                "message": "\n".join(current_message)
            })
        
        # 結果を表示
        self.display_analysis(messages, user, other)
        
        # 現在の会話を保存
        self.current_conversation = {
            "timestamp": datetime.now().isoformat(),
            "participants": [user, other],
            "messages": messages
        }
        
    def display_analysis(self, messages, user, other):
        """解析結果を表示"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        user_count = 0
        other_count = 0
        user_chars = 0
        other_chars = 0
        
        for msg in messages:
            speaker = msg["speaker"]
            message = msg["message"]
            
            if speaker.lower() == user.lower():
                color_tag = "user"
                user_count += 1
                user_chars += len(message)
                prefix = f"🟦 {user}"
            else:
                color_tag = "other"
                other_count += 1
                other_chars += len(message)
                prefix = f"🟩 {other}"
            
            self.output_text.insert(tk.END, f"{prefix}:\n", color_tag + "_name")
            self.output_text.insert(tk.END, f"{message}\n\n", color_tag)
        
        # カラータグ設定
        self.output_text.tag_config("user_name", foreground="#00aaff", font=("Arial", 11, "bold"))
        self.output_text.tag_config("user", foreground="#aaddff")
        self.output_text.tag_config("other_name", foreground="#00ff88", font=("Arial", 11, "bold"))
        self.output_text.tag_config("other", foreground="#aaffdd")
        
        self.output_text.config(state=tk.DISABLED)
        
        # 統計情報更新
        total = user_count + other_count
        stats = (
            f"総メッセージ数: {total} | "
            f"{user}: {user_count}件 ({user_chars}文字) | "
            f"{other}: {other_count}件 ({other_chars}文字)"
        )
        self.stats_label.config(text=stats)
        
    def save_chat(self):
        """会話を保存"""
        if not self.current_conversation:
            messagebox.showwarning("警告", "保存する会話がありません。まず解析を実行してください。")
            return
        
        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        participants = "_".join(self.current_conversation["participants"])
        filename = f"{timestamp}_{participants}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        # 保存
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.current_conversation, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("成功", f"会話を保存しました:\n{filename}")
        self.refresh_saved_list()
        
    def load_conversation(self, event):
        """保存済み会話を読み込み"""
        selection = self.saved_list.curselection()
        if not selection:
            return
        
        filename = self.saved_list.get(selection[0])
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 名前を設定
            if len(data["participants"]) >= 2:
                self.user_name.delete(0, tk.END)
                self.user_name.insert(0, data["participants"][0])
                self.other_name.delete(0, tk.END)
                self.other_name.insert(0, data["participants"][1])
            
            # 結果を表示
            self.display_analysis(
                data["messages"],
                data["participants"][0],
                data["participants"][1]
            )
            
            self.current_conversation = data
            
        except Exception as e:
            messagebox.showerror("エラー", f"読み込みに失敗しました:\n{e}")
    
    def refresh_saved_list(self):
        """保存済み会話リストを更新"""
        self.saved_list.delete(0, tk.END)
        
        if os.path.exists(self.save_dir):
            files = sorted(
                [f for f in os.listdir(self.save_dir) if f.endswith(".json")],
                reverse=True
            )
            for f in files:
                self.saved_list.insert(tk.END, f)
    
    def clear_all(self):
        """すべてをクリア"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.stats_label.config(text="統計: --")
        self.current_conversation = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatAnalyzer(root)
    root.mainloop()
