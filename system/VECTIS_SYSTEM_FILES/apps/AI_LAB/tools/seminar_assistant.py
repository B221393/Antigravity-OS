import tkinter as tk
from tkinter import ttk, scrolledtext
import glob
import os

# Configuration
DOCS_DIR = r"c:\Users\Yuto\.gemini\antigravity\brain\f73fd1ff-5770-4bcc-af9e-6068c7e2ba4a"
MD_FILES = ["seminar_cheat_sheet.md", "interview_qa_db.md", "seminar_prep_brexa_meitec.md"]

class SeminarAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seminar Assistant")
        self.root.geometry("500x700")
        self.root.attributes('-topmost', True)  # Always on top by default
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header Frame
        header_frame = ttk.Frame(root)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Toggle Topmost Button
        self.is_topmost = True
        self.topmost_btn = ttk.Button(header_frame, text="📌 On Top: ON", command=self.toggle_topmost)
        self.topmost_btn.pack(side=tk.LEFT)
        
        # Search Bar
        ttk.Label(header_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=(10, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_content)
        self.search_entry = ttk.Entry(header_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.text_widgets = {}
        self.file_contents = {}
        
        # Load Files
        self.load_documents()

    def load_documents(self):
        for filename in MD_FILES:
            filepath = os.path.join(DOCS_DIR, filename)
            if os.path.exists(filepath):
                tab_name = filename.replace(".md", "")
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=tab_name)
                
                text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Consolas", 10))
                text_area.pack(fill=tk.BOTH, expand=True)
                
                # Tag configuration for highlighting
                text_area.tag_config("highlight", background="yellow", foreground="black")
                text_area.tag_config("header", foreground="blue", font=("Consolas", 11, "bold"))
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.file_contents[tab_name] = content
                        self.render_markdown(text_area, content)
                except Exception as e:
                    text_area.insert(tk.END, f"Error loading file: {e}")
                
                # Make read-only
                text_area.config(state=tk.DISABLED)
                self.text_widgets[tab_name] = text_area

    def render_markdown(self, widget, content):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        
        for line in content.splitlines():
            if line.strip().startswith("#"):
                widget.insert(tk.END, line + "\n", "header")
            else:
                widget.insert(tk.END, line + "\n")
        
        widget.config(state=tk.DISABLED)

    def filter_content(self, *args):
        query = self.search_var.get().lower()
        
        for tab_name, text_widget in self.text_widgets.items():
            content = self.file_contents.get(tab_name, "")
            
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)
            
            if not query:
                self.render_markdown(text_widget, content)
            else:
                # Simple line-based filtering
                filtered_lines = []
                for line in content.splitlines():
                    # Keep headers for context or if they match
                    if line.strip().startswith("#"):
                        filtered_lines.append((line, "header"))
                    elif query in line.lower():
                        filtered_lines.append((line, "highlight"))
                
                for line, tag in filtered_lines:
                    text_widget.insert(tk.END, line + "\n", tag if tag == "header" or query in line.lower() else "")
            
            text_widget.config(state=tk.DISABLED)

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)
        self.topmost_btn.config(text=f"📌 On Top: {'ON' if self.is_topmost else 'OFF'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SeminarAssistantApp(root)
    root.mainloop()
