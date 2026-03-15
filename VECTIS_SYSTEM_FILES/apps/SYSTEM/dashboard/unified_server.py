import http.server
import socketserver
import os
import webbrowser
import threading
import time
import subprocess
from urllib.parse import urlparse, parse_qs
import json

# --- CONFIGURATION ---
PORT = 9100  # New port for the Unified System (changed from 9000 to avoid DevTools conflict)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))

class UnifiedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from current directory (which is now ROOT_DIR)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # 1. API: Launcher
        if self.path.startswith("/api/launch"):
            self.handle_launch()
            return

        # 2. explicit Dashboard routing (Fix 404)
        if self.path == "/" or self.path == "/index.html" or "unified_dashboard.html" in self.path:
            dashboard_path = os.path.join(CURRENT_DIR, "unified_dashboard.html")
            print(f"📄 Serving Dashboard: {dashboard_path}")
            if os.path.exists(dashboard_path):
                try:
                    with open(dashboard_path, "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(f.read())
                    return
                except Exception as e:
                     print(f"❌ Read Error: {e}")
            else:
                print("❌ Dashboard file missing!")

        # Default Static File Serving (Fallback)
        # Verify where it thinks it is looking
        # print(f"🔍 Looking for: {self.path} in {ROOT_DIR}")
        super().do_GET()

    def handle_launch(self):
        """ Handles executing local files (.bat, .py) """
        try:
            query = parse_qs(urlparse(self.path).query)
            target = query.get('target', [None])[0]
            
            if not target:
                self.send_error(400, "Missing target parameter")
                return

            # Security / Path Resolution
            target_path = os.path.normpath(os.path.join(ROOT_DIR, target))
            
            print(f"🚀 EXEC: {target_path}")

            if not os.path.exists(target_path):
                self.send_error(404, "File not found")
                return

            # Execution Logic
            if target_path.endswith(".bat"):
                # Detached execution for Batch
                subprocess.Popen(f'start "" "{target_path}"', shell=True, cwd=os.path.dirname(target_path))
            elif target_path.endswith(".py"):
                # Python scripts need to run in their own dir
                # subprocess.Popen(['python', target_path], cwd=os.path.dirname(target_path), shell=True) # blocks prompt if shell=False in some cases?
                # Using 'start python ...' to ensure new window
                subprocess.Popen(f'start python "{target_path}"', shell=True, cwd=os.path.dirname(target_path))
            else:
                 # Generic OS open
                 os.startfile(target_path)

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK: Launched")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.send_error(500, f"Server Error: {str(e)}")

    def log_message(self, format, *args):
        # Reduce log noise
        if "GET" in format and "200" in format: return
        print(f"[{self.log_date_time_string()}] {format % args}")

def start_server():
    print("="*40)
    print(f"⚡ VECTIS UNIFIED SERVER (Port {PORT})")
    print(f"⚡ Root: {ROOT_DIR}")
    print("="*40)
    
    url = f"http://localhost:{PORT}/apps/SYSTEM/dashboard/unified_dashboard.html"
    
    def open_browser():
        time.sleep(1.5)
        print(f"🌐 Opening Dashboard: {url}")
        webbrowser.open(url)
    
    threading.Thread(target=open_browser).start()
    
    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), UnifiedHandler) as httpd:
            print("🟢 Server Ready. Press Ctrl+C to stop.")
            httpd.serve_forever()
    except OSError as e:
        print(f"❌ Port {PORT} busy. Kill existing python processes or change port.")

if __name__ == "__main__":
    # Ensure we are serving from the correct root
    os.chdir(ROOT_DIR)
    start_server()
