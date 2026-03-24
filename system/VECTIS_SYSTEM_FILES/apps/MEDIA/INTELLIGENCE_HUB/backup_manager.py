import os
import shutil
import glob
from datetime import datetime
import time

# --- Configuration ---
# C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\youtube_channel\backup_manager.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data is at C:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data"))
# Backup Destination: Desktop/EGO_BACKUPS
BACKUP_ROOT = r"C:\Users\Yuto\Desktop\EGO_BACKUPS"

def perform_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_ROOT, timestamp)
    
    print(f"📦 Starting Safety Backup...")
    print(f"   Source: {DATA_DIR}")
    print(f"   Dest:   {backup_dir}")
    
    try:
        # Create Backup Dir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy System Data
        shutil.copytree(DATA_DIR, os.path.join(backup_dir, "data"), dirs_exist_ok=True)
        
        # Copy Research Notes (External)
        notes_file = r"C:\Users\Yuto\clawd\research_notes.md"
        if os.path.exists(notes_file):
            shutil.copy2(notes_file, backup_dir)
            
        print(f"✅ Backup Complete! Data is safe in {timestamp}")
        
        # Cleanup old backups (Keep last 10)
        backups = sorted(glob.glob(os.path.join(BACKUP_ROOT, "*")))
        if len(backups) > 10:
            print("   Cleaning up old backups...")
            for b in backups[:-10]:
                shutil.rmtree(b)
                print(f"   - Removed {os.path.basename(b)}")
                
    except Exception as e:
        print(f"❌ Backup Failed: {e}")

if __name__ == "__main__":
    perform_backup()
