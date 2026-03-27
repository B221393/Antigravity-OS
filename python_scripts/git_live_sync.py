import time
import subprocess
import os
import json
from datetime import datetime

# --- CONFIGURATION (Live Sync Engine) ---
SYNC_INTERVAL = 60 # Check every 60 seconds
COMMIT_MSG = "Auto-sync from Antigravity Brain"
STATUS_LOG = r"c:\Users\Yuto\Desktop\app\logs\SYNC_STATUS.json"

def run_git(args):
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git Command Failed: {e.cmd} | Output: {e.output}")
        return None

def sync_cycle():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] --- LIVE SYNC START ---")
    
    # 1. Fetch Remote Status (The "Northern/GitHub" Check)
    run_git(["fetch", "origin"])
    
    # 2. Pull Remote Changes (スマホ版等の変更を取り込む)
    # Use rebase to keep history clean and avoid merge commits
    print("[SYSTEM] 外部脳(GitHub)の最新状態を確認中...")
    pull_result = run_git(["pull", "--rebase", "origin", "main"])
    if pull_result and "Already up to date" not in pull_result:
        print(f"[PULL] スマホ版の変更を同期しました: {pull_result[:50]}...")
        
    # 3. Check for Local Changes
    status = run_git(["status", "--porcelain"])
    if status:
        print(f"[PUSH] ローカルの変更を外部脳(GitHub)へ送信中...")
        run_git(["add", "."])
        run_git(["commit", "-m", COMMIT_MSG])
        run_git(["push", "origin", "main"])
        print("[SUCCESS] 同期完了。")
    else:
        print("[IDLE] 変更なし。")
        
    # 4. Update Status Log for Dashboard
    status_data = {
        "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CONNECTED",
        "repo": "External Brain (GitHub)"
    }
    with open(STATUS_LOG, "w") as f:
        json.dump(status_data, f, indent=4)

def main():
    print("="*60)
    print(" [ ANTIGRAVITY LIVE SYNC ENGINE ]")
    print(" (スマホ版との双方向シンクロを自動で行います / 終了は Ctrl+C)")
    print("="*60)
    
    while True:
        try:
            sync_cycle()
        except Exception as e:
            print(f"[ERROR] Sync cycle failed: {e}")
            
        # Wait for the next cycle
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
