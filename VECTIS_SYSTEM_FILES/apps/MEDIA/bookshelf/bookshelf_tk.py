import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ScrolledFrame, ScrolledText
import json
import os
import uuid
from datetime import datetime

# TODO: Make this path configurable
HISTORY_FILE = "c:\\Users\\Yuto\\Desktop\\app\\s_history.json"

class AddBookWindow(ttk.Toplevel):
    def __init__(self, master, app_instance):
        super().__init__(title="Add New Book", master=master)
        self.app = app_instance
        self.geometry("600x700")

        # Form Fields
        form_frame = ttk.Frame(self, padding=15)
        form_frame.pack(fill=BOTH, expand=YES)
        form_frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        # Genre
        ttk.Label(form_frame, text="Genre:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.genre_entry = ttk.Entry(form_frame)
        self.genre_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        # Content
        ttk.Label(form_frame, text="Content:").grid(row=2, column=0, sticky=NW, padx=5, pady=5)
        self.content_text = ScrolledText(form_frame, height=20, autohide=True)
        self.content_text.grid(row=2, column=1, sticky=NSEW, padx=5, pady=5)
        form_frame.rowconfigure(2, weight=1)

        # Save Button
        save_button = ttk.Button(form_frame, text="Save Book", command=self.save_book, bootstyle="success")
        save_button.grid(row=3, column=1, sticky=E, padx=5, pady=10)

    def save_book(self):
        new_book = {
            "id": str(uuid.uuid4()),
            "source": self.title_entry.get() or "Untitled",
            "group": self.genre_entry.get() or "General",
            "content": self.content_text.get("1.0", END).strip(),
            "timestamp": datetime.now().isoformat()
        }
        self.app.add_book(new_book)
        self.destroy()

class BookshelfApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        self.books = []
        
        # --- Main Layout ---
        header_frame = self.create_header()
        header_frame.pack(fill=X, pady=(0, 10))

        self.bookshelf_frame = ScrolledFrame(self, autohide=True)
        self.bookshelf_frame.pack(fill=BOTH, expand=YES)

        self.load_and_display_books()

    def create_header(self):
        frame = ttk.Frame(self)
        header = ttk.Label(frame, text="🌌 Cosmic Library Bookshelf", font="-size 20 -weight bold")
        header.pack(side=LEFT, anchor=W)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=RIGHT)
        
        add_btn = ttk.Button(button_frame, text="+ Add New", command=self.open_add_book_window, bootstyle="success")
        add_btn.pack(side=RIGHT, padx=5)

        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.load_and_display_books, bootstyle="secondary")
        refresh_btn.pack(side=RIGHT, padx=5)
        
        return frame
    
    def open_add_book_window(self):
        AddBookWindow(self.master, self)

    def add_book(self, book):
        self.books.append(book)
        self.save_data_to_json()
        self.load_and_display_books()
        
    def load_and_display_books(self):
        # Clear existing widgets
        for widget in self.bookshelf_frame.winfo_children():
            widget.destroy()

        self.load_data_from_json()
        if not self.books:
            ttk.Label(self.bookshelf_frame, text="No books found. Click '+ Add New' to start.", bootstyle="info").pack(pady=20)
            return

        # Display books in reverse chronological order (most recent first)
        sorted_books = sorted(self.books, key=lambda b: b.get('timestamp', ''), reverse=True)
        for book in sorted_books:
            card = self.create_book_card(self.bookshelf_frame, book)
            card.pack(fill=X, padx=10, pady=5)
    
    def load_data_from_json(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.books = data.get("nodes", [])
            except (json.JSONDecodeError, TypeError):
                print(f"Warning: Could not decode or parse JSON from {HISTORY_FILE}. Starting fresh.")
                self.books = []
        else:
            self.books = []
            
    def save_data_to_json(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({"nodes": self.books}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")

    def create_book_card(self, parent, book_data):
        card_frame = ttk.Frame(parent, bootstyle="light", padding=15)
        
        genre = book_data.get('group', 'GENERAL').upper()
        title = book_data.get('source', 'Untitled')
        content = book_data.get('content', '').replace('#', '').strip()
        summary = content[:200] + "..." if len(content) > 200 else content

        genre_label = ttk.Label(card_frame, text=genre, bootstyle="secondary")
        genre_label.pack(fill=X, anchor=W)
        
        title_label = ttk.Label(card_frame, text=title, font="-size 14 -weight bold", bootstyle="primary")
        title_label.pack(fill=X, anchor=W, pady=(5, 10))
        
        summary_label = ttk.Label(card_frame, text=summary, wraplength=parent.winfo_width() - 50, justify=LEFT)
        summary_label.pack(fill=X, anchor=W)

        return card_frame

if __name__ == '__main__':
    app = ttk.Window("Cosmic Library Bookshelf", "cosmo", resizable=(True, True))
    app.geometry("700x800")
    BookshelfApp(app)
    app.mainloop()
