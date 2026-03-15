"""
VECTIS Data Analyzer v2.0: Simplified & Intuitive
- Click column headers to select X/Y axis
- Sample data button for quick testing
- Instant plot preview
- Modern, clean interface
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import random

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ================= MODERN THEME =================
COLOR_BG = "#1e1e2e"           # Dark background
COLOR_SURFACE = "#313244"      # Card/Panel
COLOR_ACCENT = "#89b4fa"       # Blue accent
COLOR_ACCENT_ALT = "#a6e3a1"   # Green accent
COLOR_TEXT = "#cdd6f4"
COLOR_TEXT_DIM = "#6c7086"
COLOR_SELECTED = "#f38ba8"     # Red for selection
FONT_MAIN = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")

class SimpleDataAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ VECTIS Data Analyzer")
        self.geometry("1100x750")
        self.configure(bg=COLOR_BG)
        
        self.rows = 20
        self.cols = 5
        self.data = [['' for _ in range(self.cols)] for _ in range(self.rows)]
        self.entries = []
        
        # Selection State
        self.x_col = None  # Selected X column
        self.y_col = None  # Selected Y column
        self.col_headers = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # === HEADER ===
        header = tk.Frame(self, bg=COLOR_BG)
        header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header, text="📊 VECTIS Data Analyzer", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT).pack(side=tk.LEFT)
        
        # Quick Actions
        actions = tk.Frame(header, bg=COLOR_BG)
        actions.pack(side=tk.RIGHT)
        
        self.btn_sample = tk.Button(actions, text="🎲 サンプルデータ", font=FONT_MAIN,
                                    bg=COLOR_SURFACE, fg=COLOR_TEXT, bd=0, padx=15, pady=8,
                                    command=self.load_sample_data, cursor="hand2")
        self.btn_sample.pack(side=tk.LEFT, padx=5)
        
        self.btn_csv = tk.Button(actions, text="📂 CSV読み込み", font=FONT_MAIN,
                                 bg=COLOR_SURFACE, fg=COLOR_TEXT, bd=0, padx=15, pady=8,
                                 command=self.open_csv, cursor="hand2")
        self.btn_csv.pack(side=tk.LEFT, padx=5)
        
        # === MAIN CONTENT ===
        main = tk.Frame(self, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left: Data Table
        left_panel = tk.Frame(main, bg=COLOR_SURFACE, bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="📋 データテーブル", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(anchor="w", padx=15, pady=10)
        
        # Selection Guide
        self.guide_label = tk.Label(left_panel, text="💡 列ヘッダーをクリックしてX軸・Y軸を選択", 
                                    font=FONT_MAIN, bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM)
        self.guide_label.pack(anchor="w", padx=15)
        
        # Selection Status
        self.status_frame = tk.Frame(left_panel, bg=COLOR_SURFACE)
        self.status_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.x_label = tk.Label(self.status_frame, text="X軸: 未選択", font=FONT_MAIN, bg=COLOR_SURFACE, fg=COLOR_ACCENT)
        self.x_label.pack(side=tk.LEFT, padx=10)
        
        self.y_label = tk.Label(self.status_frame, text="Y軸: 未選択", font=FONT_MAIN, bg=COLOR_SURFACE, fg=COLOR_ACCENT_ALT)
        self.y_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(self.status_frame, text="リセット", font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_TEXT, bd=0,
                  command=self.reset_selection).pack(side=tk.RIGHT, padx=10)
        
        # Table
        table_container = tk.Frame(left_panel, bg=COLOR_SURFACE)
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        canvas = tk.Canvas(table_container, bg=COLOR_BG, highlightthickness=0)
        v_scroll = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=canvas.yview)
        
        self.table_frame = tk.Frame(canvas, bg=COLOR_BG)
        canvas.configure(yscrollcommand=v_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Column Headers (Clickable!)
        for c in range(self.cols):
            col_name = chr(65 + c)
            btn = tk.Button(self.table_frame, text=col_name, width=12, font=FONT_HEADER,
                            bg=COLOR_SURFACE, fg=COLOR_TEXT, bd=1, relief="flat",
                            command=lambda col=c: self.select_column(col), cursor="hand2")
            btn.grid(row=0, column=c + 1, sticky="ew", padx=1, pady=1)
            self.col_headers.append(btn)
        
        # Data Cells
        for r in range(self.rows):
            lbl_row = tk.Label(self.table_frame, text=str(r + 1), width=4, bg=COLOR_SURFACE, fg=COLOR_TEXT_DIM)
            lbl_row.grid(row=r + 1, column=0, sticky="ns")
            
            row_entries = []
            for c in range(self.cols):
                entry = tk.Entry(self.table_frame, width=12, font=FONT_MAIN,
                                 bg=COLOR_BG, fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
                                 relief="flat", bd=2)
                entry.grid(row=r + 1, column=c + 1, sticky="ew", padx=1, pady=1)
                entry.bind("<FocusOut>", lambda e, row=r, col=c: self.save_cell(row, col, e.widget.get()))
                row_entries.append(entry)
            self.entries.append(row_entries)
        
        # Right: Graph Preview
        right_panel = tk.Frame(main, bg=COLOR_SURFACE, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="📈 グラフプレビュー", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(anchor="w", padx=15, pady=10)
        
        # Plot Buttons
        plot_btns = tk.Frame(right_panel, bg=COLOR_SURFACE)
        plot_btns.pack(fill=tk.X, padx=15, pady=5)
        
        self.btn_line = tk.Button(plot_btns, text="📈 折れ線グラフ", font=FONT_MAIN,
                                  bg=COLOR_ACCENT, fg="#000", bd=0, padx=20, pady=10,
                                  command=lambda: self.plot("line"), cursor="hand2")
        self.btn_line.pack(side=tk.LEFT, padx=5)
        
        self.btn_scatter = tk.Button(plot_btns, text="⚫ 散布図", font=FONT_MAIN,
                                     bg=COLOR_ACCENT_ALT, fg="#000", bd=0, padx=20, pady=10,
                                     command=lambda: self.plot("scatter"), cursor="hand2")
        self.btn_scatter.pack(side=tk.LEFT, padx=5)
        
        # Graph Area
        self.graph_frame = tk.Frame(right_panel, bg=COLOR_BG)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        if HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(4, 3), dpi=100, facecolor=COLOR_BG)
            self.ax = self.figure.add_subplot(111)
            self.ax.set_facecolor(COLOR_BG)
            self.ax.tick_params(colors=COLOR_TEXT_DIM)
            self.ax.spines['bottom'].set_color(COLOR_TEXT_DIM)
            self.ax.spines['left'].set_color(COLOR_TEXT_DIM)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            self.canvas_plot = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
            self.canvas_plot.draw()
            self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(self.graph_frame, text="Matplotlib未インストール", bg=COLOR_BG, fg=COLOR_TEXT_DIM).pack(pady=50)
    
    def save_cell(self, row, col, value):
        self.data[row][col] = value
    
    def select_column(self, col_index):
        """Smart column selection: First click = X, Second click = Y"""
        col_name = chr(65 + col_index)
        
        if self.x_col is None:
            self.x_col = col_index
            self.col_headers[col_index].config(bg=COLOR_ACCENT, fg="#000")
            self.x_label.config(text=f"X軸: {col_name}列")
            self.guide_label.config(text="👆 Y軸にする列をクリック")
        elif self.y_col is None and col_index != self.x_col:
            self.y_col = col_index
            self.col_headers[col_index].config(bg=COLOR_ACCENT_ALT, fg="#000")
            self.y_label.config(text=f"Y軸: {col_name}列")
            self.guide_label.config(text="✅ プロットボタンを押してグラフ作成！")
    
    def reset_selection(self):
        self.x_col = None
        self.y_col = None
        for btn in self.col_headers:
            btn.config(bg=COLOR_SURFACE, fg=COLOR_TEXT)
        self.x_label.config(text="X軸: 未選択")
        self.y_label.config(text="Y軸: 未選択")
        self.guide_label.config(text="💡 列ヘッダーをクリックしてX軸・Y軸を選択")
    
    def get_column_data(self, col_index):
        values = []
        for row in self.data:
            try:
                val = float(row[col_index])
                values.append(val)
            except (ValueError, IndexError):
                pass
        return values
    
    def load_sample_data(self):
        """Load sample data for quick testing"""
        sample_x = list(range(1, 11))
        sample_y = [x**2 + random.uniform(-5, 5) for x in sample_x]
        
        for i, (x, y) in enumerate(zip(sample_x, sample_y)):
            if i < self.rows:
                self.data[i][0] = str(x)
                self.data[i][1] = f"{y:.1f}"
                self.entries[i][0].delete(0, tk.END)
                self.entries[i][0].insert(0, str(x))
                self.entries[i][1].delete(0, tk.END)
                self.entries[i][1].insert(0, f"{y:.1f}")
        
        # Auto-select columns
        self.reset_selection()
        self.select_column(0)  # X = A
        self.select_column(1)  # Y = B
    
    def open_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for r, row in enumerate(reader):
                        if r >= self.rows: break
                        for c, val in enumerate(row):
                            if c >= self.cols: break
                            self.data[r][c] = val
                            self.entries[r][c].delete(0, tk.END)
                            self.entries[r][c].insert(0, val)
            except Exception as e:
                messagebox.showerror("エラー", f"CSV読み込み失敗: {e}")
    
    def plot(self, plot_type):
        if self.x_col is None or self.y_col is None:
            messagebox.showinfo("ヒント", "まず列ヘッダーをクリックしてX軸・Y軸を選択してください。")
            return
        
        x_data = self.get_column_data(self.x_col)
        y_data = self.get_column_data(self.y_col)
        
        if not x_data or not y_data:
            messagebox.showwarning("警告", "選択した列に数値データがありません。")
            return
        
        # Align lengths
        min_len = min(len(x_data), len(y_data))
        x_data = x_data[:min_len]
        y_data = y_data[:min_len]
        
        self.ax.clear()
        self.ax.set_facecolor(COLOR_BG)
        
        if plot_type == "line":
            self.ax.plot(x_data, y_data, marker='o', linestyle='-', color=COLOR_ACCENT, linewidth=2, markersize=6)
        else:
            self.ax.scatter(x_data, y_data, color=COLOR_ACCENT_ALT, s=50, alpha=0.8)
        
        self.ax.set_xlabel(f"{chr(65 + self.x_col)}列", color=COLOR_TEXT_DIM)
        self.ax.set_ylabel(f"{chr(65 + self.y_col)}列", color=COLOR_TEXT_DIM)
        self.ax.tick_params(colors=COLOR_TEXT_DIM)
        self.ax.grid(True, linestyle='--', alpha=0.3, color=COLOR_TEXT_DIM)
        
        self.figure.tight_layout()
        self.canvas_plot.draw()

if __name__ == "__main__":
    app = SimpleDataAnalyzer()
    app.mainloop()
