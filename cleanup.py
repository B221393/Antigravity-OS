#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def cleanup():
    base_path = Path("C:/Users/Yuto/Desktop/app")
    
    # Directories to remove
    dirs_to_remove = [
        base_path / ".venv",
        base_path / "RUST_PROJECTS/vectis-station-rs/src-tauri/target",
        base_path / ".git/index.lock",
    ]
    
    for dir_path in dirs_to_remove:
        if dir_path.exists():
            try:
                if dir_path.is_file():
                    dir_path.unlink()
                    print(f"Deleted file: {dir_path}")
                else:
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
            except Exception as e:
                print(f"Error deleting {dir_path}: {e}")
    
    # Remove node_modules and __pycache__ recursively
    for root, dirs, files in os.walk(base_path):
        if "node_modules" in dirs:
            node_modules_path = Path(root) / "node_modules"
            try:
                shutil.rmtree(node_modules_path)
                print(f"Deleted directory: {node_modules_path}")
            except Exception as e:
                print(f"Error deleting {node_modules_path}: {e}")
            dirs.remove("node_modules")
        
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                print(f"Deleted directory: {pycache_path}")
            except Exception as e:
                print(f"Error deleting {pycache_path}: {e}")
            dirs.remove("__pycache__")
        
        if ".pytest_cache" in dirs:
            pytest_cache_path = Path(root) / ".pytest_cache"
            try:
                shutil.rmtree(pytest_cache_path)
                print(f"Deleted directory: {pytest_cache_path}")
            except Exception as e:
                print(f"Error deleting {pytest_cache_path}: {e}")
            dirs.remove(".pytest_cache")
    
    print("Cleanup completed!")

if __name__ == "__main__":
    cleanup()
