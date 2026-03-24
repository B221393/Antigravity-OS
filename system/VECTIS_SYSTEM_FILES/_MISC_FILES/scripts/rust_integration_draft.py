import os
import sys
import subprocess
import logging
from error_relay import ErrorRelay

# ... (Previous imports + new Rust integration)

# Standardize path to Rust Matcher
RUST_MATCHER_EXE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/rust_matcher/target/release/rust_matcher.exe"))
KEYWORDS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../AUTO_YOUTUBE/MY_KEYWORDS.txt"))

def rust_match(target_text):
    """Call the Rust binary to check keywords quickly."""
    if not os.path.exists(RUST_MATCHER_EXE):
        return None # Fallback to python if not compiled
        
    try:
        # Run rust_matcher --keywords ... --target ...
        cmd = [
            RUST_MATCHER_EXE,
            "--keywords", KEYWORDS_FILE,
            "--target", target_text
        ]
        # Hide window on Windows
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si, encoding='utf-8')
        output = result.stdout.strip()
        
        if output == "NO_MATCH":
            return []
        else:
            return output.split(",")
            
    except Exception as e:
        print(f"Rust Matcher Error: {e}")
        return None

# ... (Existing watcher logic, but replacing the slow python keyword loop with rust_match call)
# Since the file is large, I will construct a minimal robust version that USES the rust matcher 
# instead of replacing the whole file, to avoid breaking scrapetube logic.
# Wait, I must modify the EXISTING watcher_youtube.py.
# I will use multi_replace to inject the rust helper and modify the matching function.
