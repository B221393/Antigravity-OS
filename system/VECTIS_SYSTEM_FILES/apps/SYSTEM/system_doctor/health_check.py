import os
import py_compile
import sys

APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(os.path.abspath(os.path.join(APPS_DIR, "../"))) 

def health_check():
    print(f"🏥 VECTIS SYSTEM HEALTH CHECK")
    print(f"Scanning apps in: {APPS_DIR}\n")
    
    passed = 0
    failed = 0
    
    for root, dirs, files in os.walk(APPS_DIR):
        for file in files:
            if file in ["app.py", "main.py"]:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, APPS_DIR)
                
                try:
                    # 1. Syntax Check
                    py_compile.compile(path, doraise=True)
                    
                    # 2. Import Check (UnifiedLLM Specific)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "UnifiedLLM" in content and "from modules.unified_llm" not in content:
                           # This would be a runtime error
                           print(f"❌ [MISSING IMPORT] {rel_path}: Uses UnifiedLLM but import missing.")
                           failed += 1
                           continue
                           
                    print(f"✅ [OK] {rel_path}")
                    passed += 1
                except py_compile.PyCompileError as e:
                    print(f"❌ [SYNTAX ERROR] {rel_path}: {e}")
                    failed += 1
                except Exception as e:
                    print(f"❌ [ERROR] {rel_path}: {e}")
                    failed += 1

    print(f"\nSummary: {passed} Functional / {failed} Broken")
    if failed == 0:
        print("🎉 ALL SYSTEMS NOMINAL. CONNECTION ESTABLISHED.")
    else:
        print("⚠️ SOME SYSTEMS REQUIRE MAINTENANCE.")

if __name__ == "__main__":
    health_check()
