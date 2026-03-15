import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sys
import threading
import time

# --- THEME CONFIG ---
THEME = {
    "bg": "#050505",
    "surface": "#111111", 
    "surface_hover": "#1a1a1a",
    "accent": "#3b82f6", # Blue
    "accent_hover": "#2563eb",
    "danger": "#ff0050",
    "text": "#ffffff",
    "text_dim": "#aaaaaa",
    "font_head": ("Impact", 24),
    "font_body": ("Consolas", 12)
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VectisWindow(ctk.CTk):
    def __init__(self, title="VECTIS APP", width=1000, height=700):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=THEME["bg"])
        
        # Grid Config
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        self.title_label = ctk.CTkLabel(self.header, text=title, font=THEME["font_head"], text_color=THEME["text"])
        self.title_label.pack(side="left")
        
        self.status_label = ctk.CTkLabel(self.header, text="READY", font=("Arial", 10), text_color=THEME["text_dim"])
        self.status_label.pack(side="right", anchor="s", pady=5)

        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color=THEME["bg"])
        self.main_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)

    def set_status(self, text):
        self.status_label.configure(text=text)

class VectisButton(ctk.CTkButton):
    def __init__(self, master, text, command, type="primary", **kwargs):
        colors = {
            "primary": (THEME["accent"], THEME["accent_hover"]),
            "danger": (THEME["danger"], "#cc0040"),
            "ghost": ("transparent", "#222222")
        }
        fg, hov = colors.get(type, colors["primary"])
        
        super().__init__(master, text=text, command=command, 
                         fg_color=fg, hover_color=hov, 
                         corner_radius=4, height=35, 
                         font=("Arial", 11, "bold"), **kwargs)

class ConsolePanel(ctk.CTkTextbox):
    """ A Textbox that acts like a terminal output """
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#0a0a0a", text_color="#00ff00", font=("Consolas", 11), **kwargs)
        self.configure(state="disabled")
    
    def log(self, text):
        self.configure(state="normal")
        self.insert("end", f"{text}\n")
        self.see("end")
        self.configure(state="disabled")
        self.update_idletasks()
        
    def clear(self):
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.configure(state="disabled")

class GlassCard(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, fg_color=THEME["surface"], corner_radius=10, border_width=1, border_color="#333", **kwargs)
        self.pack_propagate(False)
        
        self.lbl = ctk.CTkLabel(self, text=title, font=("Arial", 12, "bold"), text_color=THEME["text_dim"])
        self.lbl.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=5)
