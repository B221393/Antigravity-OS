import customtkinter as ctk
import os
import json
import random
import threading
from datetime import datetime
from PIL import Image

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "history_data.json")

# Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLOR_BG = "#1e1e1e"
COLOR_CARD = "#2b2b2b"
COLOR_ACCENT = "#00FFCC" # Cyan-ish
COLOR_TEXT = "#FFFFFF"

class HistoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🏛️ History Channel (Native)")
        self.geometry("1000x700")
        self.configure(fg_color=COLOR_BG)
        
        # Load Data
        self.events = self.load_data()
        self.quiz_data = [
            {"q": "1600年に起こった「天下分け目の戦い」は？", "a": ["関ヶ原の戦い", "桶狭間の戦い", "長篠の戦い", "本能寺の変"], "correct": "関ヶ原の戦い"},
            {"q": "織田信長が今川義元を破った戦いは？", "a": ["桶狭間の戦い", "姉川の戦い", "三方ヶ原の戦い", "長篠の戦い"], "correct": "桶狭間の戦い"},
            {"q": "江戸幕府を開いたのは誰？", "a": ["徳川家康", "豊臣秀吉", "織田信長", "明智光秀"], "correct": "徳川家康"},
            {"q": "1853年、浦賀に来航したアメリカ人は？", "a": ["ペリー", "ザビエル", "マッカーサー", "ハリス"], "correct": "ペリー"},
            {"q": "「敵は本能寺にあり」と言ったとされる武将は？", "a": ["明智光秀", "豊臣秀吉", "柴田勝家", "石田三成"], "correct": "明智光秀"},
        ]
        
        # Setup Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="🏛️ HISTORY", font=("Segoe UI", 20, "bold"), text_color=COLOR_ACCENT)
        self.logo.pack(pady=30, padx=20)
        
        self.btn_timeline = self.create_nav_btn("📜 Timeline", self.show_timeline)
        self.btn_quiz = self.create_nav_btn("🧠 Quiz", self.show_quiz)
        self.btn_tutor = self.create_nav_btn("🤖 Tutor", self.show_tutor)
        
        # Main Area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Initial View
        self.show_timeline()

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def save_learning_log(self, text, score=0):
        # Save to Bookshelf (Threaded to avoid freeze)
        def _save():
            try:
                book_dir = os.path.abspath(os.path.join(BASE_DIR, "../../OBSIDIAN_WRITING/BOOKSHELF/05_Manual_Notes"))
                os.makedirs(book_dir, exist_ok=True)
                book_path = os.path.join(book_dir, "History_Learning_Log.md")
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Format: | Date | Type | Content | Score |
                entry = f"| {timestamp} | ✅ Learned | {text} | {score} |\n"
                
                # Create header if new (though we just handled it externally, good safety)
                if not os.path.exists(book_path):
                    with open(book_path, "w", encoding="utf-8") as f:
                        f.write("# 🏛️ History Learning Log\n*Personal Knowledge Archive regarding History and General Arts.*\n\n## 📅 Learning Log\n\n| Timestamp | Type | Content | Score |\n|---|---|---|---|\n")
                
                with open(book_path, "a", encoding="utf-8") as f:
                    f.write(entry)
                print(f"Saved to Bookshelf: {book_path}")
            except Exception as e:
                print(f"Save failed: {e}")
        
        threading.Thread(target=_save, daemon=True).start()

    def create_nav_btn(self, text, cmd):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", hover_color="#444", anchor="w", command=cmd)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- VIEWS ---
    def show_timeline(self):
        self.clear_main()
        lbl = ctk.CTkLabel(self.main_frame, text="⏳ Chrono Stream", font=("Segoe UI", 24, "bold"))
        lbl.pack(pady=(0, 20), anchor="w")
        
        scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        for event in self.events:
            card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            
            row1 = ctk.CTkFrame(card, fg_color="transparent")
            row1.pack(fill="x", padx=10, pady=(10, 0))
            
            ctk.CTkLabel(row1, text=str(event['year']), font=("Consolas", 18, "bold"), text_color=COLOR_ACCENT).pack(side="left")
            ctk.CTkLabel(row1, text=f" [{event['era']}]", text_color="#888").pack(side="left", padx=5)
            
            ctk.CTkLabel(card, text=event['title'], font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", padx=10, pady=(5, 0))
            ctk.CTkLabel(card, text=event['desc'], font=("Segoe UI", 12), text_color="#CCC", anchor="w", wraplength=600).pack(fill="x", padx=10, pady=(5, 10))

    def show_quiz(self):
        self.clear_main()
        lbl = ctk.CTkLabel(self.main_frame, text="🧠 Knowledge Check", font=("Segoe UI", 24, "bold"))
        lbl.pack(pady=(0, 20), anchor="w")
        
        self.current_q_idx = 0
        self.quiz_score = 0
        
        self.quiz_container = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CARD)
        self.quiz_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.render_next_question()

    def render_next_question(self):
        for w in self.quiz_container.winfo_children(): w.destroy()
        
        if self.current_q_idx >= len(self.quiz_data):
            ctk.CTkLabel(self.quiz_container, text="🎉 COMPLETE!", font=("Segoe UI", 30, "bold"), text_color=COLOR_ACCENT).pack(pady=40)
            ctk.CTkLabel(self.quiz_container, text=f"Score: {self.quiz_score}", font=("Segoe UI", 20)).pack()
            ctk.CTkButton(self.quiz_container, text="Restart", command=self.show_quiz).pack(pady=20)
            return

        q = self.quiz_data[self.current_q_idx]
        
        ctk.CTkLabel(self.quiz_container, text=f"Question {self.current_q_idx + 1}", text_color="#888").pack(pady=(20, 5))
        ctk.CTkLabel(self.quiz_container, text=q['q'], font=("Segoe UI", 18, "bold"), wraplength=500).pack(pady=(0, 30))
        
        opts = q['a'].copy()
        random.shuffle(opts)
        
        for opt in opts:
            btn = ctk.CTkButton(self.quiz_container, text=opt, width=300, height=40, font=("Segoe UI", 14),
                                command=lambda o=opt: self.check_answer(o, q))
            btn.pack(pady=8)

    def check_answer(self, ans, q_data):
        if ans == q_data['correct']:
            self.quiz_score += 10
            self.save_learning_log(f"Correct: {q_data['q']} -> {ans}", 10)
        self.current_q_idx += 1
        self.render_next_question()

    def show_tutor(self):
        self.clear_main()
        lbl = ctk.CTkLabel(self.main_frame, text="🤖 AI Tutor (Mock)", font=("Segoe UI", 24, "bold"))
        lbl.pack(pady=(0, 20), anchor="w")
        
        ctk.CTkLabel(self.main_frame, text="Ask about history...").pack(anchor="w")
        self.entry_q = ctk.CTkEntry(self.main_frame, placeholder_text="Ex: Why did Edo period end?", width=400)
        self.entry_q.pack(pady=10, anchor="w")
        
        ctk.CTkButton(self.main_frame, text="Search", command=self.run_search).pack(anchor="w")
        
        self.txt_res = ctk.CTkTextbox(self.main_frame, width=600, height=300)
        self.txt_res.pack(pady=20, anchor="w")

    def run_search(self):
        q = self.entry_q.get()
        self.txt_res.delete("0.0", "end")
        self.txt_res.insert("0.0", f"Searching for: {q}...\n(In native mode, we'll connect this to the ResearchAgent module.)\n\n[Search Result]\nTitle: History of {q}\nContent: This is a placeholder for actual search results.")
        self.save_learning_log(f"Researched: {q}", 0)

if __name__ == "__main__":
    app = HistoryApp()
    app.mainloop()
