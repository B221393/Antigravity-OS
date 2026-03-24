import sys
import os
import subprocess
import time
import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QThread, pyqtSignal

# Configuration
BACKEND_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_studio", "studio_backend.py")
PORT = 8888
URL = f"http://localhost:{PORT}/vectis_studio.html"

class BackendWorker(QThread):
    def run(self):
        # Check if port is already in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', PORT))
        if result == 0:
            print(f"Port {PORT} already in use. Assuming backend is running.")
            sock.close()
            return
        sock.close()

        print("Starting backend...")
        # Use python from current environment
        python_exe = sys.executable
        # Run backend without showing window
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        self.proc = subprocess.Popen([python_exe, BACKEND_SCRIPT], cwd=os.path.dirname(BACKEND_SCRIPT), startupinfo=si)
        self.proc.wait()

    def stop(self):
        if hasattr(self, 'proc'):
            self.proc.terminate()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Coder Native (Node Studio)")
        self.resize(1200, 800)

        # Start Backend
        self.backend = BackendWorker()
        self.backend.start()
        
        # Wait a bit for server to start
        # In a real app, we should poll the port
        
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        
        # Load logic
        self.load_timer = 0
        self.check_server()

    def check_server(self):
        # Simple polling to see if server is up
        import urllib.request
        try:
            urllib.request.urlopen(URL)
            self.browser.setUrl(QUrl(URL))
        except:
            if self.load_timer < 20: # Try for 10 seconds
                self.load_timer += 1
                QApplication.processEvents()
                time.sleep(0.5)
                self.check_server()
            else:
                self.browser.setHtml(f"<h1>Error: Could not connect to backend at {URL}</h1>")

    def closeEvent(self, event):
        self.backend.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
