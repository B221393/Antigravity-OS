
import tkinter
# VECTIS共通UIモジュール
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from vectis_ui_modules import VectisUIFactory, setup_style
except ImportError:
    pass as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime

# --- CONFIG & THEME ---
THEME = {
    "bg_main": "#0f172a",       # Slate 900
    "bg_panel": "#1e293b",      # Slate 800
    "fg_text": "#f8fafc",       # Slate 50
    "fg_dim": "#94a3b8",        # Slate 400
    "accent": "#3b82f6",        # Blue 500
    "accent_hover": "#2563eb",  # Blue 600
    "success": "#22c55e",       # Green 500
    "border": "#334155"         # Slate 700
}

CATEGORIES = {
    "🎬 アニメ/ドラマ鑑賞": {"color": "#be123c", "xp": 10}, # Rose 700
    "📖 小説/読書": {"color": "#b45309", "xp": 12},       # Amber 700
    "💻 プログラミング/技術": {"color": "#0f766e", "xp": 15}, # Teal 700
    "📝 創作/執筆": {"color": "#1d4ed8", "xp": 15},       # Blue 700
    "🔬 研究/学習": {"color": "#7e22ce", "xp": 20},       # Purple 700
    "🧘 自己研鑽/日常": {"color": "#374151", "xp": 5}        # Gray 700
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "todo_log.json")

