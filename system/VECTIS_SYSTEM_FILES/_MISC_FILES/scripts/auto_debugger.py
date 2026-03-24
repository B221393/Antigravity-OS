"""
VECTIS OS - Autonomous Error Debugger & Runner
==============================================
Wraps command execution to automatically detect errors and trigger Ollama debugging.
"""

import sys
import os
import subprocess
import datetime
import shutil
from pathlib import Path

# --- Configuration ---
SYSTEM_ROOT = Path(__file__).parent.parent
LOG_DIR = SYSTEM_ROOT / "logs"
ERROR_REPORT_FILE = LOG_DIR / "ERROR_REPORT.md"
DEBUG_SCRIPT = SYSTEM_ROOT / "scripts" / "ask_ollama_debug.py"

def log_error(command, stderr_output, return_code):
    """Logs the error to ERROR_REPORT.md"""
    timestamp = datetime.datetime.now().isoformat()
    
    if not ERROR_REPORT_FILE.exists():
        ERROR_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("# Error Report\n\n| Timestamp | Error Message | Context | Status |\n|---|---|---|---|"\n)

    # Format for Markdown table (simplified)
    # Note: Complex multiline errors break simple tables, so we append details below.
    summary = stderr_output.split('\n')[-2] if stderr_output else "Unknown Error"
    summary = summary.replace("|", "\|").strip()
    
    with open(ERROR_REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | {summary} | Command: `{command}` | 🔴 New |\n")
        f.write(f"\n<details><summary>Full Traceback ({timestamp})</summary>\n\n```text\n{stderr_output}\n```\n</details>\n\n")
    
    return timestamp

def trigger_ollama_debug():
    """Triggers the Ollama debug script autonomously."""
    print("\n[VECTIS AUTO-DEBUGGER] Error detected. Summoning AI Agent...")
    
    # We call the existing debug script. 
    # Since we are already in python, we could import it, but subprocess ensures a clean context matches manual invocation.
    try:
        # Assuming the debug script takes the last error automatically if no args provided
        result = subprocess.run(
            [sys.executable, str(DEBUG_SCRIPT)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        suggestion = result.stdout
        
        # Append suggestion to log
        if suggestion:
            with open(ERROR_REPORT_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n### 🤖 AI Analysis\n{suggestion}\n\n---")
            print(suggestion)
        else:
            print("AI silent (no output).")
            if result.stderr:
                print(f"Debugger Error: {result.stderr}")

    except Exception as e:
        print(f"Failed to trigger AI debugger: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_debugger.py <command_to_run>")
        sys.exit(1)

    # Reconstruct the command
    command = sys.argv[1:]
    
    print(f"[VECTIS] Running: {' '.join(command)}")
    
    try:
        # Run the actual command
        # We allow stdout to flow to console, but capture stderr for analysis if needed
        # To display stderr in real-time AND capture it is tricky in pure python cross-platform without threads.
        # For simplicity in this prototype: we let it print to stderr, but if it fails, we might not have captured it 
        # unless we redirect. 
        # Better approach: Capture all, print all.
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate()
        
        # Print output to console
        if stdout: print(stdout)
        if stderr: print(stderr, file=sys.stderr)
        
        if process.returncode != 0:
            # Error detected!
            print(f"\n[!] Process exited with code {process.returncode}")
            log_error(" ".join(command), stderr, process.returncode)
            trigger_ollama_debug()
            sys.exit(process.returncode)
            
    except Exception as e:
        print(f"Wrapper Execution Error: {e}")
        log_error(" ".join(command), str(e), -1)
        trigger_ollama_debug()
        sys.exit(1)

if __name__ == "__main__":
    main()
