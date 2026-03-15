"""
VECTIS Job Hunting - 就活管理アプリ
===================================
就活応募・ES提出・面接のトラッキングをネイティブGUIで管理。
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
    'teal': '#94e2d5',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "applications.json")


class VectisJobHuntingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💼 VECTIS Job Hunting")
        self.root.geometry("1100x750")
        self.root.configure(bg=THEME['bg'])
        
        self.applications = []
        self.load_data()
        
        self.setup_ui()
        self.render_applications()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="💼 VECTIS Job Hunting",
            font=("Segoe UI", 20, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # 統計
        stats_frame = tk.Frame(header, bg=THEME['surface'])
        stats_frame.pack(side=tk.RIGHT, padx=20)
        
        self.stats_labels = {}
        for key, label, color in [
            ('applied', '応募', THEME['accent']),
            ('es', 'ES通過', THEME['warning']),
            ('interview', '面接', THEME['purple']),
            ('offer', '内定', THEME['success'])
        ]:
            frame = tk.Frame(stats_frame, bg=THEME['surface'])
            frame.pack(side=tk.LEFT, padx=10)
            
            num_label = tk.Label(frame, text="0", font=("Segoe UI", 20, "bold"), fg=color, bg=THEME['surface'])
            num_label.pack()
            tk.Label(frame, text=label, font=("Segoe UI", 9), fg=THEME['text_dim'], bg=THEME['surface']).pack()
            self.stats_labels[key] = num_label
        
        # メインコンテンツ
        main = tk.Frame(self.root, bg=THEME['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左パネル：入力フォーム
        left = tk.Frame(main, bg=THEME['surface'], width=350, padx=20, pady=20)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)
        
        tk.Label(
            left,
            text="🏢 企業を追加",
            font=("Segoe UI", 14, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(anchor='w', pady=(0, 15))
        
        # 企業名
        tk.Label(left, text="企業名 *", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.company_entry = tk.Entry(left, font=("Segoe UI", 11), bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.company_entry.pack(fill=tk.X, ipady=8, pady=(0, 10))
        
        # 職種
        tk.Label(left, text="職種", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.position_entry = tk.Entry(left, font=("Segoe UI", 11), bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.position_entry.pack(fill=tk.X, ipady=8, pady=(0, 10))
        
        # ステータス
        tk.Label(left, text="ステータス", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.status_var = tk.StringVar(value="interested")
        status_frame = tk.Frame(left, bg=THEME['surface'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        statuses = [
            ("興味あり", "interested"),
            ("応募済み", "applied"),
            ("ES通過", "es_passed"),
            ("面接中", "interview"),
            ("内定", "offer"),
            ("見送り", "rejected")
        ]
        
        for i, (text, value) in enumerate(statuses):
            rb = tk.Radiobutton(
                status_frame,
                text=text,
                variable=self.status_var,
                value=value,
                bg=THEME['surface'],
                fg=THEME['text'],
                selectcolor=THEME['overlay'],
                font=("Segoe UI", 9)
            )
            rb.grid(row=i//3, column=i%3, sticky='w', padx=2)
        
        # 締切日
        tk.Label(left, text="締切日", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.deadline_entry = tk.Entry(left, font=("Segoe UI", 11), bg=THEME['overlay'], fg=THEME['text'], relief=tk.FLAT)
        self.deadline_entry.pack(fill=tk.X, ipady=8, pady=(0, 10))
        self.deadline_entry.insert(0, "YYYY-MM-DD")
        
        # 優先度
        tk.Label(left, text="優先度", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.priority_var = tk.StringVar(value="normal")
        priority_frame = tk.Frame(left, bg=THEME['surface'])
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        for text, value in [("低", "low"), ("普通", "normal"), ("高", "high")]:
            rb = tk.Radiobutton(
                priority_frame,
                text=text,
                variable=self.priority_var,
                value=value,
                bg=THEME['surface'],
                fg=THEME['text'],
                selectcolor=THEME['overlay']
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # メモ
        tk.Label(left, text="メモ", fg=THEME['text'], bg=THEME['surface']).pack(anchor='w')
        self.notes_text = tk.Text(
            left,
            font=("Segoe UI", 10),
            bg=THEME['overlay'],
            fg=THEME['text'],
            relief=tk.FLAT,
            height=4,
            wrap=tk.WORD
        )
        self.notes_text.pack(fill=tk.X, pady=(0, 15))
        
        # 追加ボタン
        add_btn = tk.Button(
            left,
            text="➕ 企業を追加",
            font=("Segoe UI", 12, "bold"),
            bg=THEME['accent'],
            fg=THEME['bg'],
            relief=tk.FLAT,
            command=self.add_application,
            cursor="hand2"
        )
        add_btn.pack(fill=tk.X, ipady=10)
        
        # 右パネル：応募リスト
        right = tk.Frame(main, bg=THEME['bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # フィルター
        filter_frame = tk.Frame(right, bg=THEME['bg'])
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_var = tk.StringVar(value="all")
        filters = [("すべて", "all"), ("興味", "interested"), ("応募済", "applied"), ("ES通過", "es_passed"), ("面接", "interview"), ("内定", "offer")]
        
        for text, value in filters:
            rb = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                bg=THEME['bg'],
                fg=THEME['text'],
                selectcolor=THEME['surface'],
                command=self.render_applications
            )
            rb.pack(side=tk.LEFT, padx=3)
        
        # リスト
        list_container = tk.Frame(right, bg=THEME['surface'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(list_container, bg=THEME['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.app_frame = tk.Frame(self.canvas, bg=THEME['surface'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.app_frame, anchor='nw')
        self.app_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
    
    def load_data(self):
        """データ読み込み"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.applications = json.load(f)
        except:
            self.applications = []
    
    def save_data(self):
        """データ保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.applications, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save error: {e}")
    
    def add_application(self):
        """応募追加"""
        company = self.company_entry.get().strip()
        
        if not company:
            messagebox.showwarning("入力エラー", "企業名を入力してください")
            return
        
        app = {
            'id': int(datetime.now().timestamp() * 1000),
            'company': company,
            'position': self.position_entry.get().strip(),
            'status': self.status_var.get(),
            'deadline': self.deadline_entry.get().strip(),
            'priority': self.priority_var.get(),
            'notes': self.notes_text.get("1.0", tk.END).strip(),
            'created_at': datetime.now().isoformat()
        }
        
        self.applications.insert(0, app)
        
        # フォームクリア
        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
        self.save_data()
        self.render_applications()
    
    def delete_application(self, app_id):
        """応募削除"""
        if messagebox.askyesno("確認", "この応募を削除しますか？"):
            self.applications = [a for a in self.applications if a['id'] != app_id]
            self.save_data()
            self.render_applications()
    
    def update_status(self, app_id, new_status):
        """ステータス更新"""
        for app in self.applications:
            if app['id'] == app_id:
                app['status'] = new_status
                break
        self.save_data()
        self.render_applications()
    
    def render_applications(self):
        """応募リスト描画"""
        for widget in self.app_frame.winfo_children():
            widget.destroy()
        
        # 統計更新
        counts = {
            'applied': len([a for a in self.applications if a.get('status') in ['applied', 'es_passed', 'interview', 'offer']]),
            'es': len([a for a in self.applications if a.get('status') in ['es_passed', 'interview', 'offer']]),
            'interview': len([a for a in self.applications if a.get('status') in ['interview', 'offer']]),
            'offer': len([a for a in self.applications if a.get('status') == 'offer'])
        }
        
        for key, label in self.stats_labels.items():
            label.config(text=str(counts.get(key, 0)))
        
        # フィルター
        filter_val = self.filter_var.get()
        filtered = self.applications
        if filter_val != "all":
            filtered = [a for a in self.applications if a.get('status') == filter_val]
        
        status_config = {
            'interested': ('🔍 興味あり', THEME['text_dim']),
            'applied': ('📝 応募済み', THEME['accent']),
            'es_passed': ('✓ ES通過', THEME['warning']),
            'interview': ('🎤 面接中', THEME['purple']),
            'offer': ('🎉 内定', THEME['success']),
            'rejected': ('✕ 見送り', THEME['error'])
        }
        
        priority_order = {'high': 0, 'normal': 1, 'low': 2}
        sorted_apps = sorted(filtered, key=lambda x: (priority_order.get(x.get('priority', 'normal'), 1), -x.get('id', 0)))
        
        for app in sorted_apps:
            status = app.get('status', 'interested')
            status_text, status_color = status_config.get(status, ('不明', THEME['text']))
            
            item = tk.Frame(self.app_frame, bg=THEME['overlay'], padx=15, pady=12)
            item.pack(fill=tk.X, pady=3, padx=5)
            
            # ステータスインジケータ
            indicator = tk.Frame(item, bg=status_color, width=4, height=50)
            indicator.pack(side=tk.LEFT, padx=(0, 15))
            
            # 情報
            info = tk.Frame(item, bg=THEME['overlay'])
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(
                info,
                text=app.get('company', 'Unknown'),
                font=("Segoe UI", 13, "bold"),
                fg=THEME['text'],
                bg=THEME['overlay']
            ).pack(anchor='w')
            
            position = app.get('position', '')
            if position:
                tk.Label(
                    info,
                    text=position,
                    font=("Segoe UI", 10),
                    fg=THEME['text_dim'],
                    bg=THEME['overlay']
                ).pack(anchor='w')
            
            meta = tk.Frame(info, bg=THEME['overlay'])
            meta.pack(anchor='w')
            
            tk.Label(meta, text=status_text, font=("Segoe UI", 9), fg=status_color, bg=THEME['overlay']).pack(side=tk.LEFT)
            
            deadline = app.get('deadline', '')
            if deadline and deadline != "YYYY-MM-DD":
                tk.Label(meta, text=f" | 📅 {deadline}", font=("Segoe UI", 9), fg=THEME['warning'], bg=THEME['overlay']).pack(side=tk.LEFT)
            
            # 削除ボタン
            del_btn = tk.Button(
                item,
                text="✕",
                font=("Segoe UI", 12),
                bg=THEME['overlay'],
                fg=THEME['text_dim'],
                relief=tk.FLAT,
                command=lambda aid=app['id']: self.delete_application(aid),
                cursor="hand2"
            )
            del_btn.pack(side=tk.RIGHT)


def main():
    root = tk.Tk()
    app = VectisJobHuntingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