# --- DATA MANAGER ---
class DataManager:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# --- UI APP ---
class IdentityLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDENTITY LOG - VECTIS OS")
        self.root.geometry("1000x600")
        self.root.configure(bg=THEME["bg_main"])
        
        self.data_manager = DataManager()
        self.todos = self.data_manager.load()
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Layout
        self.setup_ui()
        self.refresh_ui()

    def configure_styles(self):
        # Configure generic TTK styles to match dark theme
        self.style.configure(".", 
            background=THEME["bg_main"], 
            foreground=THEME["fg_text"], 
            fieldbackground=THEME["bg_panel"],
            font=("Segoe UI", 10))
            
        self.style.configure("TFrame", background=THEME["bg_main"])
        self.style.configure("Panel.TFrame", background=THEME["bg_panel"], relief="flat")
        
        self.style.configure("TLabel", background=THEME["bg_main"], foreground=THEME["fg_text"])
        self.style.configure("Panel.TLabel", background=THEME["bg_panel"], foreground=THEME["fg_text"])
        self.style.configure("Dim.TLabel", background=THEME["bg_panel"], foreground=THEME["fg_dim"], font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", background=THEME["bg_panel"], foreground=THEME["fg_text"], font=("Segoe UI", 14, "bold"))
        self.style.configure("Xp.TLabel", background=THEME["bg_panel"], foreground=THEME["success"], font=("Consolas", 10, "bold"))

        self.style.configure("TButton", 
            background=THEME["accent"], 
            foreground="white", 
            borderwidth=0, 
            focuscolor=THEME["bg_panel"])
        self.style.map("TButton", 
            background=[('active', THEME["accent_hover"])])
            
        self.style.configure("Card.TFrame", background=THEME["bg_panel"], relief="raised", borderwidth=1)

    def setup_ui(self):
        # --- LEFT SIDEBAR (Input & Stats) ---
        self.sidebar = ttk.Frame(self.root, style="Panel.TFrame", width=300, padding=20)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # Fixed width
        
        # Title
        ttk.Label(self.sidebar, text="IDENTITY LOG", style="Header.TLabel").pack(anchor="w", pady=(0, 5))
        ttk.Label(self.sidebar, text="日々の積み重ねがあなたを作る", style="Dim.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Stats
        self.stats_frame = ttk.Frame(self.sidebar, style="Panel.TFrame")
        self.stats_frame.pack(fill="x", pady=10)
        
        self.lbl_level = ttk.Label(self.stats_frame, text="LEVEL 1", style="Header.TLabel")
        self.lbl_level.pack(anchor="w")
        self.lbl_xp = ttk.Label(self.stats_frame, text="0 XP", style="Xp.TLabel")
        self.lbl_xp.pack(anchor="w")
        
        self.progress_canvas = tk.Canvas(self.stats_frame, height=6, bg=THEME["bg_main"], highlightthickness=0)
        self.progress_canvas.pack(fill="x", pady=(5, 0))
        
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=20)
        
        # Input Form
        ttk.Label(self.sidebar, text="NEW ENTRY", style="Header.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        ttk.Label(self.sidebar, text="Title", style="Panel.TLabel").pack(anchor="w")
        self.entry_title = ttk.Entry(self.sidebar, font=("Segoe UI", 10))
        self.entry_title.pack(fill="x", pady=(0, 10))
        
        ttk.Label(self.sidebar, text="Category", style="Panel.TLabel").pack(anchor="w")
        self.var_cat = tk.StringVar(value=list(CATEGORIES.keys())[0])
        self.combo_cat = ttk.Combobox(self.sidebar, textvariable=self.var_cat, values=list(CATEGORIES.keys()), state="readonly")
        self.combo_cat.pack(fill="x", pady=(0, 10))
        
        ttk.Label(self.sidebar, text="Note", style="Panel.TLabel").pack(anchor="w")
        self.text_note = tk.Text(self.sidebar, height=4, bg="#0f172a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 9))
        self.text_note.pack(fill="x", pady=(0, 20))
        
        self.btn_add = ttk.Button(self.sidebar, text="ADD TO IDENTITY", command=self.add_todo, cursor="hand2")
        self.btn_add.pack(fill="x")

        # --- RIGHT CONTENT (Lists) ---
        self.main_area = ttk.Frame(self.root, padding=20)
        self.main_area.pack(side="right", fill="both", expand=True)
        
        # Tabs
        self.tabs = ttk.Notebook(self.main_area)
        self.tabs.pack(fill="both", expand=True)
        
        self.tab_active = ttk.Frame(self.tabs)
        self.tab_history = ttk.Frame(self.tabs)
        
        self.tabs.add(self.tab_active, text="🔥 ACTIVE")
        self.tabs.add(self.tab_history, text="📚 ARCHIVE")
        
        # Helper to create scrollable frame
        self.frame_active_list = self.create_scrollable_frame(self.tab_active)
        self.frame_history_list = self.create_scrollable_frame(self.tab_history)

    def create_scrollable_frame(self, parent):
        canvas = tk.Canvas(parent, bg=THEME["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=650) # Approx width
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame

    def refresh_ui(self):
        # 1. Calculate Stats
        completed = [t for t in self.todos if t.get('done')]
        total_xp = sum([CATEGORIES.get(t['cat'], {}).get('xp', 0) for t in completed])
        level = total_xp // 100 + 1
        progress = (total_xp % 100) / 100.0
        
        self.lbl_level.config(text=f"LEVEL {level}")
        self.lbl_xp.config(text=f"TOTAL XP: {total_xp}")
        
        # Draw Progress Bar
        self.progress_canvas.delete("all")
        w = self.stats_frame.winfo_width()
        if w < 10: w = 260 # fallback
        self.progress_canvas.create_rectangle(0, 0, w, 6, fill="#334155", width=0)
        self.progress_canvas.create_rectangle(0, 0, w * progress, 6, fill=THEME["success"], width=0)

        # 2. Clear Lists
        for widget in self.frame_active_list.winfo_children(): widget.destroy()
        for widget in self.frame_history_list.winfo_children(): widget.destroy()
        
        # 3. Render Active
        active = [t for t in self.todos if not t.get('done')]
        if not active:
            ttk.Label(self.frame_active_list, text="No active tasks. Start something new!", style="Dim.TLabel").pack(pady=20)
        else:
            for t in active:
                self.render_card(self.frame_active_list, t, is_active=True)
                
        # 4. Render History
        history = [t for t in self.todos if t.get('done')]
        history.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        
        if not history:
             ttk.Label(self.frame_history_list, text="No history yet.", style="Dim.TLabel").pack(pady=20)
        else:
            for t in history:
                self.render_card(self.frame_history_list, t, is_active=False)

    def render_card(self, parent, task, is_active):
        cat_conf = CATEGORIES.get(task['cat'], {"color": "#888", "xp": 0})
        color = cat_conf['color']
        
        # Card Frame
        card = tk.Frame(parent, bg=THEME["bg_panel"], pady=10, padx=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Color Stripe
        stripe = tk.Frame(card, bg=color, width=4)
        stripe.pack(side="left", fill="y", padx=(0, 10))
        
        # Content
        content = tk.Frame(card, bg=THEME["bg_panel"])
        content.pack(side="left", fill="both", expand=True)
        
        header = tk.Frame(content, bg=THEME["bg_panel"])
        header.pack(fill="x")
        
        tk.Label(header, text=task['title'], bg=THEME["bg_panel"], fg="white", font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(header, text=f"+{cat_conf['xp']} XP", bg=THEME["bg_panel"], fg=THEME["success"], font=("Consolas", 9)).pack(side="right")
        
        meta_text = f"{task['cat']} | {task['created'][:16].replace('T', ' ')}"
        if not is_active:
             meta_text += f" | ✅ {task.get('completed_at', '')[:10]}"
             
        tk.Label(content, text=meta_text, bg=THEME["bg_panel"], fg=THEME["fg_dim"], font=("Segoe UI", 8)).pack(anchor="w")
        
        if task['note']:
            tk.Label(content, text=task['note'], bg=THEME["bg_panel"], fg=THEME["fg_text"], wraplength=400, justify="left", pady=5).pack(anchor="w")
            
        # Action Button (Only for Active)
        if is_active:
             btn = tk.Button(card, text="COMPLETE", bg=THEME["success"], fg="white", relief="flat", 
                             font=("Segoe UI", 9, "bold"), cursor="hand2",
                             command=lambda t=task: self.complete_task(t))
             btn.pack(side="right", padx=10)

    def add_todo(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showwarning("Input Error", "Please enter a title.")
            return
            
        new_task = {
            "id": str(datetime.now().timestamp()),
            "title": title,
            "cat": self.var_cat.get(),
            "note": self.text_note.get("1.0", "end-1c").strip(),
            "done": False,
            "created": datetime.now().isoformat()
        }
        
        self.todos.append(new_task)
        self.data_manager.save(self.todos)
        
        # Clear form
        self.entry_title.delete(0, tk.END)
        self.text_note.delete("1.0", tk.END)
        
        self.refresh_ui()
        
    def complete_task(self, task):
        task['done'] = True
        task['completed_at'] = datetime.now().isoformat()
        self.data_manager.save(self.todos)
        self.refresh_ui()
        messagebox.showinfo("Good job!", f"Completed: {task['title']}\nYou gained XP!")

if __name__ == "__main__":
    root = tk.Tk()
    app = IdentityLogApp(root)
    root.mainloop()
