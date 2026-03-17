import os
import subprocess
import time
import asyncio
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mcp.server.fastmcp import FastMCP

# 設定
WATCH_PATH = os.getcwd()
SYNC_DELAY = 5
COMMIT_MSG = "Auto-sync from Antigravity"
IGNORE_DIRS = [".git", "__pycache__", ".pytest_cache", ".venv", "node_modules", ".gemini"]

# MCPサーバーの初期化
mcp = FastMCP("Git Auto-Sync")

class GitSyncManager:
    def __init__(self):
        self.last_change_time = 0
        self.needs_sync = False
        self.enabled = True
        self._lock = asyncio.Lock()

    def on_change(self, path: str):
        if not self.enabled:
            return
        
        path_parts = os.path.normpath(path).split(os.sep)
        if any(ignore in path_parts for ignore in IGNORE_DIRS):
            return

        self.last_change_time = time.time()
        self.needs_sync = True

    async def perform_sync(self, manual_msg: Optional[str] = None):
        async with self._lock:
            msg = manual_msg or COMMIT_MSG
            try:
                # 変更があるかチェック
                status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
                if not status.stdout.strip():
                    self.needs_sync = False
                    return "No changes to sync."

                # 同期実行
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", msg], check=True)
                subprocess.run(["git", "push"], check=True)
                
                self.needs_sync = False
                return f"Successfully synced: {msg}"
            except subprocess.CalledProcessError as e:
                return f"Sync failed: {e.stderr or str(e)}"

sync_manager = GitSyncManager()

class WatcherHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.is_directory:
            sync_manager.on_change(event.src_path)

# --- MCP Tools ---

@mcp.tool()
async def git_sync_now(message: Optional[str] = None) -> str:
    """即座に GitHub と同期（Commit & Push）を実行します。"""
    return await sync_manager.perform_sync(message)

@mcp.tool()
def git_get_status() -> str:
    """現在の Git の状態（未コミットの変更など）を取得します。"""
    try:
        status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, check=True)
        autosync_status = "Enabled" if sync_manager.enabled else "Disabled"
        return f"Autosync: {autosync_status}\n\nChanges:\n{status.stdout or 'Clean'}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def git_toggle_autosync(enable: bool) -> str:
    """自動同期の有効/無効を切り替えます。"""
    sync_manager.enabled = enable
    status = "Enabled" if enable else "Disabled"
    return f"Autosync is now {status}."

# --- Background Monitor ---

async def monitor_loop():
    observer = Observer()
    observer.schedule(WatcherHandler(), WATCH_PATH, recursive=True)
    observer.start()
    try:
        while True:
            if sync_manager.enabled and sync_manager.needs_sync and (time.time() - sync_manager.last_change_time > SYNC_DELAY):
                await sync_manager.perform_sync()
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    # MCPサーバーの実行（バックグラウンドで監視ループも回す）
    # 注: FastMCP.run() は標準入出力を占有するため、監視は別スレッド/タスクで動かす必要がある
    import threading
    
    def start_monitor():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(monitor_loop())

    monitor_thread = threading.Thread(target=start_monitor, daemon=True)
    monitor_thread.start()
    
    mcp.run()
