import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

class PasswordForgeApp:
    def __init__(self, master):
        self.master = master
        master.title("Password Forge")
        master.geometry("450x450") # Set initial window size
        master.resizable(False, False) # Disable resizing

        # --- Settings Frame ---
        settings_frame = ttk.LabelFrame(master, text="Settings")
        settings_frame.pack(padx=10, pady=10, fill=tk.X)

        # Length Slider
        ttk.Label(settings_frame, text="Length:").pack(padx=5, pady=2, anchor=tk.W)
        self.length_var = tk.IntVar(value=16)
        self.length_scale = ttk.Scale(settings_frame, from_=8, to=64, orient=tk.HORIZONTAL,
                                      variable=self.length_var, command=self._update_length_label)
        self.length_scale.pack(padx=5, pady=2, fill=tk.X)
        self.length_label = ttk.Label(settings_frame, text=f"Current Length: {self.length_var.get()}")
        self.length_label.pack(padx=5, pady=2, anchor=tk.W)

        # Character Type Checkboxes
        self.use_upper_var = tk.BooleanVar(value=True)
        self.use_lower_var = tk.BooleanVar(value=True)
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_symbols_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(settings_frame, text="A-Z Uppercase", variable=self.use_upper_var).pack(padx=5, pady=2, anchor=tk.W)
        ttk.Checkbutton(settings_frame, text="a-z Lowercase", variable=self.use_lower_var).pack(padx=5, pady=2, anchor=tk.W)
        ttk.Checkbutton(settings_frame, text="0-9 Digits", variable=self.use_digits_var).pack(padx=5, pady=2, anchor=tk.W)
        ttk.Checkbutton(settings_frame, text="!@#$ Symbols", variable=self.use_symbols_var).pack(padx=5, pady=2, anchor=tk.W)

        # Forge Button
        ttk.Button(master, text="🔨 Forge Password", command=self.generate_password_ui).pack(pady=10)

        # --- Result Frame ---
        result_frame = ttk.LabelFrame(master, text="Generated Password")
        result_frame.pack(padx=10, pady=10, fill=tk.X)

        self.generated_password_var = tk.StringVar()
        self.password_entry = ttk.Entry(result_frame, textvariable=self.generated_password_var, state='readonly', font=('Courier', 10))
        self.password_entry.pack(padx=5, pady=5, fill=tk.X)

        self.password_length_label = ttk.Label(result_frame, text="Length: 0 chars")
        self.password_length_label.pack(padx=5, pady=2, anchor=tk.W)

        self.strength_label = ttk.Label(result_frame, text="Strength: Unknown")
        self.strength_label.pack(padx=5, pady=2, anchor=tk.W)

        # Security Note
        ttk.Label(master, text="Passwords are generated locally on your machine.\nNo data is sent to any server.",
                  font=('Arial', 8), foreground='gray').pack(pady=5)

    def _update_length_label(self, event=None):
        self.length_label.config(text=f"Current Length: {self.length_var.get()}")

    def generate_password_ui(self):
        password = self._generate_password()
        self.generated_password_var.set(password)
        self.password_length_label.config(text=f"Length: {len(password)} chars")
        self._update_strength_label(password)

    def _generate_password(self):
        chars = ""
        if self.use_upper_var.get(): chars += string.ascii_uppercase
        if self.use_lower_var.get(): chars += string.ascii_lowercase
        if self.use_digits_var.get(): chars += string.digits
        if self.use_symbols_var.get(): chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not chars:
            messagebox.showwarning("Selection Error", "Please select at least one character type.")
            return ""
            
        length = self.length_var.get()
        return "".join(random.choice(chars) for _ in range(length))

    def _update_strength_label(self, password):
        if not password:
            self.strength_label.config(text="Strength: Unknown", foreground='black')
        elif len(password) < 12:
            self.strength_label.config(text="Strength: Weak (Too short)", foreground='red')
        elif len(password) < 16:
            self.strength_label.config(text="Strength: Good", foreground='orange')
        else:
            self.strength_label.config(text="Strength: Excellent (Strong)", foreground='green')

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordForgeApp(root)
    root.mainloop()
