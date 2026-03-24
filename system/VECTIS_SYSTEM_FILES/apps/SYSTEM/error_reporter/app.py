import customtkinter as ctk
import os
import datetime
import sys

# CONFIG
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

FONT_MONO = ("Consolas", 12)
BRIDGE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AI_CONTEXT_BRIDGE.md"))

class ErrorReporter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VECTIS BUG REPORT")
        self.geometry("600x500")
        
        # Header
        self.lbl = ctk.CTkLabel(self, text="⚠️ SYSTEM ERROR RELAY", font=("Arial", 20, "bold"), text_color="#ff5555")
        self.lbl.pack(pady=10)
        
        self.lbl_sub = ctk.CTkLabel(self, text="Paste raw error logs below. Antigravity will analyze them.", text_color="gray")
        self.lbl_sub.pack()
        
        # Text Area
        self.txt_error = ctk.CTkTextbox(self, font=FONT_MONO, fg_color="#1a1a1a", text_color="#f0f0f0", height=300)
        self.txt_error.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="CLEAR", fg_color="#333", command=self.clear_text)
        self.btn_clear.pack(side="left")
        
        self.btn_send = ctk.CTkButton(btn_frame, text="🚀 SEND TO ARCHITECT", fg_color="#ff5555", text_color="#fff", 
                                      font=("Arial", 12, "bold"), command=self.send_report)
        self.btn_send.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Status
        self.lbl_status = ctk.CTkLabel(self, text="READY", text_color="#555")
        self.lbl_status.pack(pady=(0, 10))

    def clear_text(self):
        self.txt_error.delete("0.0", "end")
        self.lbl_status.configure(text="CLEARED", text_color="#555")

    def send_report(self):
        error_content = self.txt_error.get("0.0", "end").strip()
        if not error_content:
            self.lbl_status.configure(text="EMPTY REPORT IGNORED", text_color="yellow")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_block = f"""
## 🐞 USER BUG REPORT [{timestamp}]
```text
{error_content}
```
---
"""
        try:
            # Append to Bridge File
            with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
                f.write(report_block)
            
            self.lbl_status.configure(text="✅ REPORT SAVED TO AI_CONTEXT_BRIDGE", text_color="#0f0")
            self.txt_error.delete("0.0", "end")
            self.txt_error.insert("0.0", ">> REPORT SENT SUCCESSFULLY.\n>> THE ARCHITECT WILL REVIEW THIS ON NEXT SESSION.")
        except Exception as e:
            self.lbl_status.configure(text=f"SAVE FAILED: {e}", text_color="red")

if __name__ == "__main__":
    app = ErrorReporter()
    app.mainloop()
