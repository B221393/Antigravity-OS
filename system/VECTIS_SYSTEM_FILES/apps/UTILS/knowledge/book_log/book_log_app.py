"""
VECTIS Book Log - 読書記録アプリ
================================
読書記録をネイティブGUIで管理。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

THEME = {
    'bg': '#1e1e2e',
    'surface': '#313244',
    'overlay': '#45475a',
    'text': '#cdd6f4',
    'text_dim': '#6c7086',
    'accent': '#89b4fa',
    'success': '#a6e3a1',
    'warning': '#f9e2af',
    'error': '#f38ba8',
    'purple': '#cba6f7',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "books.json")


class VectisBookLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 VECTIS Book Log")
        self.root.geometry("1000x700")
        self.root.configure(bg=THEME['bg'])
        
        self.books = []
        self.load_books()
        
        self.setup_ui()
        self.render_books()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📚 VECTIS Book Log",
            font=("Segoe UI", 18, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        self.stats_label = tk.Label(
            header,
            text="0冊",
            font=("Segoe UI", 12),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # メインコンテンツ
        main = tk.Frame(self.root, bg=THEME['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左パネル：入力フォーム
        left = tk.Frame(main, bg=THEME['surface'], width=350, padx=20, pady=20)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)
        
        tk.Label(
            left,
            text="📖 本を追加",
            font=("Segoe UI", 14, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(anchor='w', pady=(0, 20))
        
        # タイトル
        tk.Label(left, text="タイトル", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.title_entry = tk.Entry(left, font=("Segoe UI", 11), bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.title_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        # 著者
        tk.Label(left, text="著者", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.author_entry = tk.Entry(left, font=("Segoe UI", 11), bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.author_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        # ステータス
        tk.Label(left, text="ステータス", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.status_var = tk.StringVar(value="reading")
        status_frame = tk.Frame(left, bg=THEME['surface'])
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        for text, value in [("読書中", "reading"), ("完読", "completed"), ("積読", "wishlist")]:
            rb = tk.Radiobutton(
                status_frame,
                text=text,
                variable=self.status_var,
                value=value,
                bg=THEME['surface'],
                fg=THEME['text'],
                selectcolor=THEME['overlay']
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # 評価
        tk.Label(left, text="評価 (1-5)", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.rating_var = tk.IntVar(value=3)
        rating_frame = tk.Frame(left, bg=THEME['surface'])
        rating_frame.pack(fill=tk.X, pady=(0, 15))
        
        for i in range(1, 6):
            rb = tk.Radiobutton(
                rating_frame,
                text="⭐" * i,
                variable=self.rating_var,
                value=i,
                bg=THEME['surface'],
                fg=THEME['warning'],
                selectcolor=THEME['overlay']
            )
            rb.pack(side=tk.LEFT)
        
        # メモ
        tk.Label(left, text="メモ", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.notes_text = tk.Text(
            left,
            font=("Segoe UI", 10),
            bg=THEME['overlay'],
            fg=THEME['text'],
            relief=tk.FLAT,
            height=5,
            wrap=tk.WORD
        )
        self.notes_text.pack(fill=tk.X, pady=(0, 20))
        
        # 追加ボタン
        add_btn = tk.Button(
            left,
            text="➕ 本を追加",
            font=("Segoe UI", 12, "bold"),
            bg=THEME['accent'],
            fg=THEME['bg'],
            relief=tk.FLAT,
            command=self.add_book,
            cursor="hand2"
        )
        add_btn.pack(fill=tk.X, ipady=10)
        
        # 右パネル：本リスト
        right = tk.Frame(main, bg=THEME['bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # フィルター
        filter_frame = tk.Frame(right, bg=THEME['bg'])
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        for text, value in [("すべて", "all"), ("読書中", "reading"), ("完読", "completed"), ("積読", "wishlist")]:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                bg=THEME['bg'],
                fg=THEME['text'],
                selectcolor=THEME['surface'],
                command=self.render_books
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # 本リスト
        list_container = tk.Frame(right, bg=THEME['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(list_container, bg=THEME['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.book_frame = tk.Frame(self.canvas, bg=THEME['surface'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.book_frame, anchor='nw')
        self.book_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
    
    def load_books(self):
        """本読み込み"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
        except:
            self.books = []
    
    def save_books(self):
        """本保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save error: {e}")
    
    def add_book(self):
        """本追加"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        
        if not title:
            messagebox.showwarning("入力エラー", "タイトルを入力してください")
            return
        
        book = {
            'id': int(datetime.now().timestamp() * 1000),
            'title': title,
            'author': author,
            'status': self.status_var.get(),
            'rating': self.rating_var.get(),
            'notes': self.notes_text.get("1.0", tk.END).strip(),
            'created_at': datetime.now().isoformat()
        }
        
        self.books.insert(0, book)
        
        # フォームクリア
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
        self.save_books()
        self.render_books()
    
    def delete_book(self, book_id):
        """本削除"""
        if messagebox.askyesno("確認", "この本を削除しますか？"):
            self.books = [b for b in self.books if b['id'] != book_id]
            self.save_books()
            self.render_books()
    
    def update_status(self, book_id, new_status):
        """ステータス更新"""
        for book in self.books:
            if book['id'] == book_id:
                book['status'] = new_status
                break
        self.save_books()
        self.render_books()
    
    def render_books(self):
        """本リスト描画"""
        for widget in self.book_frame.winfo_children():
            widget.destroy()
        
        # フィルター
        filter_val = self.filter_var.get()
        filtered = self.books
        if filter_val != "all":
            filtered = [b for b in self.books if b.get('status') == filter_val]
        
        # 統計更新
        reading = len([b for b in self.books if b.get('status') == 'reading'])
        completed = len([b for b in self.books if b.get('status') == 'completed'])
        wishlist = len([b for b in self.books if b.get('status') == 'wishlist'])
        self.stats_label.config(text=f"読書中: {reading} | 完読: {completed} | 積読: {wishlist}")
        
        status_colors = {
            'reading': THEME['accent'],
            'completed': THEME['success'],
            'wishlist': THEME['warning']
        }
        
        status_labels = {
            'reading': '📖 読書中',
            'completed': '✓ 完読',
            'wishlist': '📚 積読'
        }
        
        for book in filtered:
            item = tk.Frame(self.book_frame, bg=THEME['overlay'], padx=15, pady=12)
            item.pack(fill=tk.X, pady=3, padx=5)
            
            # ステータスインジケータ
            status = book.get('status', 'reading')
            indicator = tk.Frame(item, bg=status_colors.get(status, THEME['text']), width=4, height=50)
            indicator.pack(side=tk.LEFT, padx=(0, 15))
            
            # 本情報
            info = tk.Frame(item, bg=THEME['overlay'])
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(
                info,
                text=book.get('title', 'Untitled'),
                font=("Segoe UI", 12, "bold"),
                fg=THEME['text'],
                bg=THEME['overlay'],
                anchor='w'
            ).pack(anchor='w')
            
            author = book.get('author', '')
            if author:
                tk.Label(
                    info,
                    text=f"著者: {author}",
                    font=("Segoe UI", 10),
                    fg=THEME['text_dim'],
                    bg=THEME['overlay'],
                    anchor='w'
                ).pack(anchor='w')
            
            meta_frame = tk.Frame(info, bg=THEME['overlay'])
            meta_frame.pack(anchor='w')
            
            tk.Label(
                meta_frame,
                text=status_labels.get(status, status),
                font=("Segoe UI", 9),
                fg=status_colors.get(status, THEME['text']),
                bg=THEME['overlay']
            ).pack(side=tk.LEFT)
            
            rating = book.get('rating', 0)
            tk.Label(
                meta_frame,
                text=f" | {'⭐' * rating}",
                font=("Segoe UI", 9),
                fg=THEME['warning'],
                bg=THEME['overlay']
            ).pack(side=tk.LEFT)
            
            # 削除ボタン
            del_btn = tk.Button(
                item,
                text="✕",
                font=("Segoe UI", 12),
                bg=THEME['overlay'],
                fg=THEME['text_dim'],
                relief=tk.FLAT,
                command=lambda bid=book['id']: self.delete_book(bid),
                cursor="hand2"
            )
            del_btn.pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = VectisBookLogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
