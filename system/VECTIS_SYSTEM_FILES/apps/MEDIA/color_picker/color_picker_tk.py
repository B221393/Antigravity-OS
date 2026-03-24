import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import colorchooser

class ColorPickerApp:
    def __init__(self, master):
        self.master = master
        master.title("Color Picker (色彩採取)")
        master.geometry("350x300") # Increased height for better spacing
        master.resizable(False, False)

        # Color Display Frame
        self.color_frame = ttk.Frame(master, bootstyle="primary", width=100, height=50) # Use ttk.Frame
        self.color_frame.pack(pady=10)

        # Pick Color Button
        ttk.Button(master, text="Pick Color", command=self.pick_color, bootstyle="primary").pack(pady=5)

        # Hex Code
        ttk.Label(master, text="Hex:").pack(pady=(10,0))
        self.hex_entry = ttk.Entry(master, textvariable=ttk.StringVar(value="#00A8E8"), state='readonly', width=15, justify=CENTER)
        self.hex_entry.pack()

        # RGB Tuple
        ttk.Label(master, text="RGB:").pack(pady=(10,0))
        self.rgb_entry = ttk.Entry(master, textvariable=ttk.StringVar(value="(0, 168, 232)"), state='readonly', width=20, justify=CENTER)
        self.rgb_entry.pack()

        # CSS RGB
        ttk.Label(master, text="CSS:").pack(pady=(10,0))
        self.css_entry = ttk.Entry(master, textvariable=ttk.StringVar(value="rgb(0, 168, 232)"), state='readonly', width=25, justify=CENTER)
        self.css_entry.pack()
        
        self.update_color_display("#00A8E8") # Initial display

    def pick_color(self):
        # Initial color for the color chooser should come from the current hex_entry value
        initial_color = self.hex_entry.get()
        color_code = colorchooser.askcolor(title="Pick a color", initialcolor=initial_color)
        if color_code[1]: # color_code[1] is the hex string
            self.update_color_display(color_code[1])

    def update_color_display(self, hex_color):
        self.hex_entry.config(state='normal')
        self.hex_entry.delete(0, END)
        self.hex_entry.insert(0, hex_color)
        self.hex_entry.config(state='readonly')

        self.color_frame.config(bootstyle=f"primary.{hex_color}") # Use bootstyle for background

        # Convert hex to RGB
        hex_color_stripped = hex_color.lstrip('#')
        rgb_tuple = tuple(int(hex_color_stripped[i:i+2], 16) for i in (0, 2, 4))
        
        self.rgb_entry.config(state='normal')
        self.rgb_entry.delete(0, END)
        self.rgb_entry.insert(0, str(rgb_tuple))
        self.rgb_entry.config(state='readonly')

        self.css_entry.config(state='normal')
        self.css_entry.delete(0, END)
        self.css_entry.insert(0, f"rgb{rgb_tuple}")
        self.css_entry.config(state='readonly')

if __name__ == "__main__":
    root = ttk.Window(themename="cosmo") # Use ttk.Window
    app = ColorPickerApp(root)
    root.mainloop()
