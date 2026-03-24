"""
EGO Text Router - テキスト振り分けアプリ
==========================================
入力テキストをカテゴリ別に自動振り分けして保存。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

THEME = {
    'bg': '#000000',
    'surface': '#001133',
    'overlay': '#001a4d',
    'text': '#e0e0e0',
    'text_dim': '#008888',
    'accent': '#00ffff',
    'success': '#00ffcc',
    'warning': '#ffaa00',
    'error': '#ff3333',
    'purple': '#cc99ff',
    'teal': '#00ffff',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "routed_items.json")

# カテゴリ定義
CATEGORIES = {
    'task': {'icon': '✅', 'name': 'タスク', 'color': THEME['success'], 'keywords': ['タスク', 'やる', 'todo', '買う', '作る', 'する']},
    'idea': {'icon': '💡', 'name': 'アイデア', 'color': THEME['warning'], 'keywords': ['アイデア', '思いついた', 'もし', '〜したら', '案']},
    'note': {'icon': '📝', 'name': 'メモ', 'color': THEME['accent'], 'keywords': ['メモ', '覚え', '記録', 'note']},
    'question': {'icon': '❓', 'name': '質問', 'color': THEME['purple'], 'keywords': ['なぜ', 'どうして', 'what', 'why', 'how', '?', '？']},
    'schedule': {'icon': '📅', 'name': '予定', 'color': THEME['teal'], 'keywords': ['予定', '〜日', '〜時', 'meeting', '会議', '面接']},
    'shukatsu': {'icon': '💼', 'name': '就活', 'color': THEME['success'], 'keywords': ['就活', 'ES', 'インターン', '企業', '面接']},
    'learning': {'icon': '📚', 'name': '学習', 'color': THEME['accent'], 'keywords': ['勉強', '学習', '読む', '本', 'TOEIC', '資格']},
    'other': {'icon': '📋', 'name': 'その他', 'color': THEME['text_dim'], 'keywords': []}
}


class VectisTextRouterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔀 EGO Text Router")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME['bg'])
        
        self.items = []
        self.load_items()
        
        self.setup_ui()
        self.render_items()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔀 EGO Text Router",
            font=("Segoe UI", 18, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        self.stats_label = tk.Label(
            header,
            text="0 items",
            font=("Segoe UI", 10),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # メインコンテンツ
        main = tk.Frame(self.root, bg=THEME['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 入力エリア
        input_card = tk.Frame(main, bg=THEME['surface'], padx=20, pady=20)
        input_card.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            input_card,
            text="💬 テキストを入力（自動でカテゴリ分類されます）",
            font=("Segoe UI", 12, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        input_frame = tk.Frame(input_card, bg=THEME['surface'])
        input_frame.pack(fill=tk.X)
        
        self.input_text = tk.Text(
            input_frame,
            font=("Segoe UI", 11),
            bg=THEME['overlay'],
            fg=THEME['text'],
            relief=tk.FLAT,
            height=3,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_text.bind('<Control-Return>', lambda e: self.route_text())
        
        btn_frame = tk.Frame(input_frame, bg=THEME['surface'])
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(
            btn_frame,
            text="📤\n送信",
            font=("Segoe UI", 11, "bold"),
            bg=THEME['accent'],
            fg=THEME['bg'],
            relief=tk.FLAT,
            width=6,
            height=2,
            command=self.route_text,
            cursor="hand2"
        ).pack()
        
        # カテゴリ表示
        cat_frame = tk.Frame(input_card, bg=THEME['surface'])
        cat_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(cat_frame, text="カテゴリ:", fg=THEME['text_dim'], bg=THEME['surface']).pack(side=tk.LEFT)
        
        for key, cat in CATEGORIES.items():
            lbl = tk.Label(
                cat_frame,
                text=f"{cat['icon']} {cat['name']}",
                font=("Segoe UI", 9),
                fg=cat['color'],
                bg=THEME['surface']
            )
            lbl.pack(side=tk.LEFT, padx=8)
        
        # アイテムリスト（カテゴリ別タブ）
        notebook = ttk.Notebook(main)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.category_frames = {}
        self.category_listboxes = {}
        
        # 全て + 各カテゴリのタブ
        for key in ['all'] + list(CATEGORIES.keys()):
            frame = tk.Frame(notebook, bg=THEME['surface'])
            notebook.add(frame, text=f"{'📋 すべて' if key == 'all' else CATEGORIES[key]['icon'] + ' ' + CATEGORIES[key]['name']}")
            
            listbox = tk.Listbox(
                frame,
                font=("Segoe UI", 10),
                bg=THEME['overlay'],
                fg=THEME['text'],
                selectbackground=THEME['accent'],
                relief=tk.FLAT,
                activestyle='none'
            )
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            listbox.bind('<Double-Button-1>', lambda e, k=key: self.delete_selected(k))
            
            self.category_frames[key] = frame
            self.category_listboxes[key] = listbox
        
        # ステータスバー
        status = tk.Frame(self.root, bg=THEME['surface'], height=25)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        self.status_label = tk.Label(
            status,
            text="Ctrl+Enterで送信 | ダブルクリックで削除",
            font=("Segoe UI", 9),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def load_items(self):
        """アイテム読み込み"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
        except:
            self.items = []
    
    def save_items(self):
        """アイテム保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save error: {e}")
    
    def detect_category(self, text):
        """テキストからカテゴリを自動検出"""
        text_lower = text.lower()
        
        for key, cat in CATEGORIES.items():
            if key == 'other':
                continue
            for keyword in cat['keywords']:
                if keyword.lower() in text_lower:
                    return key
        
        return 'other'
    
    def route_text(self):
        """テキストを振り分け"""
        text = self.input_text.get("1.0", tk.END).strip()
        
        if not text:
            return
        
        category = self.detect_category(text)
        cat_info = CATEGORIES[category]
        
        item = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': text,
            'category': category,
            'created_at': datetime.now().isoformat()
        }
        
        self.items.insert(0, item)
        self.input_text.delete("1.0", tk.END)
        
        self.save_items()
        self.render_items()
        
        self.status_label.config(
            text=f"✓ {cat_info['icon']} {cat_info['name']}に振り分けました",
            fg=cat_info['color']
        )
        self.root.after(3000, lambda: self.status_label.config(text="Ctrl+Enterで送信 | ダブルクリックで削除", fg=THEME['text_dim']))
    
    def delete_selected(self, category_key):
        """選択アイテム削除"""
        listbox = self.category_listboxes[category_key]
        selection = listbox.curselection()
        
        if not selection:
            return
        
        if not messagebox.askyesno("確認", "選択したアイテムを削除しますか？"):
            return
        
        # カテゴリでフィルターしたリストから削除
        if category_key == 'all':
            filtered = self.items
        else:
            filtered = [i for i in self.items if i.get('category') == category_key]
        
        idx = selection[0]
        if idx < len(filtered):
            item_to_delete = filtered[idx]
            self.items = [i for i in self.items if i['id'] != item_to_delete['id']]
            self.save_items()
            self.render_items()
    
    def render_items(self):
        """アイテムリスト描画"""
        # すべてのリストボックスをクリア
        for listbox in self.category_listboxes.values():
            listbox.delete(0, tk.END)
        
        # アイテムを振り分け
        for item in self.items:
            category = item.get('category', 'other')
            cat_info = CATEGORIES.get(category, CATEGORIES['other'])
            text = item.get('text', '')[:60]
            display = f"{cat_info['icon']} {text}"
            
            # すべてタブ
            self.category_listboxes['all'].insert(tk.END, display)
            
            # カテゴリタブ
            if category in self.category_listboxes:
                self.category_listboxes[category].insert(tk.END, display)
        
        self.stats_label.config(text=f"{len(self.items)} items")


def main():
    root = tk.Tk()
    app = VectisTextRouterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
