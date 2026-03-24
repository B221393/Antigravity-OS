import tkinter as tk
from tkinter import ttk
import uuid

class UUIDForgeApp:
    def __init__(self, master):
        self.master = master
        master.title("UUID Forge (識別子工房)")
        master.geometry("400x400") # Set initial window size

        # Count input
        self.count_label = ttk.Label(master, text="Count:")
        self.count_label.pack(pady=5)
        self.count_var = tk.IntVar(value=5)
        self.count_spinbox = ttk.Spinbox(master, from_=1, to=100, textvariable=self.count_var)
        self.count_spinbox.pack(pady=5)

        # Version input
        self.version_label = ttk.Label(master, text="Version:")
        self.version_label.pack(pady=5)
        self.version_var = tk.IntVar(value=4)
        self.version_combobox = ttk.Combobox(master, textvariable=self.version_var, values=[4, 1], state="readonly")
        self.version_combobox.pack(pady=5)
        self.version_combobox.set(4) # Default value

        # Forge button
        self.forge_button = ttk.Button(master, text="Forge", command=self.generate_uuids)
        self.forge_button.pack(pady=10)

        # Result text area
        self.result_label = ttk.Label(master, text="Result:")
        self.result_label.pack(pady=5)
        self.result_text = tk.Text(master, height=10, width=40)
        self.result_text.pack(pady=5)

    def generate_uuids(self):
        count = self.count_var.get()
        version = self.version_var.get()
        
        out = ""
        for _ in range(count):
            if version == 4:
                u = uuid.uuid4()
            else: # version == 1
                u = uuid.uuid1()
            out += str(u) + "\n"
        
        self.result_text.delete(1.0, tk.END) # Clear previous content
        self.result_text.insert(tk.END, out) # Insert new content

if __name__ == "__main__":
    root = tk.Tk()
    app = UUIDForgeApp(root)
    root.mainloop()
