"""
VECTIS TODO - ネイティブタスク管理アプリ
==========================================
HTMLからTkinterへ移植。情報密度を最大化し、プロフェッショナルなUIを提供。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ===== テーマ定義 =====
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
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "tasks.json")


class VectisTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 VECTIS TODO")
        self.root.geometry("700x600")
        self.root.configure(bg=THEME['bg'])
        
        self.tasks = []
        self.load_tasks()
        
        self.setup_ui()
        self.render_tasks()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📝 VECTIS TODO",
            font=("Segoe UI", 18, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        self.status_label = tk.Label(
            header,
            text="0 Tasks",
            font=("Segoe UI", 10),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 入力エリア
        input_frame = tk.Frame(self.root, bg=THEME['bg'])
        input_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.task_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg=THEME['surface'],
            fg=THEME['text'],
            insertbackground=THEME['accent'],
            relief=tk.FLAT,
            width=50
        )
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        add_btn = tk.Button(
            input_frame,
            text="➕ ADD",
            font=("Segoe UI", 11, "bold"),
            bg=THEME['accent'],
            fg=THEME['bg'],
            activebackground=THEME['success'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.add_task,
            cursor="hand2"
        )
        add_btn.pack(side=tk.RIGHT)
        
        # フィルターボタン
        filter_frame = tk.Frame(self.root, bg=THEME['bg'])
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        
        for text, value in [("All", "all"), ("Active", "active"), ("Done", "done")]:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                font=("Segoe UI", 10),
                bg=THEME['bg'],
                fg=THEME['text'],
                selectcolor=THEME['surface'],
                activebackground=THEME['bg'],
                activeforeground=THEME['accent'],
                command=self.render_tasks,
                cursor="hand2"
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # クリアボタン
        clear_btn = tk.Button(
            filter_frame,
            text="🗑️ Clear Done",
            font=("Segoe UI", 9),
            bg=THEME['overlay'],
            fg=THEME['text'],
            activebackground=THEME['error'],
            relief=tk.FLAT,
            padx=10,
            command=self.clear_done,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # タスクリスト（スクロール対応）
        list_container = tk.Frame(self.root, bg=THEME['bg'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas + Scrollbar
        self.canvas = tk.Canvas(list_container, bg=THEME['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.task_frame = tk.Frame(self.canvas, bg=THEME['bg'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.task_frame, anchor='nw')
        
        self.task_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        # マウスホイールスクロール
        self.canvas.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(-1*(e.delta//120), 'units'))
        
        # ステータスバー
        status_bar = tk.Frame(self.root, bg=THEME['surface'], height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.time_label = tk.Label(
            status_bar,
            text="",
            font=("Segoe UI", 9),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.update_time()
    
    def update_time(self):
        """時刻更新"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)
    
    def load_tasks(self):
        """タスク読み込み"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"Load error: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """タスク保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            self.status_label.config(text=f"✓ Saved ({len(self.tasks)} Tasks)")
            self.root.after(2000, lambda: self.status_label.config(text=f"{len(self.tasks)} Tasks"))
        except Exception as e:
            print(f"Save error: {e}")
    
    def add_task(self):
        """タスク追加"""
        text = self.task_entry.get().strip()
        if not text:
            return
        
        task = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': text,
            'done': False,
            'created_at': datetime.now().isoformat()
        }
        
        self.tasks.insert(0, task)
        self.task_entry.delete(0, tk.END)
        self.save_tasks()
        self.render_tasks()
    
    def toggle_task(self, task_id):
        """タスク完了切り替え"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['done'] = not task['done']
                break
        self.save_tasks()
        self.render_tasks()
    
    def delete_task(self, task_id):
        """タスク削除"""
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()
        self.render_tasks()
    
    def clear_done(self):
        """完了タスクをクリア"""
        if not any(t['done'] for t in self.tasks):
            return
        
        if messagebox.askyesno("確認", "完了したタスクをすべて削除しますか？"):
            self.tasks = [t for t in self.tasks if not t['done']]
            self.save_tasks()
            self.render_tasks()
    
    def render_tasks(self):
        """タスクリスト描画"""
        # 既存のウィジェットをクリア
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        # フィルター適用
        filter_val = self.filter_var.get()
        filtered = self.tasks
        if filter_val == "active":
            filtered = [t for t in self.tasks if not t['done']]
        elif filter_val == "done":
            filtered = [t for t in self.tasks if t['done']]
        
        # ソート（未完了が上）
        filtered.sort(key=lambda x: (x['done'], -x['id']))
        
        # 各タスクを描画
        for task in filtered:
            self.create_task_item(task)
        
        # ステータス更新
        active_count = len([t for t in self.tasks if not t['done']])
        done_count = len([t for t in self.tasks if t['done']])
        self.status_label.config(text=f"Active: {active_count} | Done: {done_count}")
    
    def create_task_item(self, task):
        """タスクアイテムウィジェット作成"""
        is_done = task['done']
        
        item_frame = tk.Frame(
            self.task_frame,
            bg=THEME['overlay'] if is_done else THEME['surface'],
            padx=15,
            pady=12
        )
        item_frame.pack(fill=tk.X, pady=3)
        
        # チェックボックス風ボタン
        check_text = "✓" if is_done else "○"
        check_btn = tk.Button(
            item_frame,
            text=check_text,
            font=("Segoe UI", 14),
            bg=THEME['success'] if is_done else THEME['overlay'],
            fg=THEME['bg'] if is_done else THEME['text'],
            relief=tk.FLAT,
            width=2,
            command=lambda tid=task['id']: self.toggle_task(tid),
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # タスクテキスト
        text_color = THEME['text_dim'] if is_done else THEME['text']
        text_font = ("Segoe UI", 11, "overstrike") if is_done else ("Segoe UI", 11)
        
        text_label = tk.Label(
            item_frame,
            text=task['text'],
            font=text_font,
            fg=text_color,
            bg=item_frame['bg'],
            anchor='w'
        )
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 削除ボタン
        del_btn = tk.Button(
            item_frame,
            text="✕",
            font=("Segoe UI", 12),
            bg=item_frame['bg'],
            fg=THEME['text_dim'],
            activeforeground=THEME['error'],
            relief=tk.FLAT,
            command=lambda tid=task['id']: self.delete_task(tid),
            cursor="hand2"
        )
        del_btn.pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = VectisTodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
