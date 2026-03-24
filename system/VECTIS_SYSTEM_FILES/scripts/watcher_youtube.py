import sys
import os

# Legacy Bridge for Watcher
# Points to the new location in _MISC_FILES
target = os.path.abspath(os.path.join(os.path.dirname(__file__), "../_MISC_FILES/scripts/watcher_youtube.py"))
if os.path.exists(target):
    with open(target, 'r', encoding='utf-8') as f:
        exec(f.read())
else:
    print(f"CRITICAL ERROR: Legacy bridge cannot find actual script at {target}")
