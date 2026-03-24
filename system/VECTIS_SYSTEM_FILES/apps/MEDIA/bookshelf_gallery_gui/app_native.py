import os
import glob
import re
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Set Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKSHELF_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../OBSIDIAN_WRITING/BOOKSHELF"))

class AnimatedCarousel(ctk.CTkFrame):
    def __init__(self, master, books, on_select):
        super().__init__(master, fg_color="transparent")
        self.books = books
        self.on_select = on_select
        self.current_index = 0
        self.cards = []
        
        # Canvas for 3D-like rendering
        self.canvas_width = 1000
        self.canvas_height = 500
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="#050505", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Navigation zones
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<MouseWheel>", self.handle_wheel)
        
        self.draw_scene()

    def handle_wheel(self, event):
        if event.delta > 0: self.move(-1)
        else: self.move(1)

    def handle_click(self, event):
        # Check if clicked center
        center_x = self.canvas_width / 2
        click_x = event.x
        
        # Click regions
        if click_x < center_x - 150: self.move(-1)
        elif click_x > center_x + 150: self.move(1)
        else:
            # Center clicked
            if 0 <= self.current_index < len(self.books):
                self.on_select(self.books[self.current_index])

    def move(self, direction):
        new_idx = self.current_index + direction
        if 0 <= new_idx < len(self.books):
            self.current_index = new_idx
            self.draw_scene()

    def draw_scene(self):
        self.canvas.delete("all")
        
        # Fake 3D logic: Draw from outside in (painter's algorithm)
        # Visible range: +/- 3 items
        
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        card_w, card_h = 240, 360
        spacing = 180
        
        render_queue = []
        
        for offset in range(-3, 4): # -3 to +3
            idx = self.current_index + offset
            if idx < 0 or idx >= len(self.books): continue
            
            # Calculate 3D transform properties
            abs_offset = abs(offset)
            scale = 1.0 - (abs_offset * 0.15)
            opacity = 1.0 - (abs_offset * 0.3)
            
            x_pos = center_x + (offset * spacing)
            # Perspective shift
            if offset < 0: x_pos += (abs_offset * 40) 
            if offset > 0: x_pos -= (abs_offset * 40)
            
            z_index = 100 - abs_offset
            
            render_queue.append({
                "idx": idx,
                "x": x_pos,
                "y": center_y,
                "w": card_w * scale,
                "h": card_h * scale,
                "scale": scale,
                "opacity": opacity,
                "z": z_index,
                "offset": offset,
                "data": self.books[idx]
            })
            
        # Sort by Z (painters algorithm: lowest Z first? No, furthest items first.)
        # Furthest items have lowest scale/opacity. 
        # Z-index logic: 0 is center (top), higher offset is lower Z.
        render_queue.sort(key=lambda item: item['z'])
        
        for item in render_queue:
            self.draw_card(item)

    def draw_card(self, item):
        x, y, w, h = item['x'], item['y'], item['w'], item['h']
        color = self.get_color(item['idx'])
        
        # Shadow
        self.canvas.create_rectangle(
            x - w/2, y - h/2 + 20, x + w/2, y + h/2 + 20, 
            fill="#111", outline="", tags=f"card_{item['idx']}"
        )
        
        # Card Body (Gradient approximation)
        self.canvas.create_rectangle(
            x - w/2, y - h/2, x + w/2, y + h/2, 
            fill=color, outline="#333" if item['offset']!=0 else "#fff", width=1 if item['offset']!=0 else 2,
            tags=f"card_{item['idx']}"
        )
        
        # Text
        if item['scale'] > 0.6:
            font_size = int(14 * item['scale'])
            title_font = ("Arial", font_size, "bold")
            self.canvas.create_text(
                x, y, text=item['data']['title'], 
                fill="white", font=title_font, width=w-20, justify="center"
            )
            
            tag_font = ("Arial", int(10 * item['scale']))
            self.canvas.create_text(
                x, y - h/3, text=item['data']['category'],
                fill="#ccc", font=tag_font
            )

    def get_color(self, idx):
        colors = ["#1e3c72", "#2a5298", "#4b6cb7", "#182848", "#11998e", "#38ef7d", "#8E2DE2", "#4A00E0"]
        return colors[idx % len(colors)]

class BookshelfApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EGO VISUAL ARCHIVE (Native)")
        self.geometry("1100x700")
        
        # Grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(self.header, text="EGO MEMORY ARCHIVE", font=("Impact", 24)).pack(side="left")
        
        # Mode State
        self.current_mode = "APPS" # Default to Apps for "Hub" feel, or Books? User usage pattern? 
        # User emphasized "Connect with all apps", so Apps first makes sense as a Launcher.
        
        # Data Caches
        self.books = self.load_books()
        self.apps = self.load_apps()
        
        # Grid layout for content
        self.gallery_frame = ctk.CTkFrame(self, fg_color="#050505")
        self.gallery_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Init with APPS
        self.refresh_carousel()
        
        # Mode Switcher (Bottom / Top)
        self.controls = ctk.CTkFrame(self.header, fg_color="transparent")
        self.controls.pack(side="right", padx=20)
        
        # Create control buttons
        self.btn_apps = ctk.CTkButton(self.controls, text="💻 APPLICATIONS", width=120, command=lambda: self.set_mode("APPS"), fg_color="#3b82f6")
        self.btn_apps.pack(side="left", padx=5)
        self.btn_books = ctk.CTkButton(self.controls, text="📚 KNOWLEDGE", width=120, command=lambda: self.set_mode("BOOKS"), fg_color="transparent", border_width=1, border_color="#555")
        self.btn_books.pack(side="left", padx=5)
        
        # Create Chaos Patrol button
        self.chaos_btn = ctk.CTkButton(self.controls, text="⚡ START CHAOS PATROL", width=140, command=self.run_chaos_patrol, fg_color="#ef4444")
        self.chaos_btn.pack(side="left", padx=5)
        
        # Reader Overlay
        self.reader_window = None

    def load_apps(self):
        apps = []
        
        # Color mapping based on category hash
        def get_color_idx(s):
            return sum(ord(c) for c in s) % 8

        # 1. ROOT SYSTEM LAUNCHERS (c:/.../EGO_SYSTEM_FILES/*.bat)
        # -----------------------------------------------------------
        root_sys = os.path.abspath(os.path.join(BASE_DIR, "../../../"))
        for f in glob.glob(os.path.join(root_sys, "*.bat")):
            name = os.path.basename(f)
            if name.upper().startswith("_OLD") or "ACTIVAT" in name.upper(): continue
            
            # Clean Title
            title = name.replace(".bat", "")
            # Remove numeric prefixes like 001_, 002_
            title = re.sub(r'^\d+_', '', title).replace("_", " ")
            
            apps.append({
                "title": title,
                "category": "ROOT SYSTEM",
                "desc": f"System Launcher: {name}",
                "path": f, # Absolute path
                "color_idx": 0 # Special color for Root
            })

        # 2. RECURSIVE APP SCAN (c:/.../EGO_SYSTEM_FILES/apps/**/*.bat)
        # ----------------------------------------------------------------
        apps_root = os.path.abspath(os.path.join(BASE_DIR, "../../../apps"))
        
        for root, dirs, files in os.walk(apps_root):
            # Skip noise folders
            if any(x in root for x in [".venv", "node_modules", "__pycache__", ".git", "bin", "Scripts"]):
                continue
                
            for file in files:
                if file.endswith(".bat"):
                    name = file.lower()
                    
                    # Exclude non-launchers
                    if name.startswith("_old"): continue
                    if "install" in name or "setup" in name or "update" in name: continue
                    if "activate" in name: continue
                    
                    full_path = os.path.join(root, file)
                    folder_name = os.path.basename(root)
                    
                    # Determine Category from parent structure
                    # Structure: apps/CATEGORY/APP_NAME/...
                    rel_path = os.path.relpath(root, apps_root)
                    parts = rel_path.split(os.sep)
                    
                    category = "APP"
                    if len(parts) >= 1 and parts[0] != ".":
                        category = parts[0].upper()
                    
                    # Smart Title
                    raw_title = file.replace(".bat", "")
                    title = raw_title.replace("_", " ")
                    
                    # If filename is generic (start, run, launch), use Folder Name
                    if raw_title in ["start", "run", "launch", "app", "main", "run_cli", "run_gui"]:
                         title = folder_name.replace("_", " ").upper()
                    elif raw_title.startswith("start_"):
                         title = raw_title.replace("start_", "").replace("_", " ").upper()
                    
                    # If title is still generic or same as category, add details
                    if title.replace(" ", "") == category.replace(" ", ""):
                         title = f"{folder_name.upper()}"

                    apps.append({
                        "title": title,
                        "category": category,
                        "desc": f"Located in: .../{folder_name}",
                        "path": full_path,
                        "color_idx": get_color_idx(category)
                    })
        
        # Sort: Root System first, then by Category, then Title
        apps.sort(key=lambda x: (0 if x['category'] == "ROOT SYSTEM" else 1, x['category'], x['title']))
        
        print(f"Loaded {len(apps)} apps.")
        return apps

    def load_books(self):
        books = []
        pattern = os.path.join(BOOKSHELF_DIR, "**/*.md")
        files = glob.glob(pattern, recursive=True)
        files.sort(key=os.path.getmtime, reverse=True)
        
        for f in files[:50]:
            name = os.path.basename(f).replace(".md", "")
            cat = "General"
            try:
                with open(f, 'r', encoding='utf-8') as fo:
                    txt = fo.read(500)
                    if "tags:" in txt:
                        m = re.search(r'tags:\s*\[(.*?)\]', txt)
                        if m: cat = m.group(1).replace("#","").replace(","," ")
            except: pass
            books.append({"title": name, "path": f, "category": cat, "type": "book"})
        return books

    def set_mode(self, mode):
        self.current_mode = mode
        if mode == "APPS":
            self.btn_apps.configure(fg_color="#3b82f6")
            self.btn_books.configure(fg_color="transparent")
        else:
            self.btn_apps.configure(fg_color="transparent")
            self.btn_books.configure(fg_color="#3b82f6")
        self.refresh_carousel()

    def refresh_carousel(self):
        if hasattr(self, 'carousel'): self.carousel.destroy()
        
        items = self.apps if self.current_mode == "APPS" else self.books
        if items:
            self.carousel = AnimatedCarousel(self.gallery_frame, items, self.handle_select)
            self.carousel.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(self.gallery_frame, text="No Items Available").pack(pady=100)

    def handle_select(self, item):
        if self.current_mode == "APPS":
            self.launch_app(item)
        else:
            self.open_reader(item)

    def launch_app(self, app_item):
        path = os.path.abspath(os.path.join(BASE_DIR, app_item['path']))
        if os.path.exists(path):
            try:
                # Use Start command to open in new independent window/terminal
                # shell=True with "start" on Windows
                subprocess.Popen(f'start "" "{path}"', shell=True)
                # No alert needed, visual feedback enough
            except Exception as e:
                messagebox.showerror("Launch Error", str(e))
        else:
            messagebox.showerror("Error", f"File not found: {path} \n(Base: {BASE_DIR})")

    def run_chaos_patrol(self):
        self.chaos_btn.configure(text="🚀 RUNNING...", state="disabled")
        
        def task():
            bat_path = os.path.abspath(os.path.join(BASE_DIR, "../../../../START_INTELLIGENCE_CHAOS.bat"))
            if os.path.exists(bat_path):
                subprocess.run([bat_path], shell=True)
                self.after(0, lambda: messagebox.showinfo("Patrol Complete", "Chaos Engine has finished."))
            else:
                self.after(0, lambda: messagebox.showerror("Error", "Launcher not found."))
            
            # If in Book mode, refresh
            if self.current_mode == "BOOKS":
                self.after(0, lambda: self.reload_books_and_refresh())
            else:
                self.after(0, lambda: self.reset_chaos_btn())

        threading.Thread(target=task).start()

    def reset_chaos_btn(self):
        self.chaos_btn.configure(text="⚡ START CHAOS PATROL", state="normal")

    def reload_books_and_refresh(self):
        self.books = self.load_books()
        self.refresh_carousel()
        self.reset_chaos_btn()


    def open_reader(self, book):
        if self.reader_window is None or not self.reader_window.winfo_exists():
            self.reader_window = ctk.CTkToplevel(self)
            self.reader_window.geometry("800x600")
            self.reader_window.title(book['title'])
            
            txt = ctk.CTkTextbox(self.reader_window, font=("Consolas", 14), wrap="word")
            txt.pack(fill="both", expand=True, padx=10, pady=10)
            
            try:
                with open(book['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    txt.insert("0.0", content)
            except Exception as e:
                txt.insert("0.0", f"Error reading file: {e}")
                
            txt.configure(state="disabled") # Read only
        else:
            self.reader_window.focus()

if __name__ == "__main__":
    app = BookshelfApp()
    app.mainloop()
