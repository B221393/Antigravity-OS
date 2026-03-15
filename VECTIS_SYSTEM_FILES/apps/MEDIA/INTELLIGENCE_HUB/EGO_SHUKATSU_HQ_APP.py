import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import glob
from datetime import datetime

# --- Configuration ---
# C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\youtube_channel\EGO_SHUKATSU_HQ_APP.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = r"C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data"
ES_TRACKER_FILE = os.path.join(DATA_DIR, "es_tracker_data.json")

# Data is actually inside the local data dir of the app
SHUKATSU_DATA_DIR = os.path.join(BASE_DIR, "data", "shukatsu")
os.makedirs(SHUKATSU_DATA_DIR, exist_ok=True)

# Professional Light Theme (Clean, Trustworthy)
THEME = {
    'bg': '#ffffff',             # Pure White
    'surface': '#f3f4f6',        # Light Gray (Off-white)
    'text': '#1f2937',           # Dark Gray/Black (High Contrast)
    'text_dim': '#6b7280',       # Medium Gray
    'accent': '#2563eb',         # Professional Blue
    'success': '#059669',        # Green
    'warning': '#d97706',        # Orange
    'error': '#dc2626',          # Red
    'kanban_bg': '#e5e7eb'       # Slightly darker gray for canvas
}

# Expanded Recommendations (Major / Ote)
RECOMMENDATIONS_OTE = [
    # Top Tier / Conglomerates
    {"name": "Toyota Motor", "industry": "Automotive", "reason": "Global top manufacturer, massive R&D budget, stable."},
    {"name": "Sony Group", "industry": "Conglomerate", "reason": "Diverse portfolio (Game, Image Sensor, Finance, Music). Creative culture."},
    {"name": "Mitsubishi Corp", "industry": "Trading", "reason": "Top Sogo Shosha. Energy, Retail (Lawson), wide global reach."},
    {"name": "Itochu", "industry": "Trading", "reason": "Strong in non-resource sectors (Textile, Food, IT). Morning-focused work style."},
    {"name": "Hitachi", "industry": "IT/Infrastructure", "reason": "Social Innovation leader. IoT (Lumada) & heavy machinery."},
    
    # Telecom / IT
    {"name": "KDDI", "industry": "Telecom", "reason": "Au carrier business + Life Design (Finance/Energy) + IoT."},
    {"name": "NTT Data", "industry": "IT (SIer)", "reason": "Top Japanese SIer. Government systems, stable, large scale."},
    {"name": "SoftBank Group", "industry": "Investment/Tech", "reason": "AI strategy focus. Fast-paced, aggressive growth."},
    {"name": "Nomura Research (NRI)", "industry": "Consulting/IT", "reason": "High profit margins. Strategic consulting + system implementation."},
    {"name": "Keyence", "industry": "Manufacturer", "reason": "Highest average salary in Japan. Consultative sales model."},
    
    # Finance
    {"name": "Tokio Marine & Nichido", "industry": "Insurance", "reason": "Top P&C insurer. Global acquisitions, strong leadership brand."},
    {"name": "Mitsubishi UFJ (MUFG)", "industry": "Bank", "reason": "Megabank leader. Global network, digital banking transformation."},
    {"name": "Sumitomo Mitsui (SMBC)", "industry": "Bank", "reason": "Efficiency focused. Individual performance valued."},
    
    # Manufacturers / B2B
    {"name": "Fujifilm", "industry": "Chemical/Medical", "reason": "Successful pivot from film to healthcare/cosmetics."},
    {"name": "Daikin", "industry": "Machinery", "reason": "Global No.1 in AC. High overseas sales ratio."},
    {"name": "Murata Mfg", "industry": "Electronic Parts", "reason": "Essential components for smartphones (Top market share)."},
    
    # Infrastructure / Real Estate
    {"name": "JR East", "industry": "Transportation", "reason": "Dominant railway network + Suica/Real Estate business."},
    {"name": "Mitsui Fudosan", "industry": "Real Estate", "reason": "Top developer. Urban redevelopment (Nihonbashi), stable asset income."},
    {"name": "Mitsubishi Estate", "industry": "Real Estate", "reason": "Marunouchi ownership (strongest office area). Reliable."},
    
    # Consumer / Services
    {"name": "Nintendo", "industry": "Game", "reason": "Unrivaled IP strength. High profit margin, cash rich."},
    {"name": "Fast Retailing (Uniqlo)", "industry": "Retail", "reason": "Global apparel giant. Meritocracy, global career path."},
    {"name": "Oriental Land (Disney)", "industry": "Leisure", "reason": "Tokyo Disney Resort operator. unmatched brand power."},
    {"name": "Recruit", "industry": "Services/IT", "reason": "Entrepreneurial spirit. 'Rikunabi', 'Suumo', 'HotPepper'."},
    
    # Food / Pharma
    {"name": "Suntory", "industry": "Food/Beverage", "reason": "Global beverage player (Beam Suntory). 'Yatted minahare' spirit."},
    {"name": "Ajinomoto", "industry": "Food/Chemical", "reason": "Amino science leader. Semiconductor materials business is also strong."},
    {"name": "Chugai Pharma", "industry": "Pharma", "reason": "Roche group alliance. Strong antibody drug pipeline."}
]

