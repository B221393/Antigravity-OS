import os
import sys
import traceback
import importlib.util
import subprocess

# Add system root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

ROOT_APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

def diagnose_apps():
    print("------- VECTIS SYSTEM DOCTOR: DIAGNOSIS START -------")
    print(f"Scanning Apps Directory: {ROOT_APPS_DIR}")
    
    apps = [d for d in os.listdir(ROOT_APPS_DIR) if os.path.isdir(os.path.join(ROOT_APPS_DIR, d))]
    
    warnings = []
    errors = []
    passed = 0
    
    print(f"Found {len(apps)} potential applications.")
    
    for app_name in apps:
        app_dir = os.path.join(ROOT_APPS_DIR, app_name)
        main_file = None
        
        # Check for entry point
        if os.path.exists(os.path.join(app_dir, "app.py")):
            main_file = os.path.join(app_dir, "app.py")
        elif os.path.exists(os.path.join(app_dir, "main.py")):
            main_file = os.path.join(app_dir, "main.py")
            
        if not main_file:
            # Not an app? Check if it's a util
            if not app_name.startswith("__") and not app_name == "system_doctor":
                 warnings.append(f"[{app_name}] No app.py or main.py found.")
            continue
            
        # 1. SYNTAX CHECK
        try:
            with open(main_file, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
            compile(source, main_file, 'exec')
        except SyntaxError as e:
            errors.append(f"[{app_name}] SYNTAX ERROR in {os.path.basename(main_file)}: {e}")
            continue
        except Exception as e:
            errors.append(f"[{app_name}] READ ERROR: {e}")
            continue
            
        # 2. IMPORT CHECK (Static analysis of imports)
        # We won't actually import them all as that would run code, but we can check if they are standard
        # For now, let's just mark it as 'Compiles OK'
        passed += 1
        # print(f"[{app_name}] OK")

    print("\n------- DIAGNOSIS RESULTS -------")
    print(f"✅ PASSED: {passed} / {len(apps)}")
    
    if warnings:
        print("\n⚠️ WARNINGS:")
        for w in warnings: print(w)
        
    if errors:
        print("\n❌ CRITICAL ERRORS:")
        for e in errors: print(e)
    else:
        print("\n✨ NO CRITICAL CODE ERRORS FOUND.")
        
    print("\n---------------------------------")
    
if __name__ == "__main__":
    diagnose_apps()
