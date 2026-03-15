import tkinter as tk
from tkinter import ttk, messagebox
import base64

class Base64LoomApp:
    def __init__(self, master):
        self.master = master
        master.title("Base64 Loom (機密織機)")
        master.geometry("500x500")
        master.resizable(False, False)

        # Mode Selection
        mode_frame = ttk.Frame(master, padding="10")
        mode_frame.pack(fill=tk.X)

        self.mode_var = tk.StringVar(value="Encode")
        ttk.Radiobutton(mode_frame, text="Encode", variable=self.mode_var, value="Encode").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Decode", variable=self.mode_var, value="Decode").pack(side=tk.LEFT, padx=5)

        # Input Text Area
        ttk.Label(master, text="Input Text:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.input_text = tk.Text(master, height=10, width=60)
        self.input_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Processing Button
        ttk.Button(master, text="Processing", command=self.process_text).pack(pady=10)

        # Result Text Area
        ttk.Label(master, text="Result:").pack(padx=10, pady=(10, 0), anchor=tk.W)
        self.result_text = tk.Text(master, height=10, width=60, state='disabled')
        self.result_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def process_text(self):
        input_data = self.input_text.get("1.0", tk.END).strip()
        mode = self.mode_var.get()
        
        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        
        if not input_data:
            messagebox.showwarning("Input Missing", "Please enter some text to process.")
            self.result_text.config(state='disabled')
            return

        try:
            if mode == "Encode":
                res = base64.b64encode(input_data.encode('utf-8')).decode('utf-8')
            else: # Decode
                res = base64.b64decode(input_data).decode('utf-8')
            self.result_text.insert(tk.END, res)
        except Exception as e:
            messagebox.showerror("Processing Error", f"Error: {e}")
        
        self.result_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = Base64LoomApp(root)
    root.mainloop()
