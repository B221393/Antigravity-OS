import os
import sys

# TARGET DIRECTORY
APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
MODULE_IMPORT_LINE = "from modules.unified_llm import UnifiedLLM"

def scan_and_upgrade():
    print(f"Starting VECTIS Mass Upgrade in: {APPS_DIR}")
    count = 0
    
    for root, dirs, files in os.walk(APPS_DIR):
        for file in files:
            if file in ["app.py", "main.py", "run_cli.py"]:
                target_path = os.path.join(root, file)
                process_file(target_path)
                count += 1
                
    print(f"Scan complete. Processed {count} applications.")

def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        original_content = content
        modified = False
        
        # 1. Replace Gemini Logic
        if "from modules.gemini_client import GenerativeModel" in content:
            content = content.replace("from modules.gemini_client import GenerativeModel", "from modules.unified_llm import UnifiedLLM")
            modified = True
            
        if "model = GenerativeModel(" in content:
            # Simple regex-like replacement for initialization
            import re
            content = re.sub(r"model\s*=\s*GenerativeModel\(['\"].*?['\"]\)", 
                             'model = UnifiedLLM(provider="ollama", model_name="phi4")', content)
            modified = True

        # 2. Replace generic create_llm_client if it's not specifying phi4
        # (This is a heuristic, we default to forcing the new explicit init)
        if "create_llm_client()" in content:
            content = content.replace("create_llm_client()", 'UnifiedLLM(provider="ollama", model_name="phi4")')
            # Check if import is needed
            if "from modules.unified_llm import UnifiedLLM" not in content:
                content = content.replace("from modules.unified_llm import create_llm_client", 
                                          "from modules.unified_llm import UnifiedLLM")
            modified = True

        # 3. Inject Import if missing but UnifiedLLM is used
        if "UnifiedLLM" in content and "from modules.unified_llm import UnifiedLLM" not in content:
            # Attempt to add import after sys.path appends
            if "import sys" in content:
                # Add after sys path append block usually found in VECTIS apps
                pass # Complex to insert safely, assuming replacements above handled imports
            
        if modified and content != original_content:
            print(f"[UPGRADING] {os.path.basename(os.path.dirname(filepath))}/{os.path.basename(filepath)}")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
    except Exception as e:
        print(f"[ERROR] processing {filepath}: {e}")

if __name__ == "__main__":
    scan_and_upgrade()
