"""
VECTIS Schedule Wallpaper Auto-Watcher
スケジュールファイルを監視し、変更があれば自動で壁紙を更新する
"""

import time
import os
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# 監視対象
SCHEDULE_FILE = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\CAREER\SCHEDULE.md")
SCHEDULE_JSON = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\data\SCHEDULE.json")
UPDATE_SCRIPT = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\bin\update_wallpaper.py")

class ScheduleHandler(FileSystemEventHandler):
    """スケジュールファイルの変更を監視"""
    
    def __init__(self):
        self.last_update = 0
        self.cooldown = 3  # 連続更新を防ぐクールダウン（秒）
    
    def on_modified(self, event):
        # ディレクトリは無視
        if event.is_directory:
            return
        
        # 対象ファイルかチェック
        src_path = Path(event.src_path)
        if src_path.name not in ['SCHEDULE.md', 'SCHEDULE.json']:
            return
        
        # クールダウンチェック
        now = time.time()
        if now - self.last_update < self.cooldown:
            return
        
        self.last_update = now
        
        print(f"\n{'='*50}")
        print(f"📅 スケジュール変更検出: {src_path.name}")
        print(f"   時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # 壁紙更新
        self.update_wallpaper()
    
    def update_wallpaper(self):
        """壁紙を更新"""
        try:
            print("🎨 壁紙を更新中...")
            result = subprocess.run(
                ['python', str(UPDATE_SCRIPT)],
                capture_output=True,
                text=True,
                cwd=UPDATE_SCRIPT.parent
            )
            
            if result.returncode == 0:
                print("✅ 壁紙更新完了！")
            else:
                print(f"⚠️ エラー: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 壁紙更新失敗: {e}")

def main():
    print("""
╔══════════════════════════════════════════════════╗
║   VECTIS Schedule Wallpaper Watcher              ║
║   スケジュール変更を監視し、壁紙を自動更新       ║
╚══════════════════════════════════════════════════╝
    """)
    
    # 監視対象ディレクトリ
    watch_paths = [
        SCHEDULE_FILE.parent,  # CAREER/
        SCHEDULE_JSON.parent,  # data/
    ]
    
    event_handler = ScheduleHandler()
    observer = Observer()
    
    for path in watch_paths:
        if path.exists():
            observer.schedule(event_handler, str(path), recursive=False)
            print(f"👀 監視中: {path}")
    
    observer.start()
    print("\n⏳ スケジュールファイルの変更を待機中...")
    print("   (Ctrl+C で終了)\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 監視を終了します")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
