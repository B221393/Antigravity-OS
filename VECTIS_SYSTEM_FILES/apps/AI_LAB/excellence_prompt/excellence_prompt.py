"""
EGO Excellence Prompt - 優秀さの言語化ツール
================================================
「人にとっての優秀さとは何か？」を深く内省し、言語化するためのプロンプトアプリ。
Socratic Method（ソクラテス式問答法）を用いて、自己理解を深める。
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from datetime import datetime

# ===== 設計哲学 =====
# このアプリは「答えを与える」のではなく「問いを与える」
# ユーザー自身が思考し、言葉にすることで、自己理解を深める

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "excellence_journal.json")

# ===== Socratic Prompts =====
PROMPT_STAGES = [
    {
        "title": "Stage 1: 直感",
        "question": "「優秀な人」と聞いて、最初に頭に浮かぶ人物は誰ですか？\n（実在でも架空でも可）",
        "hint": "理由は後で考えます。まず直感で答えてください。"
    },
    {
        "title": "Stage 2: 分解",
        "question": "その人物の「優秀さ」は、具体的にどのような行動・特性に現れていますか？\n3つ挙げてください。",
        "hint": "例: 「困難な状況でも冷静に判断できる」「他者の話を深く聴ける」など"
    },
    {
        "title": "Stage 3: 抽象化",
        "question": "先ほど挙げた3つの特性に共通する「核」は何だと思いますか？\n一言で表現してみてください。",
        "hint": "例: 「自己規律」「好奇心」「誠実さ」「胆力」など"
    },
    {
        "title": "Stage 4: 対比",
        "question": "逆に、「優秀ではない」と感じる人の特徴は何ですか？\nなぜそう感じるのでしょうか？",
        "hint": "批判ではなく、自分の価値観を炙り出すための問いです。"
    },
    {
        "title": "Stage 5: 自己投影",
        "question": "あなた自身は、Stage 3で挙げた「核」をどの程度持っていると思いますか？\n（0-10で評価し、理由を書いてください）",
        "hint": "正直に。自己認識の解像度を上げるための問いです。"
    },
    {
        "title": "Stage 6: 行動定義",
        "question": "もし明日から「優秀さ」を1%向上させるなら、\n具体的に何をしますか？（行動レベルで）",
        "hint": "「頑張る」ではなく「毎朝5分の読書」のように、具体的に。"
    },
    {
        "title": "Stage 7: 言語化",
        "question": "ここまでの思考を踏まえて、\n「あなたにとっての優秀さ」を一文で定義してください。",
        "hint": "これがあなたの「優秀さの定義 ver.1」です。今後も更新していきましょう。"
    }
]


class ExcellencePromptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EGO Excellence Prompt - 優秀さの言語化")
        self.root.geometry("800x700")
        self.root.configure(bg="#1a1a2e")
        
        self.current_stage = 0
        self.answers = {}
        
        self.setup_styles()
        self.create_widgets()
        self.load_previous_session()
        self.show_stage(0)
    
    def setup_styles(self):
        """ダークテーマのスタイル設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # カラーパレット
        self.colors = {
            'bg': '#1a1a2e',
            'surface': '#16213e',
            'primary': '#0f3460',
            'accent': '#e94560',
            'text': '#eaeaea',
            'dim': '#7a7a8a'
        }
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=self.colors['accent'])
        style.configure('Question.TLabel', font=('Segoe UI', 12), foreground=self.colors['text'], wraplength=700)
        style.configure('Hint.TLabel', font=('Segoe UI', 10, 'italic'), foreground=self.colors['dim'])
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'))
    
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ヘッダー
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🔮 優秀さの言語化", style='Title.TLabel').pack(side=tk.LEFT)
        
        self.stage_label = ttk.Label(header_frame, text="Stage 1 / 7", style='Hint.TLabel')
        self.stage_label.pack(side=tk.RIGHT)
        
        # プログレスバー
        self.progress = ttk.Progressbar(main_frame, length=700, mode='determinate', maximum=7)
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # 質問エリア
        self.question_frame = ttk.Frame(main_frame)
        self.question_frame.pack(fill=tk.X, pady=10)
        
        self.question_title = ttk.Label(self.question_frame, text="", style='Title.TLabel')
        self.question_title.pack(anchor=tk.W)
        
        self.question_text = ttk.Label(self.question_frame, text="", style='Question.TLabel')
        self.question_text.pack(anchor=tk.W, pady=10)
        
        self.hint_text = ttk.Label(self.question_frame, text="", style='Hint.TLabel')
        self.hint_text.pack(anchor=tk.W)
        
        # 回答エリア
        answer_frame = ttk.Frame(main_frame)
        answer_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.answer_text = scrolledtext.ScrolledText(
            answer_frame,
            font=('Segoe UI', 11),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        self.answer_text.pack(fill=tk.BOTH, expand=True)
        
        # ナビゲーションボタン
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        self.prev_btn = ttk.Button(nav_frame, text="← 前へ", command=self.prev_stage)
        self.prev_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(nav_frame, text="次へ →", command=self.next_stage, style='Accent.TButton')
        self.next_btn.pack(side=tk.RIGHT)
        
        self.save_btn = ttk.Button(nav_frame, text="💾 保存して終了", command=self.save_and_exit)
        self.save_btn.pack(side=tk.RIGHT, padx=10)
        
        # 結果表示ボタン（最終ステージで表示）
        self.result_btn = ttk.Button(nav_frame, text="📊 結果を見る", command=self.show_summary)
        self.result_btn.pack(side=tk.RIGHT, padx=10)
        self.result_btn.pack_forget()  # 最初は非表示
    
    def show_stage(self, stage_idx):
        """ステージを表示"""
        if 0 <= stage_idx < len(PROMPT_STAGES):
            self.save_current_answer()
            self.current_stage = stage_idx
            stage = PROMPT_STAGES[stage_idx]
            
            self.question_title.config(text=stage['title'])
            self.question_text.config(text=stage['question'])
            self.hint_text.config(text=f"💡 {stage['hint']}")
            self.stage_label.config(text=f"Stage {stage_idx + 1} / {len(PROMPT_STAGES)}")
            self.progress['value'] = stage_idx + 1
            
            # 以前の回答を復元
            prev_answer = self.answers.get(str(stage_idx), "")
            self.answer_text.delete('1.0', tk.END)
            self.answer_text.insert('1.0', prev_answer)
            
            # ボタンの有効/無効
            self.prev_btn['state'] = 'normal' if stage_idx > 0 else 'disabled'
            
            # 最終ステージで結果ボタンを表示
            if stage_idx == len(PROMPT_STAGES) - 1:
                self.next_btn.config(text="✓ 完了")
                self.result_btn.pack(side=tk.RIGHT, padx=10)
            else:
                self.next_btn.config(text="次へ →")
                self.result_btn.pack_forget()
    
    def save_current_answer(self):
        """現在の回答を保存"""
        answer = self.answer_text.get('1.0', tk.END).strip()
        if answer:
            self.answers[str(self.current_stage)] = answer
    
    def next_stage(self):
        self.save_current_answer()
        if self.current_stage < len(PROMPT_STAGES) - 1:
            self.show_stage(self.current_stage + 1)
        else:
            self.show_summary()
    
    def prev_stage(self):
        self.save_current_answer()
        if self.current_stage > 0:
            self.show_stage(self.current_stage - 1)
    
    def show_summary(self):
        """思考の旅のサマリーを表示"""
        self.save_current_answer()
        
        summary_window = tk.Toplevel(self.root)
        summary_window.title("あなたの「優秀さ」の定義")
        summary_window.geometry("700x600")
        summary_window.configure(bg=self.colors['bg'])
        
        # サマリーテキスト
        summary_text = scrolledtext.ScrolledText(
            summary_window,
            font=('Segoe UI', 11),
            bg=self.colors['surface'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        summary_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # サマリーを構築
        summary = f"# 優秀さの言語化 - {datetime.now().strftime('%Y/%m/%d %H:%M')}\n\n"
        
        for i, stage in enumerate(PROMPT_STAGES):
            answer = self.answers.get(str(i), "(未回答)")
            summary += f"## {stage['title']}\n"
            summary += f"**Q:** {stage['question']}\n\n"
            summary += f"**A:** {answer}\n\n"
            summary += "-" * 50 + "\n\n"
        
        # 最終定義を強調
        final_definition = self.answers.get(str(len(PROMPT_STAGES) - 1), "")
        if final_definition:
            summary += "=" * 50 + "\n"
            summary += "## 🎯 あなたの「優秀さ」の定義\n\n"
            summary += f"**{final_definition}**\n\n"
            summary += "=" * 50 + "\n"
        
        summary_text.insert('1.0', summary)
        summary_text.config(state='disabled')
        
        # 保存ボタン
        ttk.Button(
            summary_window,
            text="📄 この定義を保存する",
            command=lambda: self.save_definition(summary)
        ).pack(pady=10)
    
    def save_definition(self, summary):
        """定義をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(BASE_DIR, f"excellence_definition_{timestamp}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        messagebox.showinfo("保存完了", f"保存しました: {filename}")
    
    def save_and_exit(self):
        """セッションを保存して終了"""
        self.save_current_answer()
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'current_stage': self.current_stage,
            'answers': self.answers
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        messagebox.showinfo("保存完了", "進捗を保存しました。次回続きから再開できます。")
        self.root.destroy()
    
    def load_previous_session(self):
        """前回のセッションを読み込む"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.answers = data.get('answers', {})
                self.current_stage = data.get('current_stage', 0)
        except:
            pass


def main():
    root = tk.Tk()
    app = ExcellencePromptApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
