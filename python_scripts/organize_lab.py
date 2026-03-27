import os
import shutil
import glob

# --- CONFIGURATION (Lab Organizer) ---
BASE_PATH = r"c:\Users\Yuto\Desktop\app"
TARGET_DIRS = {
    "sims": ["game_*.html", "*.sim.html", "quake_sim*", "light_scatter*"],
    "archives": ["*.zip", "*.tar.gz", "*.7z", "archives/*", "archive/*", "Qumi_Deploy_Temp*"],
    "visuals": ["*.png", "*.jpg", "*.jpeg", "*.webp", "background_*.png"],
    "docs": ["Integrated_Thinking_OS_Paper.md", "Integrated_System_Specs.md", "QUICK_RECALL*.md"],
    "logs": ["*.txt", "gmail_out.txt", "large_tracked_files.txt", "tmp_objects.txt"]
}

def organize_lab():
    print("="*60)
    print(" [ ANTIGRAVITY LAB ORGANIZER ]")
    print(" 散らかったファイルをジャンル別に仕分け中...")
    print("="*60)
    
    os.chdir(BASE_PATH)
    
    for folder, patterns in TARGET_DIRS.items():
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[NEW] フォルダ '{folder}' を作成しました。")
            
        for pattern in patterns:
            for file in glob.glob(pattern):
                # Don't move already in folders
                if os.path.dirname(file):
                    continue
                # Don't move the scripts themselves
                if file.startswith("python_scripts") or file.endswith(".bat") or file.endswith(".vbs"):
                    continue
                    
                target_path = os.path.join(folder, file)
                try:
                    shutil.move(file, target_path)
                    print(f"[MOVE] {file} -> {folder}/")
                except Exception as e:
                    print(f"[SKIP] {file} ({e})")
                    
    print("\n[SUCCESS] ラボの整理整頓が完了しました！")

if __name__ == "__main__":
    organize_lab()
