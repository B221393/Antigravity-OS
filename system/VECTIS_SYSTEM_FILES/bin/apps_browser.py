import os
import sys
import subprocess
import random
from pathlib import Path

# Base directory for VECTIS apps
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "apps"

# Curated lists for "Store-like" feel
FEATURED_APPS = [
    "MEDIA/INTELLIGENCE_HUB/VECTIS_SHUKATSU_HQ_APP.py", # Job Hunting HQ
    "GAMES/dt_cannon/app.py", # Stress Relief
    "AI_LAB/shogi_dojo/app.py", # Brain Training
    "MEDIA/image_diet/app.py", # Utility
    "AI_LAB/es_assistant/app.py" # Career
]

CATEGORIES = {
    "AI_LAB": "🧠 AI Research & Lab",
    "GAMES": "🎮 Games & Relax",
    "MEDIA": "🎨 Creative & Media",
    "SYSTEM": "⚙️ System Tools",
    "UTILS": "🛠️ Utilities"
}

def find_all_apps():
    """Recursively find all runnable apps (app.py)"""
    apps = []
    for root, dirs, files in os.walk(BASE_DIR):
        if 'app.py' in files or 'VECTIS_SHUKATSU_HQ_APP.py' in files:
            # Handle special case for HQ App
            filename = 'VECTIS_SHUKATSU_HQ_APP.py' if 'VECTIS_SHUKATSU_HQ_APP.py' in files else 'app.py'
            
            path = Path(root) / filename
            try:
                rel_path = path.relative_to(BASE_DIR)
                category_key = rel_path.parts[0]
                category_name = CATEGORIES.get(category_key, category_key)
                
                # Prettify Name
                raw_name = rel_path.parent.name.replace('_', ' ').title()
                if filename == 'VECTIS_SHUKATSU_HQ_APP.py':
                    raw_name = "VECTIS Shukatsu HQ"
                
                apps.append({
                    'id': str(rel_path),
                    'name': raw_name,
                    'category_key': category_key,
                    'category': category_name,
                    'path': str(path),
                    'rel_path': str(rel_path)
                })
            except ValueError:
                continue
    return apps

def run_app(app_path):
    """Run the selected app"""
    print(f"\n🚀 Launching {os.path.basename(app_path)} ...\n")
    try:
        python_exe = sys.executable
        cwd = os.path.dirname(app_path)
        
        # Check for dependencies (simple check)
        subprocess.run([python_exe, app_path], cwd=cwd, check=False)
    except Exception as e:
        print(f"❌ Error launching app: {e}")
    
    input("\nPress Enter to return to Store...")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(f"╔════════════════════════════════════════════════════════════╗")
    print(f"║             🌌 VECTIS APP STORE (Console)                  ║")
    print(f"╚════════════════════════════════════════════════════════════╝")

    display_home(apps)

def display_home(apps):
    clear_screen()
    print_header()
    
    # 🔍 SEARCH IS NOW KING
    print(f"\n 🔍  SEARCH APPS (アプリを検索)")
    print(f" ─────────────────────────────────")
    print(f"   [1] ⌨️  キーワード検索 (Search by Name/Tag)")
    
    # 1. 🔥 Featured Section
    print(f"\n 🔥  FEATURED (おすすめ)")
    print(f" ─────────────────────────────────")
    
    featured_map = {}
    idx_counter = 2 # Start from 2 because Search is 1
    
    for f_path in FEATURED_APPS:
        normalized_f_path = str(Path(f_path)) 
        found = next((a for a in apps if str(Path(a['rel_path'])) == normalized_f_path), None)
        if found:
            print(f"   [{idx_counter}] 🌟 {found['name']:<25} ({found['category']})")
            featured_map[str(idx_counter)] = found
            idx_counter += 1
            
    # 2. 📂 Categories Section
    print(f"\n 📂  CATEGORIES (カテゴリ)")
    print(f" ─────────────────────────────────")
    cat_keys = sorted(list(set(a['category_key'] for a in apps)))
    
    cat_map = {}
    for i, key in enumerate(cat_keys):
        c_idx = idx_counter + i
        cat_name = CATEGORIES.get(key, key)
        count = len([a for a in apps if a['category_key'] == key])
        print(f"   [{c_idx}] {cat_name:<25} ({count} apps)")
        cat_map[str(c_idx)] = key
    
    print(f"\n [Q] Quit")
    print(f" ─────────────────────────────────")
    
    choice = input(" Select > ").strip().lower()
    
    if choice == 'q':
        return 'quit'
    elif choice == '1' or choice == 's' or choice == '': # Search is default
        display_search(apps)
        return 'home'
    elif choice in featured_map:
        run_app(featured_map[choice]['path'])
        return 'home'
    elif choice in cat_map:
        # display_category(apps, cat_map[choice]) # Assuming display_category exists or will be added
        print(f"\nCategory '{CATEGORIES.get(cat_map[choice])}' selected. (Functionality not yet implemented)")
        input("Press Enter to return...")
        return 'home'
    
    return 'home'

def main():
    apps = find_all_apps()
    while True:
        if display_home(apps) == 'quit':
            break

if __name__ == "__main__":
    main()
