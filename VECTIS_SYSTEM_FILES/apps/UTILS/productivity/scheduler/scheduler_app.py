"""
VECTIS Scheduler - ネイティブスケジュール管理
==============================================
音声入力対応のタスクスケジューラー。HTMLから移植。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta

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
DATA_FILE = os.path.join(BASE_DIR, "schedules.json")


class VectisSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 VECTIS Scheduler")
        self.root.geometry("900x700")
        self.root.configure(bg=THEME['bg'])
        
        self.tasks = []
        self.load_tasks()
        
        self.setup_ui()
        self.update_clock()
        self.render_tasks()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # 時計
        self.clock_label = tk.Label(
            header,
            text="00:00",
            font=("Segoe UI", 36, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        )
        self.clock_label.pack(side=tk.LEFT, padx=30, pady=10)
        
        # ステータス
        status_frame = tk.Frame(header, bg=THEME['surface'])
        status_frame.pack(side=tk.RIGHT, padx=30)
        
        tk.Label(
            status_frame,
            text="⚡ VECTIS ONLINE",
            font=("Segoe UI", 10),
            fg=THEME['success'],
            bg=THEME['surface']
        ).pack()
        
        self.date_label = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 10),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.date_label.pack()
        
        # メインコンテンツ
        main = tk.Frame(self.root, bg=THEME['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左カラム：統計 + 入力
        left_col = tk.Frame(main, bg=THEME['bg'], width=300)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_col.pack_propagate(False)
        
        # 統計カード
        stats_card = tk.Frame(left_col, bg=THEME['surface'], padx=20, pady=20)
        stats_card.pack(fill=tk.X, pady=(0, 20))
        
        stats_inner = tk.Frame(stats_card, bg=THEME['surface'])
        stats_inner.pack(fill=tk.X)
        
        # 残りタスク
        self.remaining_label = tk.Label(
            stats_inner,
            text="0",
            font=("Segoe UI", 32, "bold"),
            fg=THEME['warning'],
            bg=THEME['surface']
        )
        self.remaining_label.pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            stats_inner,
            text="残り",
            font=("Segoe UI", 12),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT)
        
        sep = tk.Frame(stats_inner, bg=THEME['overlay'], width=2, height=50)
        sep.pack(side=tk.LEFT, padx=20)
        
        # 完了タスク
        self.done_label = tk.Label(
            stats_inner,
            text="0",
            font=("Segoe UI", 32, "bold"),
            fg=THEME['success'],
            bg=THEME['surface']
        )
        self.done_label.pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            stats_inner,
            text="完了",
            font=("Segoe UI", 12),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT)
        
        # 入力カード
        input_card = tk.Frame(left_col, bg=THEME['surface'], padx=20, pady=20)
        input_card.pack(fill=tk.X)
        
        tk.Label(
            input_card,
            text="✏️ 新しいタスク",
            font=("Segoe UI", 12, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(anchor='w', pady=(0, 10))
        
        # タスク名入力
        self.task_entry = tk.Entry(
            input_card,
            font=("Segoe UI", 11),
            bg=THEME['overlay'],
            fg=THEME['text'],
            insertbackground=THEME['accent'],
            relief=tk.FLAT
        )
        self.task_entry.pack(fill=tk.X, ipady=8, pady=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        # 日時選択
        datetime_frame = tk.Frame(input_card, bg=THEME['surface'])
        datetime_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(datetime_frame, text="日付:", fg=THEME['text'], bg=THEME['surface']).pack(side=tk.LEFT)
        self.date_entry = tk.Entry(datetime_frame, width=12, bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(datetime_frame, text="時間:", fg=THEME['text'], bg=THEME['surface']).pack(side=tk.LEFT, padx=(10, 0))
        self.time_entry = tk.Entry(datetime_frame, width=6, bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        self.time_entry.insert(0, "09:00")
        
        # 優先度
        priority_frame = tk.Frame(input_card, bg=THEME['surface'])
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(priority_frame, text="優先度:", fg=THEME['text'], bg=THEME['surface']).pack(side=tk.LEFT)
        
        self.priority_var = tk.StringVar(value="normal")
        for text, value, color in [("低", "low", THEME['text_dim']), ("普通", "normal", THEME['warning']), ("高", "high", THEME['error'])]:
            rb = tk.Radiobutton(
                priority_frame,
                text=text,
                variable=self.priority_var,
                value=value,
                font=("Segoe UI", 10),
                bg=THEME['surface'],
                fg=color,
                selectcolor=THEME['overlay'],
                activebackground=THEME['surface']
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # 追加ボタン
        add_btn = tk.Button(
            input_card,
            text="➕ 追加",
            font=("Segoe UI", 11, "bold"),
            bg=THEME['accent'],
            fg=THEME['bg'],
            activebackground=THEME['success'],
            relief=tk.FLAT,
            command=self.add_task,
            cursor="hand2"
        )
        add_btn.pack(fill=tk.X, ipady=8)
        
        # 右カラム：タスクリスト
        right_col = tk.Frame(main, bg=THEME['bg'])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # リストヘッダー
        list_header = tk.Frame(right_col, bg=THEME['bg'])
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            list_header,
            text="🎯 今日やること",
            font=("Segoe UI", 14, "bold"),
            fg=THEME['text'],
            bg=THEME['bg']
        ).pack(side=tk.LEFT)
        
        clear_btn = tk.Button(
            list_header,
            text="🗑️",
            font=("Segoe UI", 12),
            bg=THEME['overlay'],
            fg=THEME['text_dim'],
            relief=tk.FLAT,
            command=self.clear_done,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # タスクリスト
        list_container = tk.Frame(right_col, bg=THEME['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(list_container, bg=THEME['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.task_frame = tk.Frame(self.canvas, bg=THEME['surface'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.task_frame, anchor='nw')
        self.task_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        # ステータスバー
        status_bar = tk.Frame(self.root, bg=THEME['surface'], height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            font=("Segoe UI", 9),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def update_clock(self):
        """時計更新"""
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M"))
        self.date_label.config(text=now.strftime("%Y/%m/%d (%a)"))
        self.root.after(1000, self.update_clock)
    
    def load_tasks(self):
        """タスク読み込み"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
        except:
            self.tasks = []
    
    def save_tasks(self):
        """タスク保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
            self.status_label.config(text="✓ 保存完了", fg=THEME['success'])
            self.root.after(2000, lambda: self.status_label.config(text="Ready", fg=THEME['text_dim']))
        except Exception as e:
            self.status_label.config(text=f"保存エラー: {e}", fg=THEME['error'])
    
    def add_task(self):
        """タスク追加"""
        text = self.task_entry.get().strip()
        if not text:
            return
        
        task = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': text,
            'date': self.date_entry.get(),
            'time': self.time_entry.get(),
            'priority': self.priority_var.get(),
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
        """完了タスククリア"""
        if not any(t['done'] for t in self.tasks):
            return
        if messagebox.askyesno("確認", "完了したタスクをすべて削除しますか？"):
            self.tasks = [t for t in self.tasks if not t['done']]
            self.save_tasks()
            self.render_tasks()
    
    def render_tasks(self):
        """タスクリスト描画"""
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        # ソート（未完了が上、優先度高が上）
        priority_order = {'high': 0, 'normal': 1, 'low': 2}
        sorted_tasks = sorted(self.tasks, key=lambda x: (x['done'], priority_order.get(x.get('priority', 'normal'), 1)))
        
        remaining = len([t for t in self.tasks if not t['done']])
        done = len([t for t in self.tasks if t['done']])
        
        self.remaining_label.config(text=str(remaining))
        self.done_label.config(text=str(done))
        
        for task in sorted_tasks:
            self.create_task_item(task)
    
    def create_task_item(self, task):
        """タスクアイテム作成"""
        is_done = task['done']
        priority = task.get('priority', 'normal')
        
        priority_colors = {
            'high': THEME['error'],
            'normal': THEME['warning'],
            'low': THEME['text_dim']
        }
        
        item = tk.Frame(
            self.task_frame,
            bg=THEME['overlay'] if is_done else THEME['surface'],
            padx=15,
            pady=12
        )
        item.pack(fill=tk.X, pady=2, padx=5)
        
        # 優先度インジケーター
        indicator = tk.Frame(item, bg=priority_colors[priority], width=4, height=30)
        indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # チェックボックス
        check_text = "✓" if is_done else "○"
        check_btn = tk.Button(
            item,
            text=check_text,
            font=("Segoe UI", 14),
            bg=THEME['success'] if is_done else THEME['overlay'],
            fg=THEME['bg'] if is_done else THEME['text'],
            relief=tk.FLAT,
            width=2,
            command=lambda tid=task['id']: self.toggle_task(tid),
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # タスク情報
        info_frame = tk.Frame(item, bg=item['bg'])
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        text_color = THEME['text_dim'] if is_done else THEME['text']
        text_font = ("Segoe UI", 11, "overstrike") if is_done else ("Segoe UI", 11)
        
        tk.Label(
            info_frame,
            text=task['text'],
            font=text_font,
            fg=text_color,
            bg=item['bg'],
            anchor='w'
        ).pack(anchor='w')
        
        tk.Label(
            info_frame,
            text=f"📅 {task.get('date', '')} {task.get('time', '')}",
            font=("Segoe UI", 9),
            fg=THEME['text_dim'],
            bg=item['bg'],
            anchor='w'
        ).pack(anchor='w')
        
        # 削除ボタン
        del_btn = tk.Button(
            item,
            text="✕",
            font=("Segoe UI", 12),
            bg=item['bg'],
            fg=THEME['text_dim'],
            activeforeground=THEME['error'],
            relief=tk.FLAT,
            command=lambda tid=task['id']: self.delete_task(tid),
            cursor="hand2"
        )
        del_btn.pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = VectisSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
