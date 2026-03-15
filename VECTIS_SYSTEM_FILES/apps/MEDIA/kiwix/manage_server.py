import os
import sys
import subprocess
import time
import argparse

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
LIB_DIR = os.path.join(BASE_DIR, "library")
KIWIX_SERVE = os.path.join(BIN_DIR, "kiwix-serve.exe")
PORT = 9000

def find_zim_files():
    zims = [f for f in os.listdir(LIB_DIR) if f.endswith(".zim")]
    return [os.path.join(LIB_DIR, z) for z in zims]

def start_server():
    if not os.path.exists(KIWIX_SERVE):
        print(f"Error: kiwix-serve.exe not found at {KIWIX_SERVE}")
        return

    zims = find_zim_files()
    if not zims:
        print("Error: No ZIM files found in library/")
        return

    # Construct Command: kiwix-serve --port=9000 content.zim
    cmd = [KIWIX_SERVE, "--port=" + str(PORT)] + zims
    
    print(f"Starting Kiwix Server on Port {PORT}...")
    # Hide window on Windows
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    try:
        # Launch independently
        subprocess.Popen(cmd, startupinfo=startupinfo)
        print("Server launch initiated.")
        time.sleep(2)
        print(f"Access at http://localhost:{PORT}")
    except Exception as e:
        print(f"Failed to launch: {e}")

def stop_server():
    print("Stopping Kiwix Server...")
    os.system("taskkill /f /im kiwix-serve.exe")
    print("Stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status"])
    args = parser.parse_args()

    if args.action == "start":
        start_server()
    elif args.action == "stop":
        stop_server()
    elif args.action == "status":
        # Check if port is open (simple check)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', PORT))
        if result == 0:
            print("RUNNING")
        else:
            print("STOPPED")
        sock.close()
