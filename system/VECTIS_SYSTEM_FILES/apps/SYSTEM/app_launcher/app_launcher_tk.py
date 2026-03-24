import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys
import subprocess
from pathlib import Path

class AppLauncher(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        
        self.apps_found = []
        self.find_apps()
        self.create_app_widgets()

    def find_apps(self):
        """
        Scans the sibling directories for Tkinter apps (containing a '*_tk.py' file).
        """
        script_path = Path(__file__).resolve()
        apps_root_dir = script_path.parent.parent # VECTIS_SYSTEM_FILES/apps/
        
        for app_dir in apps_root_dir.iterdir():
            if app_dir.is_dir():
                for file in app_dir.iterdir():
                    if file.name.endswith("_tk.py"):
                        app_name = app_dir.name
                        self.apps_found.append({
                            "name": app_name.replace("_", " ").title(),
                            "path": file
                        })
                        break # Found the tk app, no need to check other files in this dir
        
        # Sort apps alphabetically by name
        self.apps_found.sort(key=lambda x: x['name'])

    def create_app_widgets(self):
        """
        Creates a button for each app found.
        """
        header = ttk.Label(self, text="VECTIS Application Launcher", font="-size 20 -weight bold")
        header.pack(pady=(0, 20))

        # Scrollable Frame for buttons
        canvas = ttk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, app in enumerate(self.apps_found):
            btn = ttk.Button(
                scrollable_frame, 
                text=app['name'], 
                command=lambda p=app['path']: self.launch_app(p),
                bootstyle="outline"
            )
            btn.pack(fill=X, pady=5, padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        if not self.apps_found:
             ttk.Label(scrollable_frame, text="No Tkinter apps found.").pack(pady=20)


    def launch_app(self, script_path):
        """
        Launches the given app script using the same python interpreter.
        """
        python_executable = sys.executable # Use the same python that's running the launcher
        try:
            print(f"Launching: {python_executable} {script_path}")
            subprocess.Popen([python_executable, script_path])
        except Exception as e:
            print(f"Failed to launch {script_path}: {e}")
            # Optionally, show an error in the GUI
            # messagebox.showerror("Launch Error", f"Failed to launch app:\n{e}")


if __name__ == '__main__':
    app = ttk.Window("VECTIS Launcher", "cosmo", resizable=(False, True))
    app.geometry("400x600")
    AppLauncher(app)
    app.mainloop()
