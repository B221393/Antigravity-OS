import tkinter as tk
from tkinter import ttk
import sys
import os

# =============================================================================
# THEME CONFIGURATION
# =============================================================================
BASE_FONT = ("Meiryo", 9)
BOLD_FONT = ("Meiryo", 9, "bold")
HEADER_FONT = ("Meiryo", 11, "bold")

def setup_style(root):
    """Applies the standard EGO High-Density Utility Style."""
    style = ttk.Style(root)
    try:
        style.theme_use('vista') 
    except:
        style.theme_use('clam')

    style.configure("TLabel", font=BASE_FONT)
    style.configure("TButton", font=BASE_FONT)
    style.configure("TCheckbutton", font=BASE_FONT)
    style.configure("TRadiobutton", font=BASE_FONT)
    style.configure("TLabelframe.Label", font=BOLD_FONT, foreground="#333")
    style.configure("Treeview.Heading", font=BOLD_FONT)
    style.configure("Treeview", font=BASE_FONT, rowheight=24)

# =============================================================================
# WIDGET FACTORY
# =============================================================================
class VectisUIFactory:
    @staticmethod
    def create_window(title, width=1000, height=700):
        root = tk.Tk()
        root.title(title)
        root.geometry(f"{width}x{height}")
        root.configure(bg="#f0f0f0")
        setup_style(root)
        
        # Standard Menu
        menubar = tk.Menu(root)
        menubar.add_command(label="ファイル(F)")
        menubar.add_command(label="設定(S)")
        menubar.add_command(label="ヘルプ(H)")
        root.config(menu=menubar)
        
        return root

    @staticmethod
    def create_notebook(parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=5, pady=5)
        return nb

    @staticmethod
    def create_tab(notebook, title):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        return frame

    @staticmethod
    def create_labelframe(parent, title, relx, rely, relwidth, relheight):
        lf = ttk.LabelFrame(parent, text=title, padding=5)
        lf.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)
        return lf

# =============================================================================
# APP NAME MAPPING (For clean display)
# =============================================================================
APP_NAME_MAP = {
    "es_assistant": "ES Assistant (就活支援)",
    "shukatsu_patrol": "就活パトロール (Jobs)",
    "intelligence_aggregator": "情報収集ハブ (Intel)",
    "shogi_dojo": "将棋道場 (Shogi)",
    "job_hunting": "就活総合管理",
    "youtube_channel": "YouTube分析",
    "vectis_coder": "EGO Coder (Dev)",
    "todo": "ToDo管理",
    "calendar": "カレンダー",
    "diary": "業務日誌"
}

def get_clean_name(app_folder_name):
    return APP_NAME_MAP.get(app_folder_name, app_folder_name.replace("_", " ").title())

def is_intelligence_app(path_or_name):
    keywords = ["shukatsu", "job", "intelligence", "news", "scout", "research", "patrol"]
    name = path_or_name.lower()
    return any(k in name for k in keywords)
