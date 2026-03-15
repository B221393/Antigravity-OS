import customtkinter as ctk
import os
import sys
import json
import datetime

# --- CONFIG ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../data/precog_schedules.json"))

class MagiCalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VECTIS MAGI PRECOGNITION")
        self.geometry("600x800")
        self.configure(fg_color="#0f172a") # Dark Slate
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(self.header, text="🔮 MAGI CALENDAR", font=("Segoe UI", 24, "bold"), text_color="#f59e0b").pack(side="left")
        ctk.CTkButton(self.header, text="REFRESH", width=80, command=self.refresh_data, fg_color="#334155", hover_color="#475569").pack(side="right")
        
        # Scroll Area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh_data()
        
    def refresh_data(self):
        for w in self.scroll.winfo_children():
            w.destroy()
            
        if not os.path.exists(DATA_FILE):
            ctk.CTkLabel(self.scroll, text="No Schedule Data Found", text_color="gray").pack(pady=20)
            return
            
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            ctk.CTkLabel(self.scroll, text=f"Error loading JSON: {e}", text_color="red").pack(pady=20)
            return
            
        # Filter & Sort
        data.sort(key=lambda x: x.get("Time", "00:00"))
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Today
        ctk.CTkLabel(self.scroll, text=f"TODAY ({today_str})", font=("Segoe UI", 16, "bold"), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(10,5))
        
        found = False
        for item in data:
            if item.get("Date") == today_str:
                self.draw_card(item)
                found = True
        
        if not found:
            ctk.CTkLabel(self.scroll, text="No immediate protocols.", text_color="#475569").pack(pady=10)
            
        # Future
        ctk.CTkLabel(self.scroll, text="FUTURE OPERATIONS", font=("Segoe UI", 16, "bold"), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(30,5))
        for item in data:
            if item.get("Date") > today_str:
                self.draw_card(item)

    def draw_card(self, item):
        card = ctk.CTkFrame(self.scroll, fg_color="#1e293b", border_color="#f59e0b", border_width=1 if item.get("Priority", 3) >=4 else 0)
        card.pack(fill="x", pady=5)
        
        ctk.CTkLabel(card, text=item.get("Time", "--:--"), font=("Consolas", 20, "bold"), text_color="#f59e0b").pack(side="left", padx=15, pady=15)
        
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(info, text=item.get("Event", "Unknown"), font=("Meiryo", 14, "bold"), text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=f"Priority: {item.get('Priority', 3)}", font=("Consolas", 10), text_color="#64748b", anchor="w").pack(fill="x")
        
        status = item.get("Status", "Pending")
        col = "#22c55e" if status == "Completed" else "#94a3b8"
        ctk.CTkLabel(card, text=status.upper(), font=("Segoe UI", 10, "bold"), text_color=col).pack(side="right", padx=15)

if __name__ == "__main__":
    app = MagiCalendarApp()
    app.mainloop()
