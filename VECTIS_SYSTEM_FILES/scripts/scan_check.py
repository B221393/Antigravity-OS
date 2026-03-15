import os
import glob

ROOT_DIR = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES"
APPS_DIR = os.path.join(ROOT_DIR, "apps")

def scan_check():
    total_folders = 0
    detected_apps = 0
    missed_apps = []

    if not os.path.exists(APPS_DIR):
        print("Apps dir not found")
        return

    for category in os.listdir(APPS_DIR):
        cat_path = os.path.join(APPS_DIR, category)
        if os.path.isdir(cat_path) and not category.startswith("_"):
            for app_name in os.listdir(cat_path):
                app_path = os.path.join(cat_path, app_name)
                if not os.path.isdir(app_path):
                    continue
                
                total_folders += 1
                
                # Check detection logic
                entry_point = None
                if os.path.exists(os.path.join(app_path, "app.py")):
                    entry_point = "app.py"
                elif os.path.exists(os.path.join(app_path, "main.py")):
                    entry_point = "main.py"
                elif glob.glob(os.path.join(app_path, "*.bat")):
                    entry_point = "bat"
                
                if entry_point:
                    detected_apps += 1
                else:
                    # Check what files ARE there to improve logic
                    files = os.listdir(app_path)
                    files = [f for f in files if os.path.isfile(os.path.join(app_path, f))]
                    missed_apps.append(f"{category}/{app_name} (Files: {', '.join(files[:5])})")

    with open("scan_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Total App Folders: {total_folders}\n")
        f.write(f"Detected: {detected_apps}\n")
        f.write(f"Missed: {len(missed_apps)}\n\n")
        f.write("Missed Apps:\n")
        for app in missed_apps:
            f.write(f"- {app}\n")
    
    print("Scan complete. See scan_result.txt")

if __name__ == "__main__":
    scan_check()
