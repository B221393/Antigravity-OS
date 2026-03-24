import customtkinter as ctk
import sys
import os
import threading
import subprocess

# Path configuration to reach shared modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(project_root)

# Try importing the UnifiedLLM (Phi-4 wrapper)
try:
    from modules.unified_llm import UnifiedLLM
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# --- CONFIGURATION & CONSTANTS ---
THEME_COLOR = "green"  # Options: "blue", "green", "dark-blue"
APPEARANCE_MODE = "Dark" 

class OmniDevStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("OMNI DEV STUDIO [Prototyping Environment]")
        self.geometry("1400x900")
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(THEME_COLOR)

        # Initialize Brain (Phi-4)
        if LLM_AVAILABLE:
            self.llm = UnifiedLLM(provider="ollama", model_name="phi4")
        else:
            self.llm = None

        # --- LAYOUT CONFIGURATION ---
        # Grid: 
        # Column 0: Sidebar (Tools/Files)
        # Column 1: Main Workspace (Code Editor / Canvas)
        # Column 2: AI Co-pilot Panel (Phi-4 Interaction)
        
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.grid_columnconfigure(1, weight=3)  # Workspace expands
        self.grid_columnconfigure(2, weight=1)  # AI Panel fixed/resizable
        self.grid_rowconfigure(0, weight=1)

        # -----------------------------
        # 1. SIDEBAR (Project Management)
        # -----------------------------
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="DEV STUDIO", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(fill="x", padx=20, pady=20)
        
        self.btn_new_project = ctk.CTkButton(self.sidebar, text="+ New Project")
        self.btn_new_project.pack(fill="x", padx=20, pady=10)
        
        self.lbl_explorer = ctk.CTkLabel(self.sidebar, text="EXPLORER", anchor="w")
        self.lbl_explorer.pack(fill="x", padx=20, pady=(20, 5))
        
        # Placeholder for file tree
        self.file_tree_frame = ctk.CTkScrollableFrame(self.sidebar, height=400, fg_color="transparent")
        self.file_tree_frame.pack(fill="both", expand=True, padx=10)
        
        # Dummy Files
        for i in range(5):
            btn = ctk.CTkButton(self.file_tree_frame, text=f"module_{i}.py", fg_color="transparent", border_width=1, anchor="w", text_color="#aaa")
            btn.pack(fill="x", pady=2)

        # -----------------------------
        # 2. MAIN WORKSPACE (The Creator)
        # -----------------------------
        self.workspace = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a") # Slightly different bg
        self.workspace.grid(row=0, column=1, sticky="nsew")
        
        # Tabview for Editor
        self.editor_tabs = ctk.CTkTabview(self.workspace)
        self.editor_tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_1 = self.editor_tabs.add("app.py")
        tab_2 = self.editor_tabs.add("style.css")
        
        # Code Editor Area (Textbox)
        self.code_editor = ctk.CTkTextbox(tab_1, font=("Consolas", 14), wrap="none", fg_color="#111", text_color="#eee")
        self.code_editor.pack(fill="both", expand=True)
        self.code_editor.insert("0.0", "# Welcome to Omni Dev Studio\n# Start coding your next big idea here.\n\ndef main():\n    print('Hello World')\n")

        # -----------------------------
        # 3. AI CO-PILOT PANEL (Right Side)
        # -----------------------------
        self.ai_panel = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.ai_panel.grid(row=0, column=2, sticky="nsew")
        self.ai_panel.grid_rowconfigure(1, weight=1) # Chat history expands
        
        self.ai_header = ctk.CTkLabel(self.ai_panel, text="PHI-4 CO-PILOT", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2b2b2b")
        self.ai_header.grid(row=0, column=0, sticky="ew", padx=0, pady=0, ipady=10)
        
        # Chat History
        self.chat_history = ctk.CTkTextbox(self.ai_panel, font=("Segoe UI", 12), wrap="word", fg_color="transparent")
        self.chat_history.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_history.insert("0.0", "AI: I am ready to assist with your development logic. Ask me anything about Python, UI design, or architecture.\n\n")
        self.chat_history.configure(state="disabled") # Read-only initially
        
        # Input Area
        self.chat_input_frame = ctk.CTkFrame(self.ai_panel, height=60, fg_color="transparent")
        self.chat_input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.chat_entry = ctk.CTkEntry(self.chat_input_frame, placeholder_text="Ask Phi-4...", height=40)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.chat_entry.bind("<Return>", self.send_ai_message)
        
        self.chat_send_btn = ctk.CTkButton(self.chat_input_frame, text="➤", width=40, height=40, command=self.send_ai_message)
        self.chat_send_btn.pack(side="right")

    def send_ai_message(self, event=None):
        user_text = self.chat_entry.get()
        if not user_text.strip():
            return
            
        self.chat_entry.delete(0, 'end')
        self.append_chat(f"YOU: {user_text}")
        
        # Run AI processing in background thread
        threading.Thread(target=self.process_ai_response, args=(user_text,), daemon=True).start()

    def process_ai_response(self, user_text):
        if not self.llm:
            self.append_chat("SYSTEM: LLM Module not found.")
            return
            
        try:
            # Contextual Prompting for Development
            system_prompt = f"""[Role: Senior Developer Assistant]
The user is building an application. Answer technically and concisely.
User Query: {user_text}"""
            
            response = self.llm.generate(system_prompt)
            self.append_chat(f"PHI-4: {response}")
        except Exception as e:
            self.append_chat(f"SYSTEM_ERROR: {str(e)}")

    def append_chat(self, text):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", text + "\n\n")
        self.chat_history.see("end")
        self.chat_history.configure(state="disabled")

if __name__ == "__main__":
    app = OmniDevStudio()
    app.mainloop()
