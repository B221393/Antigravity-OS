"""
VECTIS Data Hub - 統合データダッシュボード
===========================================
全VECTISアプリのデータを一元管理・表示するネイティブダッシュボード。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
import glob

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
VECTIS_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../.."))

# データソース定義
DATA_SOURCES = {
    'universe': os.path.join(VECTIS_ROOT, "apps/MEDIA/youtube_channel/data/universe.json"),
    'shukatsu': os.path.join(VECTIS_ROOT, "apps/MEDIA/youtube_channel/data/shukatsu"),
    'deep_knowledge': os.path.join(VECTIS_ROOT, "apps/MEDIA/youtube_channel/data/deep_knowledge.json"),
    'todo': os.path.join(VECTIS_ROOT, "apps/UTILS/todo/tasks.json"),
    'scheduler': os.path.join(VECTIS_ROOT, "apps/UTILS/scheduler/schedules.json"),
    'task_inbox': os.path.join(VECTIS_ROOT, "data/task_inbox.json"),
}


class VectisDataHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 VECTIS Data Hub")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME['bg'])
        
        self.data = {}
        self.setup_ui()
        self.load_all_data()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """UI構築"""
        # ヘッダー
        header = tk.Frame(self.root, bg=THEME['surface'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 VECTIS Data Hub",
            font=("Segoe UI", 20, "bold"),
            fg=THEME['accent'],
            bg=THEME['surface']
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # コントロールボタン
        btn_frame = tk.Frame(header, bg=THEME['surface'])
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        self.create_button(btn_frame, "🔄 同期", self.load_all_data).pack(side=tk.LEFT, padx=5)
        self.create_button(btn_frame, "📥 エクスポート", self.export_all).pack(side=tk.LEFT, padx=5)
        
        self.sync_label = tk.Label(
            btn_frame,
            text="最終同期: -",
            font=("Segoe UI", 9),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        self.sync_label.pack(side=tk.LEFT, padx=20)
        
        # メインコンテンツ
        main = tk.Frame(self.root, bg=THEME['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 統計カード
        stats_frame = tk.Frame(main, bg=THEME['bg'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stat_cards = {}
        stats_config = [
            ('total', '総データ', THEME['accent']),
            ('universe', 'Universe', THEME['purple']),
            ('knowledge', 'Deep Knowledge', THEME['teal']),
            ('shukatsu', '就活情報', THEME['success']),
            ('tasks', 'タスク', THEME['warning']),
        ]
        
        for key, label, color in stats_config:
            card = self.create_stat_card(stats_frame, label, color)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.stat_cards[key] = card
        
        # データセクション（グリッド）
        sections_frame = tk.Frame(main, bg=THEME['bg'])
        sections_frame.pack(fill=tk.BOTH, expand=True)
        
        # 2x2グリッド
        sections_frame.grid_rowconfigure(0, weight=1)
        sections_frame.grid_rowconfigure(1, weight=1)
        sections_frame.grid_columnconfigure(0, weight=1)
        sections_frame.grid_columnconfigure(1, weight=1)
        
        # Universe
        self.universe_section = self.create_data_section(sections_frame, "🌐 Universe", THEME['purple'])
        self.universe_section.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Deep Knowledge
        self.knowledge_section = self.create_data_section(sections_frame, "📚 Deep Knowledge", THEME['teal'])
        self.knowledge_section.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Shukatsu
        self.shukatsu_section = self.create_data_section(sections_frame, "💼 就活情報", THEME['success'])
        self.shukatsu_section.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Tasks
        self.tasks_section = self.create_data_section(sections_frame, "✅ タスク/スケジュール", THEME['warning'])
        self.tasks_section.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        
        # ログエリア
        log_frame = tk.Frame(self.root, bg=THEME['surface'], height=100)
        log_frame.pack(fill=tk.X, side=tk.BOTTOM)
        log_frame.pack_propagate(False)
        
        tk.Label(
            log_frame,
            text="📝 Sync Log",
            font=("Segoe UI", 10, "bold"),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        ).pack(anchor='w', padx=10, pady=5)
        
        self.log_text = tk.Text(
            log_frame,
            font=("Consolas", 9),
            bg='#0a0a0a',
            fg=THEME['success'],
            height=4,
            relief=tk.FLAT
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def create_button(self, parent, text, command):
        """ボタン作成"""
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10),
            bg=THEME['overlay'],
            fg=THEME['text'],
            activebackground=THEME['accent'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=command,
            cursor="hand2"
        )
    
    def create_stat_card(self, parent, label, color):
        """統計カード作成"""
        card = tk.Frame(parent, bg=THEME['surface'], padx=20, pady=15)
        
        value_label = tk.Label(
            card,
            text="0",
            font=("Segoe UI", 28, "bold"),
            fg=color,
            bg=THEME['surface']
        )
        value_label.pack()
        
        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 10),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        ).pack()
        
        card.value_label = value_label
        return card
    
    def create_data_section(self, parent, title, color):
        """データセクション作成"""
        section = tk.Frame(parent, bg=THEME['surface'])
        
        # ヘッダー
        header = tk.Frame(section, bg=THEME['surface'])
        header.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 12, "bold"),
            fg=color,
            bg=THEME['surface']
        ).pack(side=tk.LEFT)
        
        count_label = tk.Label(
            header,
            text="0件",
            font=("Segoe UI", 10),
            fg=THEME['text_dim'],
            bg=THEME['surface']
        )
        count_label.pack(side=tk.RIGHT)
        section.count_label = count_label
        
        # リスト
        list_frame = tk.Frame(section, bg=THEME['surface'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            bg=THEME['overlay'],
            fg=THEME['text'],
            selectbackground=THEME['accent'],
            relief=tk.FLAT,
            height=8
        )
        listbox.pack(fill=tk.BOTH, expand=True)
        section.listbox = listbox
        
        return section
    
    def log(self, message, level='info'):
        """ログ出力"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {'info': THEME['text'], 'success': THEME['success'], 'error': THEME['error']}
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def load_all_data(self):
        """全データ読み込み"""
        self.log("データ同期開始...")
        
        total = 0
        
        # Universe
        universe_count = 0
        try:
            if os.path.exists(DATA_SOURCES['universe']):
                with open(DATA_SOURCES['universe'], 'r', encoding='utf-8') as f:
                    universe = json.load(f)
                    nodes = universe.get('nodes', [])
                    universe_count = len(nodes)
                    
                    self.universe_section.listbox.delete(0, tk.END)
                    for node in nodes[-20:]:  # 最新20件
                        title = node.get('title', 'Untitled')[:50]
                        self.universe_section.listbox.insert(0, f"• {title}")
        except Exception as e:
            self.log(f"Universe読込エラー: {e}", 'error')
        
        self.universe_section.count_label.config(text=f"{universe_count}件")
        self.stat_cards['universe'].value_label.config(text=str(universe_count))
        total += universe_count
        
        # Deep Knowledge
        knowledge_count = 0
        try:
            if os.path.exists(DATA_SOURCES['deep_knowledge']):
                with open(DATA_SOURCES['deep_knowledge'], 'r', encoding='utf-8') as f:
                    knowledge = json.load(f)
                    articles = knowledge.get('articles', [])
                    knowledge_count = len(articles)
                    
                    self.knowledge_section.listbox.delete(0, tk.END)
                    for article in articles[-20:]:
                        title = article.get('title', 'Untitled')[:50]
                        self.knowledge_section.listbox.insert(0, f"📖 {title}")
        except Exception as e:
            self.log(f"Deep Knowledge読込エラー: {e}", 'error')
        
        self.knowledge_section.count_label.config(text=f"{knowledge_count}件")
        self.stat_cards['knowledge'].value_label.config(text=str(knowledge_count))
        total += knowledge_count
        
        # Shukatsu
        shukatsu_count = 0
        try:
            shukatsu_dir = DATA_SOURCES['shukatsu']
            if os.path.exists(shukatsu_dir):
                files = glob.glob(os.path.join(shukatsu_dir, "SHUKATSU_*.json"))
                shukatsu_count = len(files)
                
                self.shukatsu_section.listbox.delete(0, tk.END)
                for f in sorted(files, reverse=True)[:20]:
                    try:
                        with open(f, 'r', encoding='utf-8') as jf:
                            item = json.load(jf)
                            title = item.get('title', 'Untitled')[:50]
                            self.shukatsu_section.listbox.insert(tk.END, f"💼 {title}")
                    except:
                        pass
        except Exception as e:
            self.log(f"就活情報読込エラー: {e}", 'error')
        
        self.shukatsu_section.count_label.config(text=f"{shukatsu_count}件")
        self.stat_cards['shukatsu'].value_label.config(text=str(shukatsu_count))
        total += shukatsu_count
        
        # Tasks
        tasks_count = 0
        try:
            self.tasks_section.listbox.delete(0, tk.END)
            
            # TODO
            if os.path.exists(DATA_SOURCES['todo']):
                with open(DATA_SOURCES['todo'], 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                    for task in todos[:10]:
                        status = "✓" if task.get('done') else "○"
                        self.tasks_section.listbox.insert(tk.END, f"{status} {task.get('text', '')[:40]}")
                    tasks_count += len(todos)
            
            # Scheduler
            if os.path.exists(DATA_SOURCES['scheduler']):
                with open(DATA_SOURCES['scheduler'], 'r', encoding='utf-8') as f:
                    schedules = json.load(f)
                    for task in schedules[:10]:
                        self.tasks_section.listbox.insert(tk.END, f"📅 {task.get('text', '')[:40]}")
                    tasks_count += len(schedules)
        except Exception as e:
            self.log(f"タスク読込エラー: {e}", 'error')
        
        self.tasks_section.count_label.config(text=f"{tasks_count}件")
        self.stat_cards['tasks'].value_label.config(text=str(tasks_count))
        total += tasks_count
        
        # 総計
        self.stat_cards['total'].value_label.config(text=str(total))
        
        # 同期時刻更新
        now = datetime.now().strftime("%H:%M:%S")
        self.sync_label.config(text=f"最終同期: {now}")
        self.log(f"同期完了 - 総データ: {total}件", 'success')
    
    def export_all(self):
        """全データエクスポート"""
        filepath = filedialog.asksaveasfilename(
            title="エクスポート",
            defaultextension=".json",
            initialfile=f"vectis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if not filepath:
            return
        
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0',
                'sources': {}
            }
            
            for key, path in DATA_SOURCES.items():
                if os.path.exists(path):
                    if os.path.isfile(path):
                        with open(path, 'r', encoding='utf-8') as f:
                            export_data['sources'][key] = json.load(f)
                    elif os.path.isdir(path):
                        files = glob.glob(os.path.join(path, "*.json"))
                        export_data['sources'][key] = []
                        for f in files[:100]:
                            try:
                                with open(f, 'r', encoding='utf-8') as jf:
                                    export_data['sources'][key].append(json.load(jf))
                            except:
                                pass
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("エクスポート完了", f"データを保存しました:\n{filepath}")
            self.log(f"エクスポート完了: {filepath}", 'success')
        
        except Exception as e:
            messagebox.showerror("エラー", f"エクスポートに失敗しました:\n{e}")
            self.log(f"エクスポートエラー: {e}", 'error')
    
    def start_auto_refresh(self):
        """自動更新開始（30秒ごと）"""
        self.load_all_data()
        self.root.after(30000, self.start_auto_refresh)


def main():
    root = tk.Tk()
    app = VectisDataHubApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
