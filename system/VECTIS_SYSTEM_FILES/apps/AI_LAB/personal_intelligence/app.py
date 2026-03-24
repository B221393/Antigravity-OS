import customtkinter as ctk
import os
import json
import webbrowser
from datetime import datetime

# --- CONFIG ---
ctk.set_appearance_mode("Light") # Clean reading mode
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Shared data with YouTube Channel / Intelligence
DATA_UNIVERSE = os.path.abspath(os.path.join(BASE_DIR, "../youtube_channel/data/universe.json"))
DATA_CALENDAR = os.path.abspath(os.path.join(BASE_DIR, "../../data/precog_schedules.json"))

class PersonalIntelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EGO PERSONAL INTELLIGENCE AGENT")
        self.geometry("1100x800")
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Header
        self.header = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ctk.CTkLabel(self.header, text="PERSONAL INTELLIGENCE AGENT", font=("Segoe UI", 24, "bold"), text_color="#1e293b").pack(side="left", padx=20, pady=20)
        ctk.CTkButton(self.header, text="REFRESH FEED", command=self.load_feed).pack(side="right", padx=20)
        
        # 2. Main Content (Split View)
        self.main_area = ctk.CTkFrame(self, fg_color="#f1f5f9")
        self.main_area.grid(row=1, column=0, sticky="nsew")
        
        # Left: Feed Header / Categories
        self.left_panel = ctk.CTkFrame(self.main_area, width=250, fg_color="white")
        self.left_panel.pack(side="left", fill="y", padx=1, pady=1)
        
        ctk.CTkLabel(self.left_panel, text="SOURCES", font=("Segoe UI", 12, "bold"), text_color="#94a3b8").pack(anchor="w", padx=15, pady=15)
        
        self.cat_btns = {}
        for cat in ["ALL", "COMMUTE", "NEWS", "DEV", "JOB"]:
            btn = ctk.CTkButton(self.left_panel, text=cat, fg_color="transparent", text_color="#475569", anchor="w",
                                hover_color="#f8fafc", command=lambda c=cat: self.filter_feed(c))
            btn.pack(fill="x", padx=5, pady=2)
            self.cat_btns[cat] = btn

        # Right: Content Scroll
        self.scroll = ctk.CTkScrollableFrame(self.main_area, fg_color="#f1f5f9")
        self.scroll.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.nodes = []
        self.current_filter = "ALL"
        
        self.load_feed()
        
    def load_feed(self):
        # Load Universe Data
        if os.path.exists(DATA_UNIVERSE):
            try:
                with open(DATA_UNIVERSE, "r", encoding="utf-8") as f:
                    self.nodes = json.load(f).get("nodes", [])
            except:
                self.nodes = []
        
        # Mock some "Commute/Personal" data if not present (since real fetch is offline)
        # In a real app, this would come from a tailored fetcher.
        self.inject_personal_data()
        
        self.filter_feed(self.current_filter)

    def inject_personal_data(self):
        # Adding some mocked personal intelligence as requested
        # "Commute" (Tsukin) info
        commute_info = {
            "id": "commute_001",
            "title": "🚃 Commute Alert: Chuo Line Status",
            "group": "COMMUTE",
            "summary": "Verified delay on Chuo-Sobu Line due to signal inspection at Shinjuku. Expect 10-15 min delays. Recommendation: Use Marunouchi Line if heading to Tokyo station.",
            "importance": 9,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Add to top
        self.nodes.insert(0, commute_info)

    def filter_feed(self, cat):
        self.current_filter = cat
        
        # Highlight btn
        for c, btn in self.cat_btns.items():
            if c == cat: btn.configure(fg_color="#e0f2fe", text_color="#0284c7")
            else: btn.configure(fg_color="transparent", text_color="#475569")
            
        # Draw
        for w in self.scroll.winfo_children(): w.destroy()
        
        items = [n for n in self.nodes if cat == "ALL" or n.get("group", "Other") == cat]
        items.sort(key=lambda x: x.get("importance", 0), reverse=True)
        
        for item in items:
            self.draw_card(item)

    def draw_card(self, item):
        card = ctk.CTkFrame(self.scroll, fg_color="white", border_color="#e2e8f0", border_width=1)
        card.pack(fill="x", pady=10)
        
        # Header
        h = ctk.CTkFrame(card, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=15)
        
        # Tag
        tag_col = "#3b82f6" if item.get("group") == "COMMUTE" else "#64748b"
        ctk.CTkLabel(h, text=f"[{item.get('group', 'REPO')}]", font=("Consolas", 11, "bold"), text_color=tag_col).pack(side="left")
        ctk.CTkLabel(h, text=item.get("timestamp", "")[:16], font=("Consolas", 11), text_color="#cbd5e1").pack(side="right")
        
        # Title
        ctk.CTkLabel(card, text=item.get("title", "No Title"), font=("Segoe UI", 18, "bold"), text_color="#0f172a", anchor="w").pack(fill="x", padx=20, pady=(0, 10))
        
        # Body (FULL TEXT - USER REQUESTED MORE INFO per page)
        # We use a Label with wrapping, but allow it to be long.
        summary_text = item.get("summary", "No details.")
        
        # Visual separator
        ctk.CTkFrame(card, fg_color="#f1f5f9", height=2).pack(fill="x", padx=20, pady=5)
        
        body_lbl = ctk.CTkLabel(card, text=summary_text, font=("Meiryo", 13), text_color="#334155", 
                                anchor="w", justify="left", wraplength=700)
        body_lbl.pack(fill="x", padx=20, pady=15)
        
        # Actions Footer
        f = ctk.CTkFrame(card, fg_color="#f8fafc", height=40)
        f.pack(fill="x")
        
        # Calendar Sync Button
        btn_cal = ctk.CTkButton(f, text="📅 Add to Calendar", font=("Segoe UI", 11), width=120, height=28,
                                fg_color="#ffffff", text_color="#334155", hover_color="#f1f5f9", border_width=1, border_color="#cbd5e1",
                                command=lambda i=item: self.add_to_calendar(i))
        btn_cal.pack(side="right", padx=15, pady=10)
        
        # Link Button (if url exists)
        if "url" in item:
             ctk.CTkButton(f, text="🔗 Open Source", font=("Segoe UI", 11), width=100, height=28,
                                fg_color="transparent", text_color="#2563eb", hover_color="#dbeafe",
                                command=lambda u=item["url"]: webbrowser.open(u)).pack(side="right")

    def add_to_calendar(self, item):
        # Determine Date/Time (Naive for now: Tomorrow 9AM if not specified)
        target_date = datetime.now().strftime("%Y-%m-%d")
        
        new_event = {
            "Date": target_date,
            "Time": "08:00", # Default morning
            "Event": f"[INTEL] {item['title']}",
            "Type": "INTEL",
            "Priority": item.get("importance", 5),
            "Status": "Pending"
        }
        
        # Load existing
        data = []
        if os.path.exists(DATA_CALENDAR):
            try:
                with open(DATA_CALENDAR, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except: pass
            
        data.append(new_event)
        
        try:
            with open(DATA_CALENDAR, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Added to Calendar")
            # Visual feedback on button? (Ideally)
        except Exception as e:
            print(f"Failed to save calendar: {e}")

if __name__ == "__main__":
    app = PersonalIntelApp()
    app.mainloop()