class ShukatsuHQ(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ EGO SHUKATSU HQ - Intelligence & Operations")
        self.geometry("1100x800")
        self.configure(bg=THEME['bg'])
        
        self.load_tracker_data()
        
        # Tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=THEME['bg'], borderwidth=0)
        style.configure("TNotebook.Tab", background=THEME['surface'], foreground=THEME['text_dim'], padding=[15, 5], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab", background=[('selected', THEME['accent'])], foreground=[('selected', '#ffffff')])
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tab_dashboard = tk.Frame(self.notebook, bg=THEME['bg'])
        self.tab_tracker = tk.Frame(self.notebook, bg=THEME['bg'])
        self.tab_research = tk.Frame(self.notebook, bg=THEME['bg'])
        self.tab_recs = tk.Frame(self.notebook, bg=THEME['bg'])
        
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self.notebook.add(self.tab_tracker, text="📝 ES Tracker")
        self.notebook.add(self.tab_recs, text="🏆 Picks") 
        self.notebook.add(self.tab_research, text="🏢 Research")
        
        # Init Tabs
        self.setup_dashboard()
        self.setup_tracker()
        self.setup_recs()
        self.setup_research()
        
    def load_tracker_data(self):
        if os.path.exists(ES_TRACKER_FILE):
             try:
                 with open(ES_TRACKER_FILE, 'r', encoding='utf-8') as f:
                     self.tracker_data = json.load(f)
             except:
                 self.tracker_data = {"columns": ["Drafting", "Review", "Submitted", "Interview", "Offer"], "tasks": []}
        else:
             self.tracker_data = {"columns": ["Drafting", "Review", "Submitted", "Interview", "Offer"], "tasks": []}

    def save_tracker_data(self):
        with open(ES_TRACKER_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tracker_data, f, indent=4, ensure_ascii=False)

    # --- Dashboard Tab ---
    def setup_dashboard(self):
        for widget in self.tab_dashboard.winfo_children():
            widget.destroy()

        tk.Label(self.tab_dashboard, text="EGO INTELLIGENCE SUMMARY", font=("Segoe UI", 20, "bold"), fg=THEME['accent'], bg=THEME['bg']).pack(pady=30)
        
        stats_frame = tk.Frame(self.tab_dashboard, bg=THEME['surface'], padx=20, pady=20)
        stats_frame.pack(fill=tk.X, padx=50)
        
        submitted = len([t for t in self.tracker_data['tasks'] if t['status'] == 'Submitted'])
        drafts = len([t for t in self.tracker_data['tasks'] if t['status'] == 'Drafting'])
        interview = len([t for t in self.tracker_data['tasks'] if t['status'] == 'Interview'])
        
        self.create_stat_card(stats_frame, "ES Submitted", str(submitted), THEME['success'])
        self.create_stat_card(stats_frame, "Pending Drafts", str(drafts), THEME['warning'])
        self.create_stat_card(stats_frame, "Interviewing", str(interview), THEME['accent'])

    def create_stat_card(self, parent, title, value, color):
        f = tk.Frame(parent, bg=THEME['bg'], bd=1, relief=tk.SOLID)
        f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(f, text=value, font=("Segoe UI", 40, "bold"), fg=color, bg=THEME['bg']).pack()
        tk.Label(f, text=title, font=("Segoe UI", 12), fg=THEME['text_dim'], bg=THEME['bg']).pack(pady=(0, 10))

    # --- Tracker Tab (Kanban) ---
    def setup_tracker(self):
        if not hasattr(self, 'kanban_frame'):
            self.kanban_frame = tk.Frame(self.tab_tracker, bg=THEME['kanban_bg'])
            self.kanban_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.cols_frames = {}
            for col in self.tracker_data['columns']:
                cf = tk.Frame(self.kanban_frame, bg=THEME['surface'], width=200)
                cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                cf.pack_propagate(False)
                tk.Label(cf, text=col, font=("Segoe UI", 12, "bold"), fg=THEME['text'], bg=THEME['surface']).pack(pady=10)
                self.cols_frames[col] = cf
            
            controls = tk.Frame(self.tab_tracker, bg=THEME['bg'])
            controls.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
            tk.Button(controls, text="+ Add New ES", command=self.add_task_dialog, bg=THEME['accent'], fg='#ffffff', font=("Segoe UI", 10, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT)
            tk.Button(controls, text="🌐 Strategic Map", command=self.open_map, bg=THEME['success'], fg='#ffffff', font=("Segoe UI", 10, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)
        
        self.refresh_kanban()

    def refresh_kanban(self):
        for col, frame in self.cols_frames.items():
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Frame) or (isinstance(widget, tk.Label) and "Segoe UI" not in str(widget.cget("font"))):
                     if widget.winfo_class() != "Label": # Keep headers
                        widget.destroy()

        for task in self.tracker_data['tasks']:
            col = task['status']
            if col in self.cols_frames:
                self.create_task_card(self.cols_frames[col], task)

    def create_task_card(self, parent, task):
        card = tk.Frame(parent, bg=THEME['bg'], bd=0, highlightthickness=1, highlightbackground=THEME['text_dim'])
        card.pack(fill=tk.X, padx=5, pady=5)
        
        card.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        header_lbl = tk.Label(card, text=task['company'], font=("Segoe UI", 11, "bold"), fg=THEME['text'], bg=THEME['bg'])
        header_lbl.pack(anchor='w', padx=5, pady=(5,0))
        header_lbl.bind("<Button-1>", lambda e, t=task: self.edit_task(t))
        
        tk.Label(card, text=f"Limit: {task.get('deadline','-')}", font=("Segoe UI", 9), fg=THEME['warning'], bg=THEME['bg']).pack(anchor='w', padx=5)
        
        btns = tk.Frame(card, bg=THEME['bg'])
        btns.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btns, text=">", command=lambda: self.move_task(task, 1), font=("Consolas", 8), width=3).pack(side=tk.RIGHT)
        tk.Button(btns, text="<", command=lambda: self.move_task(task, -1), font=("Consolas", 8), width=3).pack(side=tk.LEFT)
        
        edit_lbl = tk.Label(btns, text="[Edit]", font=("Segoe UI", 8, "underline"), fg=THEME['text_dim'], bg=THEME['bg'], cursor="hand2")
        edit_lbl.pack(side=tk.LEFT, padx=10)
        edit_lbl.bind("<Button-1>", lambda e, t=task: self.edit_task(t))

    def move_task(self, task, direction):
        cols = self.tracker_data['columns']
        curr_idx = cols.index(task['status'])
        new_idx = curr_idx + direction
        if 0 <= new_idx < len(cols):
            task['status'] = cols[new_idx]
            self.save_tracker_data()
            self.refresh_kanban()
            self.setup_dashboard() 

    # --- Recommendations Tab ---
    def setup_recs(self):
        # Header
        tk.Label(self.tab_recs, text="🏆 STRATEGIC TARGETS (MAJOR)", font=("Segoe UI", 16, "bold"), fg=THEME['accent'], bg=THEME['bg']).pack(pady=20)
        
        canvas = tk.Canvas(self.tab_recs, bg=THEME['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_recs, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

        for rec in RECOMMENDATIONS_OTE:
            self.create_rec_card(scrollable_frame, rec)

    def create_rec_card(self, parent, rec):
        card = tk.Frame(parent, bg=THEME['surface'], bd=0, padx=15, pady=15)
        card.pack(fill=tk.X, pady=10)
        
        header = tk.Frame(card, bg=THEME['surface'])
        header.pack(fill=tk.X)
        
        tk.Label(header, text=rec['name'], font=("Segoe UI", 14, "bold"), fg=THEME['text'], bg=THEME['surface']).pack(side=tk.LEFT)
        tk.Label(header, text=f" [{rec['industry']}]", font=("Consolas", 10), fg=THEME['text_dim'], bg=THEME['surface']).pack(side=tk.LEFT, pady=(5,0), padx=5)
        
        tk.Button(header, text="+ Track", command=lambda r=rec: self.add_rec_to_tracker(r), bg=THEME['success'], fg='#ffffff', font=("Segoe UI", 9, "bold"), relief=tk.FLAT).pack(side=tk.RIGHT)
        
        tk.Label(card, text=rec['reason'], font=("Segoe UI", 10), fg=THEME['text'], bg=THEME['surface'], wraplength=800, justify=tk.LEFT).pack(anchor='w', pady=(5,0))

    def add_rec_to_tracker(self, rec):
        for t in self.tracker_data['tasks']:
            if t['company'] == rec['name']:
                messagebox.showinfo("Info", f"{rec['name']} is already in your tracker.")
                return

        new_task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "company": rec['name'],
            "status": "Drafting",
            "deadline": datetime.now().strftime("%Y-%m-%d"),
            "notes": f"Industry: {rec['industry']}\nReason: {rec['reason']}\n[Added from Recs]"
        }
        self.tracker_data['tasks'].append(new_task)
        self.save_tracker_data()
        self.refresh_kanban()
        self.setup_dashboard()
        messagebox.showinfo("Success", f"Added {rec['name']} to Drafting")

    # --- Research Tab ---
    def setup_research(self):
        if not hasattr(self, 'research_container'):
            self.research_container = tk.Frame(self.tab_research, bg=THEME['bg'])
            self.research_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            search_frame = tk.Frame(self.research_container, bg=THEME['bg'])
            search_frame.pack(fill=tk.X, pady=(0, 10))
            tk.Label(search_frame, text="Search Intelligence:", fg=THEME['text'], bg=THEME['bg']).pack(side=tk.LEFT)
            
            self.search_var = tk.StringVar()
            self.search_var.trace_add("write", lambda *args: self.filter_research_items())
            
            entry = tk.Entry(search_frame, textvariable=self.search_var, width=40, font=("Segoe UI", 11), bg=THEME['surface'], fg=THEME['text'])
            entry.pack(side=tk.LEFT, padx=10)
            tk.Button(search_frame, text="Clear", command=lambda: self.search_var.set(""), bg=THEME['surface'], fg=THEME['text']).pack(side=tk.LEFT)
            tk.Button(search_frame, text="🔄 Reload", command=self.load_all_research_data, bg=THEME['surface'], fg=THEME['text']).pack(side=tk.LEFT, padx=5)
            
            self.research_list_frame = tk.Frame(self.research_container, bg=THEME['surface'])
            self.research_list_frame.pack(fill=tk.BOTH, expand=True)

            self.research_tree = ttk.Treeview(self.research_list_frame, columns=("Collected"), show="tree headings", selectmode="browse", height=20)
            self.research_tree.heading("#0", text="Strategic Entity / Intelligence Title")
            self.research_tree.heading("Collected", text="Collected At")
            self.research_tree.column("#0", width=600)
            self.research_tree.column("Collected", width=100, anchor='center')
            self.research_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Style Treeview for Dark/Light Professional Look
            style = ttk.Style()
            style.configure("Treeview", background="#ffffff", foreground=THEME['text'], fieldbackground="#ffffff", font=("Segoe UI", 10))
            style.map("Treeview", background=[('selected', THEME['accent'])], foreground=[('selected', '#ffffff')])

            scrollbar = tk.Scrollbar(self.research_list_frame, orient=tk.VERTICAL, command=self.research_tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.research_tree.config(yscrollcommand=scrollbar.set)
            
            self.research_tree.bind('<<TreeviewSelect>>', self.show_research_detail_tree)
            
            self.research_status = tk.Label(self.research_container, text="Searching...", fg=THEME['text_dim'], bg=THEME['bg'], font=("Segoe UI", 9))
            self.research_status.pack(anchor='w', pady=(5, 0))
            
            self.all_research_cache = []
            self.load_all_research_data()

    def load_all_research_data(self):
        """Load all shukatsu JSONs and group them by company."""
        self.all_research_cache = {} # Key: Company Name, Value: List of items
        files = glob.glob(os.path.join(SHUKATSU_DATA_DIR, "*.json"))
        
        for f in files:
            if "processed_shukatsu" in f: continue
            try:
                with open(f, 'r', encoding='utf-8') as j:
                    data = json.load(j)
                    comp = str(data.get('ai_analysis', {}).get('company') or "General")
                    if comp.lower() == "none": comp = "General"
                    
                    if comp not in self.all_research_cache:
                        self.all_research_cache[comp] = []
                    self.all_research_cache[comp].append(data)
            except: pass
        
        # Sort each group by date
        for comp in self.all_research_cache:
            self.all_research_cache[comp].sort(key=lambda x: x.get('collected_at', ''), reverse=True)
            
        self.filter_research_items()

    def filter_research_items(self):
        """Real-time hierarchical filtering from cache."""
        for i in self.research_tree.get_children():
            self.research_tree.delete(i)
            
        query = self.search_var.get().lower().strip()
        self.research_items_map = {} # Map iid to data
        
        count = 0
        total = 0
        
        # Sort Companies Alphabetically
        for company in sorted(self.all_research_cache.keys()):
            company_items = self.all_research_cache[company]
            total += len(company_items)
            
            # Filter within company
            filtered_items = []
            for item in company_items:
                title = str(item.get('title', 'No Title'))
                summary = str(item.get('ai_analysis', {}).get('summary') or "")
                intent = str(item.get('critical_analysis', {}).get('true_intent') or "")
                
                if (not query or 
                    query in company.lower() or 
                    query in title.lower() or 
                    query in summary.lower() or 
                    query in intent.lower()):
                    filtered_items.append(item)
            
            if filtered_items:
                parent = self.research_tree.insert("", tk.END, text=f"🏢 {company}", values=("",), open=(query != ""))
                for item in filtered_items:
                    iid = self.research_tree.insert(parent, tk.END, text=item.get('title', 'No Title'), values=(item.get('collected_at', '')[:10],))
                    self.research_items_map[iid] = item
                    count += 1
        
        self.research_status.config(text=f"Found {count} items across {len(self.all_research_cache)} companies. (Grouped by Company)")

    def show_research_detail_tree(self, event):
        selection = self.research_tree.selection()
        if not selection or selection[0] not in self.research_items_map: return
        
        data = self.research_items_map[selection[0]]
        self.display_detail_popup(data)

    def display_detail_popup(self, data):
        top = tk.Toplevel(self)
        top.title("Intelligence Detail")
        top.geometry("700x700")
        top.configure(bg=THEME['bg'])
        
        text = tk.Text(top, bg=THEME['surface'], fg=THEME['text'], font=("Segoe UI", 11), wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)
        
        analysis = data.get('ai_analysis', {})
        critical = data.get('critical_analysis', {})
        
        content = f"""SOURCE: {data.get('source')}
TITLE: {data.get('title')}
LINK: {data.get('link')}

--- 🤖 AI SUMMARY ---
{analysis.get('summary')}

--- 🏢 COMPANY PROFILE ---
{analysis.get('company_profile', 'N/A')}

--- 📊 SWOT ANALYSIS ---
Strengths: {critical.get('swot', {}).get('strength', 'N/A')}
Weaknesses: {critical.get('swot', {}).get('weakness', 'N/A')}
Opportunities: {critical.get('swot', {}).get('opportunity', 'N/A')}
Threats: {critical.get('swot', {}).get('threat', 'N/A')}

--- ⚔️ STRATEGIC ACTION PLAN (Yuto Exclusive) ---
{critical.get('action_plan', 'N/A')}

--- 🏰 DEEP STRATEGIC DOSSIER (IR/Plan Analysis) ---
{data.get('deep_strategic_dossier', 'N/A')}

--- 👁️ TRUE INTENT & BIAS ANALYSIS ---
Intent: {critical.get('true_intent', 'N/A')}
Bias Warning: {data.get('bias', 'N/A')}

--- 🏛️ ACADEMIC DEEP DIVE / INTELLECTUAL GENEALOGY ---
{analysis.get('academic_deep_dive', 'N/A')}

--- 🛰️ DEEP WEB INTELLIGENCE (EXPERIMENTAL) ---
{data.get('ai_analysis', {}).get('deep_web_intel', 'N/A')}
"""
        text.insert(tk.END, content)

    # --- Add / Edit Dialog ---
    def add_task_dialog(self):
        self.open_task_editor(None)

    def edit_task(self, task):
        self.open_task_editor(task)

    def open_task_editor(self, task=None):
        is_new = task is None
        
        dialog = tk.Toplevel(self)
        dialog.title("Add / Edit Task")
        dialog.geometry("400x500")
        dialog.configure(bg=THEME['bg'])
        
        def lbl(txt): tk.Label(dialog, text=txt, fg=THEME['text'], bg=THEME['bg'], font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20, pady=(15, 5))
        
        lbl("Company Name:")
        var_company = tk.StringVar(value=task['company'] if not is_new else "")
        tk.Entry(dialog, textvariable=var_company, font=("Segoe UI", 11), bg=THEME['surface'], fg=THEME['text']).pack(fill=tk.X, padx=20)
        
        lbl("Deadline (YYYY-MM-DD):")
        var_deadline = tk.StringVar(value=task.get('deadline', '') if not is_new else datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(dialog, textvariable=var_deadline, font=("Segoe UI", 11), bg=THEME['surface'], fg=THEME['text']).pack(fill=tk.X, padx=20)
        
        lbl("Status:")
        status_opts = self.tracker_data['columns']
        var_status = tk.StringVar(value=task['status'] if not is_new else status_opts[0])
        ttk.Combobox(dialog, textvariable=var_status, values=status_opts, state="readonly").pack(fill=tk.X, padx=20)
        
        lbl("Notes / Strategies:")
        txt_notes = tk.Text(dialog, height=6, font=("Segoe UI", 10), bg=THEME['surface'], fg=THEME['text'])
        txt_notes.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        if not is_new: txt_notes.insert(tk.END, task.get('notes', ''))
        
        def save():
            new_company = var_company.get().strip()
            if not new_company:
                messagebox.showerror("Error", "Company name is required.")
                return
            
            nonlocal task
            if is_new:
                task = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "company": new_company,
                    "status": var_status.get(),
                    "deadline": var_deadline.get(),
                    "notes": txt_notes.get("1.0", tk.END).strip()
                }
                self.tracker_data['tasks'].append(task)
            else:
                task['company'] = new_company
                task['status'] = var_status.get()
                task['deadline'] = var_deadline.get()
                task['notes'] = txt_notes.get("1.0", tk.END).strip()
            
            self.save_tracker_data()
            self.refresh_kanban()
            self.setup_dashboard()
            dialog.destroy()
        
        def delete():
            if messagebox.askyesno("Confirm", "Delete this task?"):
                self.tracker_data['tasks'].remove(task)
                self.save_tracker_data()
                self.refresh_kanban()
                self.setup_dashboard()
                dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=THEME['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(btn_frame, text="SAVE", command=save, bg=THEME['accent'], fg='#ffffff', font=("Segoe UI", 10, "bold"), width=15, relief=tk.FLAT).pack(side=tk.RIGHT)
        if not is_new:
            tk.Button(btn_frame, text="DELETE", command=delete, bg=THEME['error'], fg='#ffffff', font=("Segoe UI", 10, "bold"), relief=tk.FLAT).pack(side=tk.LEFT)

    def open_map(self):
        import webbrowser
        # Map is in a sibling directory to 'youtube_channel'
        map_path = os.path.join(os.path.dirname(BASE_DIR), "shukatsu_map", "index.html")
        webbrowser.open(f"file:///{map_path.replace('\\', '/')}")

if __name__ == "__main__":
    app = ShukatsuHQ()
    app.mainloop()
