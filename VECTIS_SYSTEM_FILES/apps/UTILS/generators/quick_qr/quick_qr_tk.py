import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
import qrcode
from PIL import Image, ImageTk
from io import BytesIO

class QuickQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Quick QR Generator")
        
        self.img = None # To hold the QR code PIL Image object

        # --- Widgets ---
        
        # Data Input
        ttk.Label(master, text="Enter URL or Text:").pack(padx=10, pady=5, anchor=tk.W)
        self.data_var = tk.StringVar(value="https://www.example.com")
        ttk.Entry(master, textvariable=self.data_var, width=50).pack(padx=10, pady=5, fill=tk.X)

        # Color Pickers
        color_frame = ttk.Frame(master)
        color_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.fill_color = tk.StringVar(value="#000000")
        self.back_color = tk.StringVar(value="#FFFFFF")

        ttk.Button(color_frame, text="Fill Color", command=self.choose_fill_color).pack(side=tk.LEFT, expand=True, padx=5)
        self.fill_color_label = ttk.Label(color_frame, text=self.fill_color.get(), width=10, relief="solid", anchor=tk.CENTER)
        self.fill_color_label.pack(side=tk.LEFT, expand=True, padx=5)
        
        ttk.Button(color_frame, text="Background Color", command=self.choose_back_color).pack(side=tk.LEFT, expand=True, padx=5)
        self.back_color_label = ttk.Label(color_frame, text=self.back_color.get(), width=10, relief="solid", anchor=tk.CENTER)
        self.back_color_label.pack(side=tk.LEFT, expand=True, padx=5)


        # Generate Button
        ttk.Button(master, text="Generate QR", command=self.generate_qr).pack(padx=10, pady=10)

        # QR Code Display
        self.qr_label = ttk.Label(master, text="QR Code will appear here", anchor=tk.CENTER)
        self.qr_label.pack(padx=10, pady=10)
        
        # Save Button
        self.save_button = ttk.Button(master, text="Save Image...", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(padx=10, pady=5)


    def choose_fill_color(self):
        color_code = colorchooser.askcolor(title="Choose fill color", initialcolor=self.fill_color.get())
        if color_code[1]:
            self.fill_color.set(color_code[1])
            self.fill_color_label.config(text=color_code[1])

    def choose_back_color(self):
        color_code = colorchooser.askcolor(title="Choose background color", initialcolor=self.back_color.get())
        if color_code[1]:
            self.back_color.set(color_code[1])
            self.back_color_label.config(text=color_code[1])

    def generate_qr(self):
        data = self.data_var.get()
        if not data:
            tk.messagebox.showwarning("Input Missing", "Please enter some text or a URL.")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        self.img = qr.make_image(fill_color=self.fill_color.get(), back_color=self.back_color.get())
        
        # Convert for Tkinter
        tk_img = ImageTk.PhotoImage(self.img)
        
        self.qr_label.config(image=tk_img)
        self.qr_label.image = tk_img # Keep a reference!
        
        self.save_button.config(state=tk.NORMAL)

    def save_image(self):
        if not self.img:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile="qrcode.png",
            title="Save QR Code as..."
        )
        if file_path:
            self.img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickQRApp(root)
    root.mainloop()
