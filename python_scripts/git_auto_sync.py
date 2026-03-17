import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 設定
WATCH_PATH = "."  # 監視するディレクトリ
SYNC_DELAY = 5    # 最後の変更から同期開始までの待ち時間（秒）
COMMIT_MSG = "Auto-sync from Antigravity"
IGNORE_DIRS = [".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"]

class GitSyncHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_change_time = 0
        self.needs_sync = False

    def on_any_event(self, event):
        # フォルダ自身や無視対象のディレクトリはスキップ
        if event.is_directory:
            return
        
        # 特定のディレクトリは無視
        path_parts = os.path.normpath(event.src_path).split(os.sep)
        if any(ignore in path_parts for ignore in IGNORE_DIRS):
            return

        print(f"[*] Change detected: {event.src_path}")
        self.last_change_time = time.time()
        self.needs_sync = True

    def perform_sync(self):
        print("[!] Starting auto-sync...")
        try:
            # git statusを確認して変更があるかチェック
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if not status.stdout.strip():
                print("[*] No changes to sync.")
                self.needs_sync = False
                return

            # 同期処理
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", COMMIT_MSG], check=True)
            subprocess.run(["git", "push"], check=True)
            print("[+] Sync complete!")
        except subprocess.CalledProcessError as e:
            print(f"[X] Sync failed: {e}")
        
        self.needs_sync = False

def main():
    handler = GitSyncHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_PATH, recursive=True)
    observer.start()
    
    print(f"[*] Git Auto-Sync started. Monitoring {os.getcwd()}")
    print(f"[*] Delay: {SYNC_DELAY}s | Commit Message: '{COMMIT_MSG}'")

    try:
        while True:
            # 変更があり、かつ最後の変更から一定時間経過していたら同期
            if handler.needs_sync and (time.time() - handler.last_change_time > SYNC_DELAY):
                handler.perform_sync()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Stopping auto-sync...")
    
    observer.join()

if __name__ == "__main__":
    main()
