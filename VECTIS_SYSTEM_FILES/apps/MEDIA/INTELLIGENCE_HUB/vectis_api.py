import http.server
import socketserver
import json
import os
import glob
from urllib.parse import urlparse, parse_qs

# --- Configuration ---
PORT = 8999
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data"))
SHUKATSU_DIR = os.path.join(DATA_DIR, "shukatsu")
NOTES_FILE = r"C:\Users\Yuto\clawd\research_notes.md"

class VectisHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API: /api/stats
        if parsed.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow any app to connect
            self.end_headers()
            
            stats = self.get_stats()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            return

        # API: /api/notes
        if parsed.path == '/api/notes':
            self.send_response(200)
            self.send_header('Content-type', 'text/markdown; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            content = ""
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
            self.wfile.write(content.encode('utf-8'))
            return
            
        # Default: Serve Files
        super().do_GET()

    def get_stats(self):
        # Quick file count
        files = glob.glob(os.path.join(SHUKATSU_DIR, "*.json"))
        return {
            "status": "online",
            "files_count": len(files),
            "data_dir": DATA_DIR
        }

if __name__ == "__main__":
    os.chdir(DATA_DIR) # Serve data directory statically for easy access
    
    # Use a subclass to allow address reuse (prevents WinError 10048)
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    try:
        with ReusableTCPServer(("", PORT), VectisHandler) as httpd:
            print(f"🌍 EGO Universal API Server running at http://localhost:{PORT}")
            print(f"   - API: http://localhost:{PORT}/api/stats")
            print(f"   - Notes: http://localhost:{PORT}/api/notes")
            print(f"   - File Server: Rooted at {DATA_DIR}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 API Server stopping...")
    except OSError as e:
        if e.errno == 10013:
            print(f"❌ Error: Permission denied on port {PORT}. (WinError 10013)")
            print("   The port might be reserved by another service or restricted.")
        elif e.errno == 10048:
            print(f"❌ Error: Port {PORT} is already in use. (WinError 10048)")
        else:
            print(f"❌ Unexpected Error during startup: {e}")
