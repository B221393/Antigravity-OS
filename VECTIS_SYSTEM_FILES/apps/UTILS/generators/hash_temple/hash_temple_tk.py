import tkinter as tk
from tkinter import ttk
import hashlib

class HashTempleApp:
    def __init__(self, master):
        self.master = master
        master.title("Hash Temple (ハッシュ寺院)")
        master.geometry("500x350")
        master.resizable(False, False)

        # Input Frame
        input_frame = ttk.Frame(master, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Enter String:").pack(side=tk.LEFT, padx=(0, 10))
        self.text_input_var = tk.StringVar()
        self.text_input_var.trace_add("write", self.update_hashes)
        self.text_entry = ttk.Entry(input_frame, textvariable=self.text_input_var, width=50)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Hashes Display Frame
        hashes_frame = ttk.LabelFrame(master, text="Hashes", padding="10")
        hashes_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.hash_vars = {}
        hash_types = ["MD5", "SHA1", "SHA256", "SHA512"]
        for hash_type in hash_types:
            row_frame = ttk.Frame(hashes_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{hash_type}:", width=8, anchor=tk.W).pack(side=tk.LEFT)
            hash_var = tk.StringVar()
            ttk.Entry(row_frame, textvariable=hash_var, state='readonly', font=('Courier', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.hash_vars[hash_type] = hash_var

    def update_hashes(self, *args):
        txt = self.text_input_var.get()
        if txt:
            b = txt.encode('utf-8')
            self.hash_vars["MD5"].set(hashlib.md5(b).hexdigest())
            self.hash_vars["SHA1"].set(hashlib.sha1(b).hexdigest())
            self.hash_vars["SHA256"].set(hashlib.sha256(b).hexdigest())
            self.hash_vars["SHA512"].set(hashlib.sha512(b).hexdigest())
        else:
            for hash_var in self.hash_vars.values():
                hash_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = HashTempleApp(root)
    root.mainloop()
