"""
EGO UI Module Applicator
===========================
This script scans all apps in the EGO_SYSTEM_FILES/apps directory and ensures they import
and use the shared UI module (vectis_ui_modules.py).

For Streamlit apps: Ensures apply_vectis_style() is called.
For Tkinter apps: Ensures VectisUIFactory is used.

Run: python apply_ui_module.py
"""

import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(ROOT_DIR, "apps")
UI_MODULE_PATH = os.path.join(ROOT_DIR, "vectis_ui_modules.py")

# Standard import line to add
IMPORT_LINE_STREAMLIT = """
# EGO共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
"""

IMPORT_LINE_TKINTER = """
# EGO共通UIモジュール
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from vectis_ui_modules import VectisUIFactory, setup_style
except ImportError:
    pass
"""

def scan_apps():
    """Get all Python app files"""
    apps = []
    for cat in os.listdir(APPS_DIR):
        cat_path = os.path.join(APPS_DIR, cat)
        if not os.path.isdir(cat_path) or cat.startswith("_"):
            continue
        for app_name in os.listdir(cat_path):
            app_path = os.path.join(cat_path, app_name)
            if not os.path.isdir(app_path):
                continue
            # Check for app.py or main.py
            for entry in ["app.py", "main.py"]:
                entry_path = os.path.join(app_path, entry)
                if os.path.exists(entry_path):
                    apps.append({
                        "category": cat,
                        "name": app_name,
                        "path": entry_path
                    })
                    break
    return apps

def detect_app_type(content):
    """Detect if app is Streamlit or Tkinter"""
    if "streamlit" in content.lower() or "import st" in content:
        return "streamlit"
    elif "tkinter" in content.lower() or "import tk" in content:
        return "tkinter"
    return "unknown"

def check_has_vectis_style(content):
    """Check if file already imports vectis style"""
    patterns = [
        "apply_vectis_style",
        "vectis_ui_modules",
        "VectisUIFactory"
    ]
    return any(p in content for p in patterns)

def apply_ui_module(app_info, dry_run=True):
    """Apply UI module to an app"""
    with open(app_info["path"], "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    app_type = detect_app_type(content)
    has_style = check_has_vectis_style(content)
    
    result = {
        "app": app_info["name"],
        "type": app_type,
        "has_style": has_style,
        "modified": False
    }
    
    if has_style:
        result["status"] = "SKIP (already has EGO style)"
        return result
    
    if app_type == "streamlit":
        # Add import after first import block
        if "import os" in content:
            new_content = content.replace("import os", "import os\n" + IMPORT_LINE_STREAMLIT.strip(), 1)
            result["modified"] = True
        else:
            result["status"] = "SKIP (no standard import block found)"
            return result
    elif app_type == "tkinter":
        if "import tkinter" in content:
            new_content = content.replace("import tkinter", "import tkinter\n" + IMPORT_LINE_TKINTER.strip(), 1)
            result["modified"] = True
        else:
            result["status"] = "SKIP (no tkinter import found)"
            return result
    else:
        result["status"] = f"SKIP (unknown type: {app_type})"
        return result
    
    if result["modified"]:
        if not dry_run:
            with open(app_info["path"], "w", encoding="utf-8") as f:
                f.write(new_content)
            result["status"] = "MODIFIED"
        else:
            result["status"] = "WOULD MODIFY (dry run)"
    
    return result

def main():
    print("=" * 60)
    print("EGO UI Module Applicator")
    print("=" * 60)
    
    apps = scan_apps()
    print(f"\nFound {len(apps)} apps to process.\n")
    
    # Dry run first
    results = []
    modified_count = 0
    skip_count = 0
    
    for app in apps:
        result = apply_ui_module(app, dry_run=True)
        results.append(result)
        if result["modified"]:
            modified_count += 1
        else:
            skip_count += 1
        print(f"[{result['type']:10}] {app['category']:15} / {app['name']:25} -> {result['status']}")
    
    print("\n" + "=" * 60)
    print(f"Summary: {modified_count} to modify, {skip_count} skipped")
    print("=" * 60)
    
    if modified_count > 0:
        confirm = input("\nApply changes? [y/N]: ")
        if confirm.lower() == "y":
            for app in apps:
                result = apply_ui_module(app, dry_run=False)
                if result["modified"]:
                    print(f"✅ Modified: {app['name']}")
            print("\nDone!")
        else:
            print("Cancelled.")
    else:
        print("\nNo changes needed.")

if __name__ == "__main__":
    main()
