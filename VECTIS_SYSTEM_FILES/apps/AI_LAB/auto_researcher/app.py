import customtkinter as ctk
import os
import sys
import json
import time
import threading

# --- THEME ---
COLOR_BG = "#f8fafc"
COLOR_SIDEBAR = "#ffffff"
COLOR_TEXT_MAIN = "#1e293b"
COLOR_TEXT_SUB = "#64748b"
COLOR_ACCENT = "#3b82f6"
COLOR_BORDER = "#e2e8f0"

class AutoResearcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EGO AUTO RESEARCHER")
        self.geometry("900x600")
        self.configure(fg_color=COLOR_BG)
        
        # SEARCH PATHS
        self.history_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../s_history.json"))
        
        # LAYOUT
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # HEADER
        self.header = ctk.CTkFrame(self, height=60, fg_color="#fff", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(self.header, text="🔭 DEEP WATCHER", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=20, pady=15)
        self.lbl_status = ctk.CTkLabel(self.header, text="MONITORING ACTIVE", font=("Consolas", 12), text_color="#22c55e")
        self.lbl_status.pack(side="right", padx=20)
        
        # CONTENT SPLIT
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=2) # Knowledge Graph / List
        self.main_content.grid_columnconfigure(1, weight=1) # Recent Events
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # 1. KNOWLEDGE STREAM (Left)
        self.frame_stream = ctk.CTkFrame(self.main_content, fg_color="#fff", corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.frame_stream.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(self.frame_stream, text="KNOWLEDGE STREAM", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_SUB).pack(padx=15, pady=15, anchor="w")
        
        self.scroll_stream = ctk.CTkScrollableFrame(self.frame_stream, fg_color="transparent")
        self.scroll_stream.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 2. RISU WATCH / ALERTS (Right)
        self.frame_alerts = ctk.CTkFrame(self.main_content, fg_color="#fff", corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        self.frame_alerts.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.frame_alerts, text="RISU WATCH & ALERTS", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_SUB).pack(padx=15, pady=15, anchor="w")
        
        self.scroll_alerts = ctk.CTkScrollableFrame(self.frame_alerts, fg_color="transparent")
        self.scroll_alerts.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Start Monitor
        self.last_load = 0
        self.monitor_loop()
        
    def monitor_loop(self):
        try:
            if os.path.exists(self.history_file):
                mtime = os.path.getmtime(self.history_file)
                if mtime > self.last_load:
                    self.reload_data()
                    self.last_load = mtime
        except Exception as e:
            print(e)
            
        self.after(2000, self.monitor_loop)
        
    def reload_data(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                nodes = data.get("nodes", [])
                
                # Clear Stream
                for w in self.scroll_stream.winfo_children(): w.destroy()
                
                # Show last 20 nodes
                for node in reversed(nodes[-20:]):
                    self.create_node_card(node)
                    
                # Risu filter
                risu_nodes = [n for n in nodes if "就活" in n.get("content", "") or "syukatsurisu" in n.get("source", "")]
                
                # Clear Alerts
                for w in self.scroll_alerts.winfo_children(): w.destroy()
                
                for node in reversed(risu_nodes[-10:]):
                    self.create_alert_card(node)
                    
        except Exception as e:
            print(f"Load Error: {e}")

    def create_node_card(self, node):
        card = ctk.CTkFrame(self.scroll_stream, fg_color="#eff6ff", corner_radius=8, border_width=1, border_color="#dbeafe")
        card.pack(fill="x", pady=5)
        
        # Title
        title = node.get("title", "Unknown")
        ctk.CTkLabel(card, text=title[:40], font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=10, pady=(5,0))
        
        # Content
        content = node.get("content", "")[:100].replace("\n", " ") + "..."
        ctk.CTkLabel(card, text=content, font=("Segoe UI", 11), text_color=COLOR_TEXT_SUB, wraplength=400).pack(anchor="w", padx=10, pady=(0,5))
        
    def create_alert_card(self, node):
        card = ctk.CTkFrame(self.scroll_alerts, fg_color="#fff7ed", corner_radius=8, border_width=1, border_color="#ffedd5") # Orange tint
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text="🔔 SQUIRREL SIGNAL", font=("Segoe UI", 10, "bold"), text_color="#ea580c").pack(anchor="w", padx=10, pady=(5,0))
        content = node.get("content", "")[:80] + "..."
        ctk.CTkLabel(card, text=content, font=("Segoe UI", 11), text_color="#9a3412", wraplength=200).pack(anchor="w", padx=10, pady=(0,5))

if __name__ == "__main__":
    app = AutoResearcherApp()
    app.mainloop()
