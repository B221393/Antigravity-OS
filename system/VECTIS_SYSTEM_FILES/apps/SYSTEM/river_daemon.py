
import time
import subprocess
import datetime
import sys
import json
from pathlib import Path

# Configuration
VECTIS_ROOT = Path(r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES")
RIVER_SCRIPT = VECTIS_ROOT / "apps" / "SYSTEM" / "river_flow.py"
LOG_FILE = VECTIS_ROOT / "apps" / "SYSTEM" / "river_daemon.log"
CONFIG_FILE = VECTIS_ROOT / "apps" / "SYSTEM" / "river_config.json"

def load_config():
    """設定ファイルを読み込む（ファイル編集不要でカスタマイズ可能）"""
    default = {"interval_seconds": 300}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

# Load interval from config (default 5 minutes = 300 seconds)
config = load_config()
INTERVAL = config.get("interval_seconds", 300) 

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def run_river():
    log("🌊 Starting River Flow Cycle...")
    try:
        # Run with --discover flag to find new companies
        target_process = subprocess.run(
            ["python", str(RIVER_SCRIPT), "--discover"],
            cwd=str(VECTIS_ROOT),
            capture_output=True,
            text=True
        )
        
        if target_process.returncode == 0:
            log("✅ River Flow Cycle Completed Successfully.")
            log(f"Output Preview: {target_process.stdout[:200]}...")
        else:
            log(f"❌ River Flow Failed with code {target_process.returncode}")
            log(f"Error: {target_process.stderr}")
            
    except Exception as e:
        log(f"❌ Critical Daemon Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    log("🚀 VECTIS River Daemon Started (PID: {})".format(sys.argv[0]))
    log("   Schedule: Running every 6 hours.")
    
    while True:
        run_river()
        
        log(f"💤 Sleeping for {INTERVAL} seconds...")
        sys.stdout.flush()
        time.sleep(INTERVAL)
