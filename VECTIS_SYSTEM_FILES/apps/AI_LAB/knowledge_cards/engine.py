import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class CardEngine:
    def __init__(self, card_dir=os.path.join("outputs", "cards")):
        self.card_dir = card_dir
        if not os.path.exists(self.card_dir):
            os.makedirs(self.card_dir)

    def save_kcard(self, card_data):
        """Save card data as a .kcard JSON file."""
        if not card_data: return
        filename = f"{card_data['title'].replace(' ', '_')}_{card_data['timestamp'].replace(':', '-')}.kcard"
        path = os.path.join(self.card_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(card_data, f, ensure_ascii=False, indent=4)
        print(f"Card saved: {path}")
        return path

class CardViewerGUI:
    def __init__(self, card_dir="cards"):
        self.card_dir = card_dir
        self.root = tk.Tk()
        self.root.title("Vectis Knowledge Card Viewer")
        self.root.geometry("800x600")
        self.cards = []
        
        self.setup_ui()
        self.load_cards()
        
    def setup_ui(self):
        # Header / Filters
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="Timestamp")
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var, values=["Timestamp", "Rarity", "Genre"])
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display())

        # Main Display (Scrollable)
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.card_frame = tk.Frame(self.canvas)

        self.card_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.card_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_cards(self):
        self.cards = []
        if not os.path.exists(self.card_dir): return
        for f in os.listdir(self.card_dir):
            if f.endswith(".kcard"):
                with open(os.path.join(self.card_dir, f), "r", encoding="utf-8") as file:
                    self.cards.append(json.load(file))
        self.refresh_display()

    def refresh_display(self):
        # Clear frame
        for widget in self.card_frame.winfo_children():
            widget.destroy()
            
        sort_key = self.sort_var.get().lower()
        # Custom sort logic
        rarity_order = {"Legendary": 0, "Epic": 1, "Rare": 2, "Uncommon": 3, "Common": 4}
        if sort_key == "rarity":
            self.cards.sort(key=lambda x: rarity_order.get(x.get("rarity", "Common"), 99))
        elif sort_key == "timestamp":
            self.cards.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        else:
            self.cards.sort(key=lambda x: x.get(sort_key, ""))

        for card in self.cards:
            self.draw_card_ui(card)

    def draw_card_ui(self, card):
        frame = tk.Frame(self.card_frame, bd=2, relief=tk.RAISED, padx=10, pady=10, bg="#2e2e2e")
        frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Style based on rarity
        r_colors = {"Common": "white", "Uncommon": "#1eff00", "Rare": "#0070dd", "Epic": "#a335ee", "Legendary": "#ff8000"}
        color = r_colors.get(card.get("rarity"), "white")
        
        title_lbl = tk.Label(frame, text=card.get("title"), font=("Arial", 14, "bold"), fg=color, bg="#2e2e2e")
        title_lbl.pack(anchor="w")
        
        info_lbl = tk.Label(frame, text=f"{card.get('genre')} | {card.get('rarity')} | {card.get('timestamp')}", fg="gray", bg="#2e2e2e")
        info_lbl.pack(anchor="w")
        
        content_lbl = tk.Label(frame, text=card.get("content"), wraplength=700, justify=tk.LEFT, fg="white", bg="#2e2e2e", pady=5)
        content_lbl.pack(anchor="w")
        
        src_lbl = tk.Label(frame, text=f"Source: {card.get('source')}", font=("Arial", 8, "italic"), fg="lightblue", bg="#2e2e2e")
        src_lbl.pack(anchor="w")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Test UI
    viewer = CardViewerGUI()
    viewer.run()
