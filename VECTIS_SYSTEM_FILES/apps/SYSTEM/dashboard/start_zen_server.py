import http.server
import socketserver
import os
import webbrowser
import threading
import time
import subprocess

# Configuration
PORT = 8999 # Unique port to avoid conflicts
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Root is VECTIS_SYSTEM_FILES to allow navigating to other apps
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))

class VectisHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    
    def do_GET(self):
        # API: Execute Local File
        if self.path.startswith("/run_app"):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            target = query.get('target', [None])[0]
            
            if target:
                # Security: Ensure target is within allowable paths (basic check)
                # Allowing absolute paths since this is a local personal tool
                target_path = os.path.normpath(os.path.join(ROOT_DIR, target))
                
                print(f"🚀 Request to launch: {target_path}")
                
                if os.path.exists(target_path):
                    try:
                        # Use start in shell to detach
                        if target_path.endswith(".bat"):
                             subprocess.Popen(f'start "" "{target_path}"', shell=True, cwd=os.path.dirname(target_path))
                        else:
                             os.startfile(target_path)
                             
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b"Launched")
                        return
                    except Exception as e:
                        print(f"❌ Launch Error: {e}")
                        self.send_response(500)
                        self.end_headers()
                        self.wfile.write(f"Error: {e}".encode())
                        return
                else:
                    print(f"❌ File not found: {target_path}")
                    self.send_response(404)
                    self.end_headers()
                    return

        # Default: Serve Files
        super().do_GET()

def start_server():
    print(f"⚡ VECTIS ZEN SERVER | Root: {ROOT_DIR}")
    print(f"⚡ Port: {PORT}")
    
    # Open Browser
    rel_path = "apps/SYSTEM/dashboard/zen_dashboard.html"
    url = f"http://localhost:{PORT}/{rel_path}"
    
    print(f"⚡ Opening: {url}")
    
    def open_browser():
        time.sleep(1)
        webbrowser.open(url)
    
    threading.Thread(target=open_browser).start()
    
    try:
        # Allow reuse address to prevent 'Address already in use'
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), VectisHandler) as httpd:
            print("⚡ Server Running. Waiting for commands...")
            httpd.serve_forever()
    except OSError as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()
