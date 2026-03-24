"""
EGO Neuro-Link: Brain Server (The Bridge)
=========================================
A Zero-Dependency HTTP Server that connects Logic Studio (Browser) to Python (AI).
It listens for 'POST /think' requests containing Game State, asks the Agent, and returns an Action.

Design Pattern: Client-Server API
"""

import http.server
import socketserver
import json
import os
import sys

# Import our Agent (Systematic Module Import)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent import RuleBasedAgent

# Configuration
PORT = 8080
active_agent = RuleBasedAgent("Neuro-Bot v1")

class NeuroLinkHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom Request Handler to handle API calls.
    Overrides standard method to handle JSON POST requests.
    """
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests (Browser Security)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle incoming Game State signals"""
        if self.path == '/think':
            # 1. Read Valid JSON Input
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                game_state = json.loads(post_data.decode('utf-8'))
                
                # 2. Ask the "Brain" (Agent) to think
                action = active_agent.think(game_state)
                
                # 3. Send Response back to "Body" (Game)
                response = {"action": action, "agent": active_agent.name}
                self._send_json(response)
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data):
        """Helper to send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow Browser Access
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server():
    print(f"🧠 [Neuro-Link] Brain Server starting on port {PORT}...")
    print(f"   Listening for Game Signals at http://localhost:{PORT}/think")
    
    # Allow address reuse to prevent 'Address already in use' errors during restart
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), NeuroLinkHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🧠 [Neuro-Link] Shutting down...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
