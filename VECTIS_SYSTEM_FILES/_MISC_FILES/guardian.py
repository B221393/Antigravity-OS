import subprocess
import sys
import os
import datetime
import threading
import time

import requests
import json

# ... (Previous imports remain)

import requests
import json
try:
    import pyperclip
except ImportError:
    pyperclip = None

# ... (Previous imports remain)

import requests
import json
try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

# ... (Previous imports remain)

# CONFIG
TARGET_SCRIPT = os.path.join(os.path.dirname(__file__), "apps/vectis_omni/app.py")
BRIDGE_FILE = os.path.join(os.path.dirname(__file__), "AI_CONTEXT_BRIDGE.md")
LOG_FILE = os.path.join(os.path.dirname(__file__), "../../outputs/logs/vectis_runtime.log")

def consult_oracle(error_text):
    """
    Sends the traceback to the local Ollama instance for immediate diagnosis.
    """
    print("\n🛡️ GUARDIAN: 🚨 CRASH DETECTED. CONSULTING VECTIS BRAIN...\n")
    
    prompt = f"""
    [CRITICAL SYSTEM ERROR]
    The Python application crashed with the following traceback.
    Analyze the error and provide the exact cause and a specific fix.
    
    TRACEBACK:
    {error_text}
    
    DIAGNOSIS & FIX:
    """
    
    # Copy to Clipboard & Auto-Paste
    if pyperclip:
        try:
            clip_text = f"CRASH REPORT:\n{error_text}"
            pyperclip.copy(clip_text)
            print("📋 [AUTO-COPY] Copied to clipboard.")
            
            # Auto-Paste (User Requested)
            if pyautogui:
                print("⌨️ [AUTO-PASTE] Injecting to active window in 1s...")
                time.sleep(1.0)
                # We assume the user focus is on the chat window where they can paste
                # Or if they are in the console, pastes there.
                # Actually, this might paste into the console running the script if not careful.
                # But user asked for it.
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                pyautogui.press('enter')
                print("✅ [AUTO-SEND] Error report submitted.")
                
        except Exception as e:
            print(f"Auto-Paste Warning: {e}")

    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "phi4", # Fast local model
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        res = requests.post(url, json=payload, timeout=20)
        if res.status_code == 200:
            analysis = res.json().get("response", "No response.")
            print("="*60)
            print(f"🧠 AI AUTO-DIAGNOSIS:\n{analysis}")
            print("="*60)
            return analysis
    except Exception as e:
        print(f"⚠️ Guardian Auto-Diagnosis Failed: {e}")
        return None

def log_error(error_text):
    if not error_text or error_text.isspace(): return
    
    # 1. Consult AI immediately
    diagnosis = consult_oracle(error_text)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"\n## 🚨 AUTO-DETECTED ERROR [{timestamp}]\n```text\n{error_text}\n```\n"
    
    if diagnosis:
        report += f"\n### 🧠 AI DIAGNOSIS\n{diagnosis}\n"
    
    try:
        # Write to Bridge
        with open(BRIDGE_FILE, "a", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[SYSTEM MONITOR] Error & Diagnosis logged to AI Context Bridge.")
    except Exception as e:
        print(f"[SYSTEM MONITOR] Failed to log error: {e}")

def monitor_stderr(process):
    """
    Reads stderr from the subprocess and logs it if significant.
    """
    capturing = False
    buffer = ""

    while True:
        line = process.stderr.readline()
        if not line:
            break
        
        try:
            text = line.decode('utf-8', errors='ignore')
            
            # Suppress specific warnings
            if "RuntimeWarning: line buffering" in text:
                continue
            
            sys.stderr.write(text) # Console Output
            
            # Start Capturing
            if "Traceback (most recent call last):" in text:
                capturing = True
                buffer = text
            elif capturing:
                buffer += text
                # End condition: Line is not indented and doesn't look like an error line?
                # Actually, standard Traceback ends with "Exception: msg" which is not indented.
                # So we capture until valid next prompt or known exit string "Press any key"
                if text.strip() == "" or text.startswith("Press any key"):
                     capturing = False
                     log_error(buffer)
                     buffer = ""
                # Also if line doesn't start with space and isn't "File ...", it might be the final deviation
                # But "last line" is usually unindented. e.g. "NameError: ..."
                # We'll just grab everything until empty line for safety.
            
            # Fallback for single line errors
            elif "Error:" in text or "Exception" in text:
                if not capturing:
                     log_error(text.strip())

        except Exception as e:
            pass

def main():
    print(f"🛡️ VECTIS GUARDIAN SYSTEM ACTIVE")
    print(f"   Target: {TARGET_SCRIPT}")
    print(f"   Monitoring for crashes...")
    
    # Run the main app as a subprocess, piping stderr
    cmd = [sys.executable, TARGET_SCRIPT]
    
    # We use Popen to keep it running
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=sys.stdout, bufsize=1)
    
    # Start Monitor Thread
    t = threading.Thread(target=monitor_stderr, args=(p,))
    t.daemon = True
    t.start()
    
    try:
        p.wait()
    except KeyboardInterrupt:
        p.terminate()

if __name__ == "__main__":
    main()
