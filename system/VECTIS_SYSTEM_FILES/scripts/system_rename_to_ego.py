
import os
import shutil
import fileinput

DRY_RUN = False  # Set to False to execute
TARGET_ROOT = r"c:\Users\Yuto\Desktop\app"
IGNORE_DIRS = {".git", ".venvs", ".venv", "node_modules", "__pycache__", ".vscode", "_ARCHIVE", "_ARCHIVE_FULL"}
TEXT_EXTENSIONS = {".py", ".md", ".txt", ".json", ".js", ".ts", ".rs", ".html", ".css", ".bat", ".sh", ".env", ".toml"}

def rename_directory(old_name, new_name):
    old_path = os.path.join(TARGET_ROOT, old_name)
    new_path = os.path.join(TARGET_ROOT, new_name)
    
    if os.path.exists(old_path):
        print(f"[DIR] Renaming {old_name} -> {new_name}")
        if not DRY_RUN:
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print(f"FAILED to rename directory: {e}")
    else:
        print(f"[SKIP] Directory {old_name} not found (maybe already renamed?)")

def replace_in_file(filepath):
    try:
        # Check specific ignores
        if "package-lock.json" in filepath or "yarn.lock" in filepath:
            return

        # Read content
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if "EGO" in content:
            print(f"[TEXT] Replacing content in: {filepath}")
            new_content = content.replace("EGO", "EGO")
            if not DRY_RUN:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def walk_and_process():
    # 1. Rename files and Process content
    for root, dirs, files in os.walk(TARGET_ROOT):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Text Replacement
            _, ext = os.path.splitext(filename)
            if ext in TEXT_EXTENSIONS or filename in ["GEMINI.md", "Dockerfile"]:
                replace_in_file(filepath)
            
            # Filename Renaming
            if "EGO" in filename:
                new_filename = filename.replace("EGO", "EGO")
                new_filepath = os.path.join(root, new_filename)
                print(f"[FILE_NAME] Renaming {filename} -> {new_filename}")
                if not DRY_RUN:
                    try:
                        os.rename(filepath, new_filepath)
                    except Exception as e:
                        print(f"FAILED to rename file: {e}")

if __name__ == "__main__":
    print("=== STARTING SYSTEM RENAMING (EGO -> EGO) ===")
    
    # 1. Rename Root System Folder
    rename_directory("EGO_SYSTEM_FILES", "EGO_SYSTEM_FILES")
    
    # 2. Rename root files
    rename_directory("EGO_STATUS.txt", "EGO_STATUS.txt")
    rename_directory("EGO_INTELLIGENCE_VIEWER.bat", "EGO_INTELLIGENCE_VIEWER.bat")

    # 3. Deep Process
    walk_and_process()
    
    print("=== COMPLETED ===")
