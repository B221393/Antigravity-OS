import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class KanjiNumApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # --- Data ---
        self.daiji_map = str.maketrans("0123456789", "零壱弐参肆伍陸漆捌玖")

        # --- Widgets ---
        header = ttk.Label(self, text="Kanji Num (大字変換)", font="-size 20 -weight bold")
        header.pack(pady=(0, 20))
        
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=X, pady=5)
        input_label = ttk.Label(input_frame, text="Amount (Yen):", width=15)
        input_label.pack(side=LEFT)

        self.amount_var = ttk.StringVar()
        self.amount_var.trace_add("write", self.update_results)
        amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var)
        amount_entry.pack(side=LEFT, fill=X, expand=YES)

        # --- Results ---
        results_frame = ttk.LabelFrame(self, text="Results") # Removed padding from here
        results_frame.pack(fill=BOTH, expand=YES, pady=10)
        results_frame.columnconfigure(1, weight=1)

        # Direct Mapping
        direct_label = ttk.Label(results_frame, text="Direct Mapping:")
        direct_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.direct_var = ttk.StringVar()
        direct_entry = ttk.Entry(results_frame, textvariable=self.direct_var, state="readonly", font=('Courier', 10))
        direct_entry.grid(row=0, column=1, sticky=EW, padx=5)

        # Formal Legal
        formal_label = ttk.Label(results_frame, text="Formal Legal:")
        formal_label.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.formal_var = ttk.StringVar()
        formal_entry = ttk.Entry(results_frame, textvariable=self.formal_var, state="readonly", font=('Courier', 10))
        formal_entry.grid(row=1, column=1, sticky=EW, padx=5)
        
        # Set initial value AFTER all vars are created to avoid race condition
        self.amount_var.set("10000")

    def to_daiji(self, n_str):
        # Filter only digits from the input string
        s = "".join(filter(str.isdigit, n_str))
        if not s:
            return ""
        return s.translate(self.daiji_map)

    def update_results(self, *args):
        amount_str = self.amount_var.get()
        daiji_result = self.to_daiji(amount_str)
        
        self.direct_var.set(daiji_result)
        
        if daiji_result:
            self.formal_var.set(f"金 {daiji_result} 円 也")
        else:
            self.formal_var.set("")


if __name__ == '__main__':
    app = ttk.Window("Kanji Num", "cosmo")
    app.geometry("500x300")
    KanjiNumApp(app)
    app.mainloop()
