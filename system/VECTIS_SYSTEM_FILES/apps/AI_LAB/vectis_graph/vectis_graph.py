"""
EGO Graph Studio - Origin風のシンプルなグラフ作成ツール
==========================================================
gnuplotの代替として、Pythonで洗練されたグラフを作成。
無駄を排除し、直感的な操作でプロフェッショナルなグラフを生成。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import csv
import os
from datetime import datetime

# 日本語フォント設定
plt.rcParams['font.family'] = ['Meiryo', 'Yu Gothic', 'MS Gothic', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class VectisGraphStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("EGO Graph Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2e")
        
        # データ保持
        self.datasets = []  # [(label, x_data, y_data, style), ...]
        self.current_file = None
        
        # カラースキーム（Origin風 + モダン）
        self.colors = {
            'bg': '#1e1e2e',
            'surface': '#2d2d3f',
            'panel': '#3d3d5c',
            'text': '#cdd6f4',
            'accent': '#89b4fa',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'error': '#f38ba8'
        }
        
        # グラフカラーパレット
        self.plot_colors = [
            '#89b4fa', '#f38ba8', '#a6e3a1', '#f9e2af', 
            '#cba6f7', '#94e2d5', '#fab387', '#74c7ec'
        ]
        
        self.setup_ui()
        self.create_sample_data()
    
    def setup_ui(self):
        """UI構築"""
        # メインコンテナ
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左パネル（コントロール）
        self.control_panel = tk.Frame(main_container, bg=self.colors['surface'], width=280)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.control_panel.pack_propagate(False)
        
        self.setup_control_panel()
        
        # 右パネル（グラフ）
        self.graph_panel = tk.Frame(main_container, bg=self.colors['bg'])
        self.graph_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_graph_panel()
    
    def setup_control_panel(self):
        """コントロールパネル構築"""
        panel = self.control_panel
        
        # タイトル
        title_frame = tk.Frame(panel, bg=self.colors['panel'])
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text="📊 EGO Graph",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['panel'],
            pady=10
        ).pack()
        
        # --- データ入力セクション ---
        self.create_section_label(panel, "📈 データ入力")
        
        # 関数入力
        func_frame = tk.Frame(panel, bg=self.colors['surface'])
        func_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(func_frame, text="f(x) =", fg=self.colors['text'], bg=self.colors['surface']).pack(side=tk.LEFT)
        
        self.func_entry = tk.Entry(
            func_frame,
            font=('Consolas', 11),
            bg=self.colors['panel'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT
        )
        self.func_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.func_entry.insert(0, "np.sin(x)")
        
        # X範囲
        range_frame = tk.Frame(panel, bg=self.colors['surface'])
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(range_frame, text="x", fg=self.colors['text'], bg=self.colors['surface']).pack(side=tk.LEFT)
        
        self.x_min = tk.Entry(range_frame, width=8, bg=self.colors['panel'], fg=self.colors['text'], relief=tk.FLAT)
        self.x_min.pack(side=tk.LEFT, padx=5)
        self.x_min.insert(0, "-10")
        
        tk.Label(range_frame, text="→", fg=self.colors['text'], bg=self.colors['surface']).pack(side=tk.LEFT)
        
        self.x_max = tk.Entry(range_frame, width=8, bg=self.colors['panel'], fg=self.colors['text'], relief=tk.FLAT)
        self.x_max.pack(side=tk.LEFT, padx=5)
        self.x_max.insert(0, "10")
        
        # プロットボタン
        btn_frame = tk.Frame(panel, bg=self.colors['surface'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.create_button(btn_frame, "➕ 関数を追加", self.add_function).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "📂 CSV読込", self.load_csv).pack(side=tk.LEFT, padx=2)
        
        # --- グラフ設定セクション ---
        self.create_section_label(panel, "⚙️ グラフ設定")
        
        # タイトル
        title_input_frame = tk.Frame(panel, bg=self.colors['surface'])
        title_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(title_input_frame, text="Title:", fg=self.colors['text'], bg=self.colors['surface'], width=8, anchor='w').pack(side=tk.LEFT)
        self.title_entry = tk.Entry(title_input_frame, bg=self.colors['panel'], fg=self.colors['text'], relief=tk.FLAT)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.title_entry.insert(0, "EGO Graph")
        
        # X軸ラベル
        xlabel_frame = tk.Frame(panel, bg=self.colors['surface'])
        xlabel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(xlabel_frame, text="X Label:", fg=self.colors['text'], bg=self.colors['surface'], width=8, anchor='w').pack(side=tk.LEFT)
        self.xlabel_entry = tk.Entry(xlabel_frame, bg=self.colors['panel'], fg=self.colors['text'], relief=tk.FLAT)
        self.xlabel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.xlabel_entry.insert(0, "x")
        
        # Y軸ラベル
        ylabel_frame = tk.Frame(panel, bg=self.colors['surface'])
        ylabel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(ylabel_frame, text="Y Label:", fg=self.colors['text'], bg=self.colors['surface'], width=8, anchor='w').pack(side=tk.LEFT)
        self.ylabel_entry = tk.Entry(ylabel_frame, bg=self.colors['panel'], fg=self.colors['text'], relief=tk.FLAT)
        self.ylabel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ylabel_entry.insert(0, "y")
        
        # グリッド設定
        grid_frame = tk.Frame(panel, bg=self.colors['surface'])
        grid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.grid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            grid_frame,
            text="グリッド表示",
            variable=self.grid_var,
            fg=self.colors['text'],
            bg=self.colors['surface'],
            selectcolor=self.colors['panel'],
            activebackground=self.colors['surface'],
            command=self.update_graph
        ).pack(side=tk.LEFT)
        
        self.legend_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            grid_frame,
            text="凡例表示",
            variable=self.legend_var,
            fg=self.colors['text'],
            bg=self.colors['surface'],
            selectcolor=self.colors['panel'],
            activebackground=self.colors['surface'],
            command=self.update_graph
        ).pack(side=tk.LEFT)
        
        # 更新ボタン
        self.create_button(panel, "🔄 グラフ更新", self.update_graph).pack(fill=tk.X, padx=10, pady=10)
        
        # --- データセットリスト ---
        self.create_section_label(panel, "📋 データセット")
        
        self.dataset_listbox = tk.Listbox(
            panel,
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Segoe UI', 10),
            height=6,
            selectmode=tk.SINGLE,
            relief=tk.FLAT
        )
        self.dataset_listbox.pack(fill=tk.X, padx=10, pady=5)
        
        list_btn_frame = tk.Frame(panel, bg=self.colors['surface'])
        list_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_button(list_btn_frame, "🗑️ 選択削除", self.remove_dataset).pack(side=tk.LEFT, padx=2)
        self.create_button(list_btn_frame, "🧹 全削除", self.clear_all).pack(side=tk.LEFT, padx=2)
        
        # --- エクスポート ---
        self.create_section_label(panel, "💾 エクスポート")
        
        export_frame = tk.Frame(panel, bg=self.colors['surface'])
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.create_button(export_frame, "PNG保存", lambda: self.export_graph('png')).pack(side=tk.LEFT, padx=2)
        self.create_button(export_frame, "SVG保存", lambda: self.export_graph('svg')).pack(side=tk.LEFT, padx=2)
        self.create_button(export_frame, "PDF保存", lambda: self.export_graph('pdf')).pack(side=tk.LEFT, padx=2)
    
    def setup_graph_panel(self):
        """グラフパネル構築"""
        # Figure作成（ダークテーマ）
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor=self.colors['bg'])
        self.ax = self.fig.add_subplot(111)
        
        # ダークテーマ適用
        self.ax.set_facecolor(self.colors['surface'])
        self.ax.tick_params(colors=self.colors['text'])
        self.ax.spines['bottom'].set_color(self.colors['text'])
        self.ax.spines['top'].set_color(self.colors['panel'])
        self.ax.spines['left'].set_color(self.colors['text'])
        self.ax.spines['right'].set_color(self.colors['panel'])
        self.ax.xaxis.label.set_color(self.colors['text'])
        self.ax.yaxis.label.set_color(self.colors['text'])
        self.ax.title.set_color(self.colors['accent'])
        
        # キャンバス
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ツールバー（ズーム、パンなど）
        toolbar_frame = tk.Frame(self.graph_panel, bg=self.colors['bg'])
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
    
    def create_section_label(self, parent, text):
        """セクションラベル作成"""
        frame = tk.Frame(parent, bg=self.colors['surface'])
        frame.pack(fill=tk.X, padx=10, pady=(15, 5))
        
        tk.Label(
            frame,
            text=text,
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['surface']
        ).pack(anchor='w')
    
    def create_button(self, parent, text, command):
        """スタイル付きボタン作成"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 9),
            bg=self.colors['panel'],
            fg=self.colors['text'],
            activebackground=self.colors['accent'],
            activeforeground=self.colors['bg'],
            relief=tk.FLAT,
            padx=8,
            pady=4
        )
        return btn
    
    def create_sample_data(self):
        """サンプルデータを生成"""
        x = np.linspace(-10, 10, 200)
        y = np.sin(x)
        self.datasets.append(("sin(x)", x, y, '-'))
        self.update_dataset_list()
        self.update_graph()
    
    def add_function(self):
        """関数を追加"""
        func_str = self.func_entry.get()
        try:
            x_min = float(self.x_min.get())
            x_max = float(self.x_max.get())
        except ValueError:
            messagebox.showerror("エラー", "X範囲には数値を入力してください")
            return
        
        try:
            x = np.linspace(x_min, x_max, 500)
            y = eval(func_str)
            
            label = func_str.replace('np.', '')
            self.datasets.append((label, x, y, '-'))
            self.update_dataset_list()
            self.update_graph()
        except Exception as e:
            messagebox.showerror("関数エラー", f"関数の評価に失敗しました:\n{e}\n\n例: np.sin(x), x**2, np.exp(-x**2)")
    
    def load_csv(self):
        """CSVファイルを読み込み"""
        filepath = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            x_data = []
            y_data = []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        try:
                            x_data.append(float(row[0]))
                            y_data.append(float(row[1]))
                        except ValueError:
                            continue  # ヘッダー行などをスキップ
            
            if x_data and y_data:
                label = os.path.basename(filepath)
                self.datasets.append((label, np.array(x_data), np.array(y_data), 'o-'))
                self.update_dataset_list()
                self.update_graph()
                messagebox.showinfo("読込完了", f"{len(x_data)}点のデータを読み込みました")
            else:
                messagebox.showerror("エラー", "有効なデータが見つかりませんでした")
        
        except Exception as e:
            messagebox.showerror("読込エラー", f"ファイル読込に失敗しました:\n{e}")
    
    def update_dataset_list(self):
        """データセットリストを更新"""
        self.dataset_listbox.delete(0, tk.END)
        for i, (label, x, y, style) in enumerate(self.datasets):
            self.dataset_listbox.insert(tk.END, f"{i+1}. {label} ({len(x)} pts)")
    
    def remove_dataset(self):
        """選択したデータセットを削除"""
        selection = self.dataset_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.datasets[idx]
            self.update_dataset_list()
            self.update_graph()
    
    def clear_all(self):
        """全データを削除"""
        if messagebox.askyesno("確認", "全てのデータセットを削除しますか？"):
            self.datasets.clear()
            self.update_dataset_list()
            self.update_graph()
    
    def update_graph(self):
        """グラフを更新"""
        self.ax.clear()
        
        # 各データセットをプロット
        for i, (label, x, y, style) in enumerate(self.datasets):
            color = self.plot_colors[i % len(self.plot_colors)]
            self.ax.plot(x, y, style, label=label, color=color, linewidth=1.5, markersize=4)
        
        # ラベル・タイトル
        self.ax.set_title(self.title_entry.get(), fontsize=14, fontweight='bold', color=self.colors['accent'])
        self.ax.set_xlabel(self.xlabel_entry.get(), fontsize=11, color=self.colors['text'])
        self.ax.set_ylabel(self.ylabel_entry.get(), fontsize=11, color=self.colors['text'])
        
        # グリッド
        if self.grid_var.get():
            self.ax.grid(True, alpha=0.3, color=self.colors['text'])
        
        # 凡例
        if self.legend_var.get() and self.datasets:
            legend = self.ax.legend(facecolor=self.colors['panel'], edgecolor=self.colors['accent'])
            for text in legend.get_texts():
                text.set_color(self.colors['text'])
        
        # スタイル維持
        self.ax.set_facecolor(self.colors['surface'])
        self.ax.tick_params(colors=self.colors['text'])
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def export_graph(self, fmt):
        """グラフをエクスポート"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"vectis_graph_{timestamp}.{fmt}"
        
        filepath = filedialog.asksaveasfilename(
            title=f"{fmt.upper()}として保存",
            defaultextension=f".{fmt}",
            initialfile=default_name,
            filetypes=[(f"{fmt.upper()} Files", f"*.{fmt}"), ("All Files", "*.*")]
        )
        
        if filepath:
            try:
                self.fig.savefig(filepath, format=fmt, facecolor=self.colors['bg'], dpi=150)
                messagebox.showinfo("保存完了", f"グラフを保存しました:\n{filepath}")
            except Exception as e:
                messagebox.showerror("保存エラー", f"保存に失敗しました:\n{e}")


def main():
    root = tk.Tk()
    app = VectisGraphStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
