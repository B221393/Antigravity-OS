"""
TEXT ROUTER - 文章仕分け装置
テキストを解析して適切なアプリに自動振り分け（マインクラフトの仕分け装置風）
+ 知識として蓄積（Knowledge Cards + Ego Memory）
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import os
# EGO共通スタイル
import sys
import os

# Ensure VECTIS_SYSTEM_FILES and UTILS are importable
current_dir = os.path.dirname(os.path.abspath(__file__))
vectis_root = os.path.abspath(os.path.join(current_dir, "../../.."))  # To VECTIS_SYSTEM_FILES
apps_root = os.path.abspath(os.path.join(current_dir, "../.."))      # To apps
utils_path = os.path.join(apps_root, "UTILS")

if vectis_root not in sys.path:
    sys.path.insert(0, vectis_root)
if apps_root not in sys.path:
    sys.path.insert(0, apps_root)
if utils_path not in sys.path:
    sys.path.append(utils_path)

try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except ImportError:
    pass

# Helper to import Google Calendar Client
try:
    from calendar.google_calendar_client import GoogleCalendarClient
except ImportError:
    # Try alternate import if package structure differs
    try:
        sys.path.append(os.path.join(utils_path, "calendar"))
        from google_calendar_client import GoogleCalendarClient
    except ImportError:
        GoogleCalendarClient = None
        print("Warning: GoogleCalendarClient could not be imported.")
import re
from datetime import datetime
import json

class TextRouter:
    def __init__(self, root):
        self.root = root
        self.root.title("TEXT ROUTER - 文章仕分け装置")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0f0f23")
        
        # アプリマッピング定義
        self.app_routes = self.load_routes()
        
        # ルーティングログ
        self.routing_log = []
        
        # 知識保存先パス
        base_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.knowledge_dir = os.path.join(base_app_path, "knowledge_cards", "outputs", "cards")
        self.ego_memory_dir = os.path.join(base_app_path, "memory", "data")
        
        # ディレクトリ作成
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.ego_memory_dir, exist_ok=True)
        
        self.setup_ui()
        
    def load_routes(self):
        """アプリケーションルートを定義"""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        return {
            "就活・ES関連": {
                "keywords": ["就活", "就職", "エントリーシート", "ES", "面接", "インターン", "企業", "志望動機", "自己PR"],
                "app_path": os.path.join(base_path, "es_assistant", "es_quick_launch.bat"),
                "app_type": "bat",
                "icon": "💼",
                "priority": 10
            },
            "チャット会話": {
                "keywords": ["会話", "チャット", "LINE", "Discord", "メッセージ", "トーク"],
                "app_path": os.path.join(base_path, "chat_analyzer", "chat_analyzer.bat"),
                "app_type": "bat",
                "icon": "💬",
                "priority": 9
            },
            "将棋": {
                "keywords": ["将棋", "shogi", "藤井聡太", "棋譜", "対局", "王手", "詰み"],
                "app_path": os.path.join(base_path, "shogi_dojo", "app_gui.py"),
                "app_type": "python",
                "icon": "♟️",
                "priority": 8
            },
            "YouTube": {
                "keywords": ["youtube", "youtu.be", "動画", "チャンネル", "配信"],
                "app_path": os.path.join(base_path, "youtube_summarizer", "app.py"),
                "app_type": "streamlit",
                "icon": "📺",
                "priority": 7
            },
            "スケジュール": {
                "keywords": ["予定", "スケジュール", "カレンダー", "締切", "期限", "タスク", "TODO"],
                "app_path": os.path.join(base_path, "schedule_magi", "app.py"),
                "app_type": "streamlit",
                "icon": "📅",
                "priority": 9
            },
            "日記・メモ": {
                "keywords": ["日記", "diary", "メモ", "記録", "思い出"],
                "app_path": os.path.join(base_path, "diary", "app.py"),
                "app_type": "streamlit",
                "icon": "📔",
                "priority": 6
            },
            "検索・リサーチ": {
                "keywords": ["検索", "調査", "リサーチ", "調べる", "情報", "ニュース"],
                "app_path": os.path.join(base_path, "deep_search", "app.py"),
                "app_type": "streamlit",
                "icon": "🔍",
                "priority": 5
            },
            "プログラミング": {
                "keywords": ["コード", "プログラム", "python", "javascript", "バグ", "エラー", "開発"],
                "app_path": os.path.join(base_path, "vectis_coder", "app.py"),
                "app_type": "streamlit",
                "icon": "💻",
                "priority": 7
            },
            "英語・TOEIC": {
                "keywords": ["英語", "TOEIC", "英単語", "リスニング", "リーディング"],
                "app_path": os.path.join(base_path, "toeic_mastery", "app.py"),
                "app_type": "streamlit",
                "icon": "🇬🇧",
                "priority": 6
            },
            "その他・汎用": {
                "keywords": [],  # 最後のフォールバック
                "app_path": os.path.join(base_path, "vectis_omni", "app.py"),
                "app_type": "streamlit",
                "icon": "🌐",
                "priority": 1
            }
        }
    
    def setup_ui(self):
        # ヘッダー
        header = tk.Frame(self.root, bg="#1a1a2e", height=100)
        header.pack(fill=tk.X, padx=0, pady=0)
        
        title = tk.Label(
            header,
            text="🔀 TEXT ROUTER",
            font=("Arial", 28, "bold"),
            bg="#1a1a2e",
            fg="#00d9ff"
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            header,
            text="テキストを解析して適切なアプリに自動振り分け",
            font=("Arial", 12),
            bg="#1a1a2e",
            fg="#aaaaaa"
        )
        subtitle.pack()
        
        # メインコンテナ
        main_container = tk.Frame(self.root, bg="#0f0f23")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左側 - 入力エリア
        left_frame = tk.Frame(main_container, bg="#0f0f23", width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        input_label = tk.Label(
            left_frame,
            text="📝 テキストを入力してください:",
            font=("Arial", 14, "bold"),
            bg="#0f0f23",
            fg="#ffffff"
        )
        input_label.pack(anchor="w", pady=(0, 10))
        
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#1a1f35",
            fg="#ffffff",
            insertbackground="#00d9ff",
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # ボタンフレーム
        btn_frame = tk.Frame(left_frame, bg="#0f0f23")
        btn_frame.pack(fill=tk.X, pady=15)
        
        self.route_btn = self.create_button(
            btn_frame,
            "🚀 仕分け開始",
            self.analyze_and_route,
            "#00ff88",
            14
        )
        self.route_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)
        
        self.clear_btn = self.create_button(
            btn_frame,
            "🗑️ クリア",
            self.clear_input,
            "#ff4444",
            14
        )
        self.clear_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # 中央 - ルーティングビジュアル
        center_frame = tk.Frame(main_container, bg="#0f0f23", width=400)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10)
        
        visual_label = tk.Label(
            center_frame,
            text="🔀 ルーティング状態:",
            font=("Arial", 14, "bold"),
            bg="#0f0f23",
            fg="#ffffff"
        )
        visual_label.pack(anchor="w", pady=(0, 10))
        
        # ルーティングキャンバス
        self.routing_canvas = tk.Canvas(
            center_frame,
            bg="#1a1f35",
            highlightthickness=0,
            width=350,
            height=600
        )
        self.routing_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右側 - 解析結果とアプリ一覧
        right_frame = tk.Frame(main_container, bg="#0f0f23")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        result_label = tk.Label(
            right_frame,
            text="📊 解析結果:",
            font=("Arial", 14, "bold"),
            bg="#0f0f23",
            fg="#ffffff"
        )
        result_label.pack(anchor="w", pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#1a1f35",
            fg="#ffffff",
            relief=tk.FLAT,
            height=15,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=False, pady=(0, 20))
        
        # アプリ一覧
        apps_label = tk.Label(
            right_frame,
            text="🎯 利用可能なアプリ:",
            font=("Arial", 14, "bold"),
            bg="#0f0f23",
            fg="#ffffff"
        )
        apps_label.pack(anchor="w", pady=(0, 10))
        
        # アプリリストフレーム（スクロール可能）
        apps_container = tk.Frame(right_frame, bg="#1a1f35")
        apps_container.pack(fill=tk.BOTH, expand=True)
        
        apps_canvas = tk.Canvas(apps_container, bg="#1a1f35", highlightthickness=0)
        scrollbar = tk.Scrollbar(apps_container, orient="vertical", command=apps_canvas.yview)
        self.apps_frame = tk.Frame(apps_canvas, bg="#1a1f35")
        
        self.apps_frame.bind(
            "<Configure>",
            lambda e: apps_canvas.configure(scrollregion=apps_canvas.bbox("all"))
        )
        
        apps_canvas.create_window((0, 0), window=self.apps_frame, anchor="nw")
        apps_canvas.configure(yscrollcommand=scrollbar.set)
        
        apps_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.populate_app_list()
        self.draw_initial_routing()
        
    def populate_app_list(self):
        """アプリ一覧を表示"""
        sorted_apps = sorted(
            self.app_routes.items(),
            key=lambda x: x[1]["priority"],
            reverse=True
        )
        
        for i, (name, info) in enumerate(sorted_apps):
            app_card = tk.Frame(self.apps_frame, bg="#252540", relief=tk.FLAT)
            app_card.pack(fill=tk.X, padx=5, pady=5)
            
            # アプリ情報
            header_frame = tk.Frame(app_card, bg="#252540")
            header_frame.pack(fill=tk.X, padx=10, pady=8)
            
            icon_label = tk.Label(
                header_frame,
                text=info["icon"],
                font=("Arial", 20),
                bg="#252540",
                fg="#ffffff"
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            name_label = tk.Label(
                header_frame,
                text=name,
                font=("Arial", 12, "bold"),
                bg="#252540",
                fg="#00d9ff",
                anchor="w"
            )
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # キーワード表示
            keywords_text = ", ".join(info["keywords"][:5])
            if len(info["keywords"]) > 5:
                keywords_text += "..."
            
            keywords_label = tk.Label(
                app_card,
                text=f"キーワード: {keywords_text}",
                font=("Arial", 9),
                bg="#252540",
                fg="#888888",
                anchor="w"
            )
            keywords_label.pack(fill=tk.X, padx=10, pady=(0, 8))
            
            # 起動ボタン
            launch_btn = tk.Button(
                app_card,
                text="起動",
                command=lambda n=name: self.launch_app(n),
                font=("Arial", 9, "bold"),
                bg="#0088ff",
                fg="#ffffff",
                relief=tk.FLAT,
                cursor="hand2"
            )
            launch_btn.pack(pady=(0, 8), padx=10, anchor="e")
    
    def draw_initial_routing(self):
        """初期ルーティング図を描画"""
        canvas = self.routing_canvas
        canvas.delete("all")
        
        # 入力ボックス
        canvas.create_rectangle(50, 50, 300, 120, fill="#00d9ff", outline="")
        canvas.create_text(175, 85, text="📥 INPUT", font=("Arial", 16, "bold"), fill="#000000")
        
        # 中央処理ノード
        canvas.create_oval(100, 200, 250, 350, fill="#ff00ff", outline="")
        canvas.create_text(175, 275, text="🔀\nROUTER", font=("Arial", 14, "bold"), fill="#ffffff")
        
        # 矢印
        canvas.create_line(175, 120, 175, 200, arrow=tk.LAST, width=3, fill="#00ff88")
        
        # 出力ノード（複数）
        outputs = [
            (50, 450, "💼"),
            (150, 500, "💬"),
            (250, 450, "📺"),
        ]
        
        for x, y, icon in outputs:
            canvas.create_oval(x-30, y-30, x+30, y+30, fill="#00ff88", outline="")
            canvas.create_text(x, y, text=icon, font=("Arial", 20))
            canvas.create_line(175, 350, x, y-30, width=2, fill="#666666", dash=(5, 5))
    
    def animate_routing(self, target_category):
        """ルーティングアニメーション"""
        canvas = self.routing_canvas
        canvas.delete("all")
        
        # 入力
        canvas.create_rectangle(50, 50, 300, 120, fill="#00d9ff", outline="")
        canvas.create_text(175, 85, text="📥 INPUT", font=("Arial", 16, "bold"), fill="#000000")
        
        # ルーター（アクティブ）
        canvas.create_oval(100, 200, 250, 350, fill="#ff00ff", outline="#ffffff", width=3)
        canvas.create_text(175, 275, text="🔀\nROUTER\nACTIVE", font=("Arial", 12, "bold"), fill="#ffffff")
        
        # 矢印
        canvas.create_line(175, 120, 175, 200, arrow=tk.LAST, width=4, fill="#00ff88")
        
        # ターゲット出力（ハイライト）
        info = self.app_routes[target_category]
        canvas.create_rectangle(50, 450, 300, 550, fill="#00ff88", outline="#ffffff", width=3)
        canvas.create_text(175, 475, text=info["icon"], font=("Arial", 30))
        canvas.create_text(175, 520, text=target_category, font=("Arial", 12, "bold"), fill="#000000")
        
        canvas.create_line(175, 350, 175, 450, arrow=tk.LAST, width=5, fill="#00ff88")
    

    def analyze_and_route(self):
        """テキストを解析して適切なアプリにルーティング + Ollama AI解析"""
        text = self.input_text.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("警告", "テキストを入力してください")
            return
        
        # 1. 従来のキーワード解析（高速・確実）
        text_lower = text.lower()
        scores = {}
        
        for category, info in self.app_routes.items():
            score = 0
            matched_keywords = []
            for keyword in info["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_keywords.append(keyword)
            score += info["priority"] * 0.1
            if score > 0:
                scores[category] = {
                    "score": score,
                    "matched_keywords": matched_keywords
                }
        
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1]["score"])[0]
        else:
            best_category = "その他・汎用"

        self.display_routing_result(best_category, scores, text)
        self.animate_routing(best_category)
        self.log_routing(text, best_category)
        
        self.save_as_knowledge(text, best_category, scores)
        self.save_to_ego_memory(text, best_category)

        # 2. Ollama AIによる高度解析と自動登録
        # キーワードで見つかったカテゴリとは別に、タスク/予定としての性質を判断
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, "\n🧠 AI(Ollama)が解析中...\n", "info")
        self.result_text.config(state=tk.DISABLED)
        self.root.update()

        ai_result = self.analyze_with_ollama(text)
        
        if ai_result:
            action_type = ai_result.get("type")
            if action_type == "schedule":
                self.save_to_calendar(ai_result)
                messagebox.showinfo("AI自動処理", f"📅 カレンダーに予定を追加しました:\n{ai_result.get('title')} ({ai_result.get('date')})")
            elif action_type == "todo":
                self.save_to_todo(ai_result)
                messagebox.showinfo("AI自動処理", f"📋 TODOリストに追加しました:\n{ai_result.get('title')}")
        
        # 確認ダイアログ (AI処理が終わってから)
        result = messagebox.askyesno(
            "ルーティング結果",
            f"「{best_category}」に振り分けられました。\n\n✅ 知識カードとエゴメモリに保存しました。\n" + 
            (f"\n✅ AIが「{ai_result['type']}」として自動登録しました。" if ai_result and ai_result.get('type') != 'other' else "") + 
            "\n\nこのアプリを起動しますか？"
        )
        
        if result:
            self.launch_app(best_category, text)

    def analyze_with_ollama(self, text):
        """Ollama APIを使用してテキストを解析"""
        try:
            import urllib.request
            
            url = "http://localhost:11434/api/generate"
            today_str = datetime.now().strftime("%Y-%m-%d (%A)")
            
            prompt = f"""
            You are a smart personal assistant. Analyze the text and classify it into 'schedule', 'todo', or 'other'.
            Current Date: {today_str}
            
            Text: "{text}"
            
            If it involves a specific date/time or deadline, it is a 'schedule'.
            If it is a task without a specific date, it is a 'todo'.
            Otherwise 'other'.

            Extract:
            - title (summary of action)
            - date (YYYY-MM-DD format if applicable, calculate from relative terms like 'tomorrow', 'next week'. Return null if none)
            - category (Choose one: 'Job', 'Deadline', 'Study', 'Personal')
            - memo (details)

            Return JSON ONLY. No markdown.
            Format:
            {{
                "type": "schedule" | "todo" | "other",
                "title": "string",
                "date": "YYYY-MM-DD" | null,
                "category": "string",
                "memo": "string"
            }}
            """
            
            
            data = {
                "model": "glm-4.7-flash", # User requested specific model name
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            req = urllib.request.Request(
                url, 
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                response_text = result.get('response', '{}')
                
                # GLM-4 might return markdown code block even with format json sometimes
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                parsed = json.loads(response_text)
                
                # Debug display
                self.result_text.config(state=tk.NORMAL)
                self.result_text.insert(tk.END, f"\n🤖 AI Analysis:\n{json.dumps(parsed, indent=2, ensure_ascii=False)}\n", "keyword")
                self.result_text.config(state=tk.DISABLED)
                
                return parsed

        except Exception as e:
            print(f"Ollama Error: {e}")
            self.result_text.config(state=tk.NORMAL)
            self.result_text.insert(tk.END, f"\n⚠️ AI解析エラー (Ollamaが起動していない可能性があります): {e}\n", "info")
            self.result_text.config(state=tk.DISABLED)
            return None

    def save_to_calendar(self, data):
        """カレンダーに保存 (Google Calendar API優先 -> ローカルJSON)"""
        
        # 1. Try Google Calendar API
        google_success = False
        if GoogleCalendarClient:
            print("Attempting to sync with Google Calendar...")
            try:
                gcal = GoogleCalendarClient()
                
                # Format date/time
                start_date = data.get("date") # YYYY-MM-DD
                if not start_date:
                    start_date = datetime.now().strftime("%Y-%m-%d")
                    
                # Description
                desc = f"Category: {data.get('category')}\nMemo: {data.get('memo', '')}\nCreated via Text Router"
                
                # Add Event
                event = gcal.add_event(
                    title=data.get("title", "No Title"),
                    start_dt=start_date,
                    description=desc
                )
                
                if event:
                    print("✅ Google Calendar Sync Successful")
                    google_success = True
                    # Update local data to reflect sync? 
                    # For now we still save local log but maybe mark it?
                
            except Exception as e:
                print(f"⚠️ Google Calendar Sync Failed: {e}")
                # Don't show error box yet, just fallback silently to local or show warning in log
        
        # 2. Save to Local JSON (Backup & VECTIS Internal View)
        try:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "UTILS", "calendar"))
            json_path = os.path.join(base_path, "events.json")
            
            events = []
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            # Map category
            cat_map = {
                "Job": "💼 就活",
                "Deadline": "🔴 締切",
                "Study": "📝 その他", 
                "Personal": "📝 その他"
            }
            category = cat_map.get(data.get("category"), "📝 その他")
            
            new_event = {
                "id": str(datetime.now().timestamp()),
                "title": data.get("title", "No Title"),
                "date": data.get("date") if data.get("date") else datetime.now().strftime("%Y-%m-%d"),
                "time": "",
                "category": category,
                "memo": data.get("memo", ""),
                "created": datetime.now().isoformat(),
                "google_synced": google_success
            }
            
            events.append(new_event)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
                
            print(f"Saved to Calendar (Local): {json_path}")
            
        except Exception as e:
            print(f"Calendar Save Error: {e}")
            messagebox.showerror("保存エラー", f"カレンダーへの保存に失敗しました:\n{e}")

    def save_to_todo(self, data):
        """Todo(todo_log.json)に保存"""
        try:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "UTILS", "todo", "data"))
            json_path = os.path.join(base_path, "todo_log.json")
            
            # ディレクトリがない場合は作成
            os.makedirs(base_path, exist_ok=True)
            
            todos = []
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
            
            # Map category
            # CATEGORIES = ["🎬 アニメ/ドラマ鑑賞", "📖 小説/読書", "💻 プログラミング/技術", "📝 創作/執筆", "🔬 研究/学習", "🧘 自己研鑽/日常"]
            cat_lower = data.get("category", "").lower()
            if "job" in cat_lower or "work" in cat_lower:
                cat = "🧘 自己研鑽/日常"
            elif "study" in cat_lower:
                cat = "🔬 研究/学習"
            elif "code" in cat_lower or "tech" in cat_lower:
                cat = "💻 プログラミング/技術"
            else:
                cat = "🧘 自己研鑽/日常"

            new_todo = {
                "id": str(datetime.now().timestamp()),
                "title": data.get("title", "No Title"),
                "cat": cat,
                "note": data.get("memo", "") + " (from Item Sorter)",
                "done": False,
                "created": datetime.now().isoformat()
            }
            
            todos.append(new_todo)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(todos, f, indent=2, ensure_ascii=False)
                
            print(f"Saved to Todo: {json_path}")

        except Exception as e:
            print(f"Todo Save Error: {e}")
            messagebox.showerror("保存エラー", f"Todoへの保存に失敗しました:\n{e}")

    def display_routing_result(self, best_category, scores, original_text):
        """ルーティング結果を表示"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        
        self.result_text.insert(tk.END, "=" * 50 + "\n", "header")
        self.result_text.insert(tk.END, f"🎯 ルーティング結果: {best_category}\n", "result")
        self.result_text.insert(tk.END, "=" * 50 + "\n\n", "header")
        
        if scores:
            self.result_text.insert(tk.END, "📊 スコア詳細:\n\n", "subheader")
            
            sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
            for category, info in sorted_scores:
                is_best = category == best_category
                tag = "best" if is_best else "normal"
                
                prefix = "👉 " if is_best else "   "
                self.result_text.insert(
                    tk.END,
                    f"{prefix}{category}: {info['score']:.1f}点\n",
                    tag
                )
                
                if info["matched_keywords"]:
                    keywords = ", ".join(info["matched_keywords"])
                    self.result_text.insert(tk.END, f"      マッチ: {keywords}\n", "keyword")
                
                self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "キーワードが見つからなかったため、汎用アプリに振り分けます。\n", "info")
        
        # タグ設定
        self.result_text.tag_config("header", foreground="#00d9ff", font=("Consolas", 10))
        self.result_text.tag_config("result", foreground="#00ff88", font=("Arial", 14, "bold"))
        self.result_text.tag_config("subheader", foreground="#ffffff", font=("Arial", 11, "bold"))
        self.result_text.tag_config("best", foreground="#00ff88", font=("Consolas", 11, "bold"))
        self.result_text.tag_config("normal", foreground="#aaaaaa", font=("Consolas", 10))
        self.result_text.tag_config("keyword", foreground="#ff00ff", font=("Consolas", 9))
        self.result_text.tag_config("info", foreground="#ffaa00")
        
        self.result_text.config(state=tk.DISABLED)
    
    def launch_app(self, category, text_to_pass=None):
        """指定されたアプリを起動"""
        info = self.app_routes[category]
        app_path = info["app_path"]
        app_type = info.get("app_type", "python")
        
        if not os.path.exists(app_path):
            messagebox.showwarning("警告", f"アプリが見つかりません:\n{app_path}")
            return
        
        try:
            if app_type == "bat":
                # バッチファイルを起動
                subprocess.Popen([app_path], shell=True)
            elif app_type == "streamlit":
                # Streamlitアプリを起動
                subprocess.Popen(["streamlit", "run", app_path], shell=True)
            elif app_type == "python":
                # Pythonアプリを起動
                subprocess.Popen(["pythonw", app_path])
            else:
                # デフォルトはPython
                subprocess.Popen(["pythonw", app_path])
            
            messagebox.showinfo("起動", f"{category} を起動しました")
        except Exception as e:
            messagebox.showerror("エラー", f"起動に失敗しました:\n{e}")
    
    def log_routing(self, text, category):
        """ルーティングログを記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "routed_to": category
        }
        self.routing_log.append(log_entry)
        
        # ログをファイルに保存
        log_file = "routing_log.json"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except:
            pass
    
    def save_as_knowledge(self, text, category, scores):
        """テキストを知識カードとして保存"""
        try:
            # レアリティ判定（スコアに基づく）
            max_score = max([s["score"] for s in scores.values()]) if scores else 0
            if max_score >= 5:
                rarity = "Legendary"
            elif max_score >= 3:
                rarity = "Epic"
            elif max_score >= 2:
                rarity = "Rare"
            elif max_score >= 1:
                rarity = "Uncommon"
            else:
                rarity = "Common"
            
            # 知識カードデータ構造
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            card_data = {
                "title": f"{category} - {timestamp[:10]}",
                "genre": category,
                "rarity": rarity,
                "timestamp": timestamp,
                "content": text[:500],  # 最初の500文字
                "source": "Text Router - 自動仕分け",
                "full_text": text,
                "routing_scores": {k: v["score"] for k, v in scores.items()} if scores else {}
            }
            
            # ファイル名を生成
            safe_title = card_data["title"].replace(" ", "_").replace(":", "-")
            filename = f"{safe_title}_{datetime.now().strftime('%H%M%S')}.kcard"
            filepath = os.path.join(self.knowledge_dir, filename)
            
            # 保存
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(card_data, f, ensure_ascii=False, indent=4)
            
            print(f"📚 Knowledge Card saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save knowledge card: {e}")
    
    def save_to_ego_memory(self, text, category):
        """テキストをエゴメモリとして保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # エゴメモリデータ構造
            ego_data = {
                "type": "thought",
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "content": text,
                "context": {
                    "source": "text_router",
                    "auto_captured": True,
                    "routed_category": category
                },
                "metadata": {
                    "length": len(text),
                    "has_keywords": category != "その他・汎用"
                }
            }
            
            # ファイル名を生成
            filename = f"ego_thought_{timestamp}_{category.replace('・', '_')}.json"
            filepath = os.path.join(self.ego_memory_dir, filename)
            
            # 保存
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(ego_data, f, ensure_ascii=False, indent=2)
            
            print(f"🧠 Ego Memory saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save ego memory: {e}")
    
    def clear_input(self):
        """入力をクリア"""
        self.input_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.draw_initial_routing()
    
    def create_button(self, parent, text, command, color, font_size=11):
        """ボタンを作成"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", font_size, "bold"),
            bg=color,
            fg="#000000" if color in ["#00ff88", "#00d9ff"] else "#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=12
        )
        return btn

if __name__ == "__main__":
    root = tk.Tk()
    app = TextRouter(root)
    root.mainloop()
