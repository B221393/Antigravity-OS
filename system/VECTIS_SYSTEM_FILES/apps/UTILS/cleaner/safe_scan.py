import os

def scan_directory(directory, min_size_mb=100):
    """Scans a directory for files larger than min_size_mb."""
    print(f"Scanning {directory} for files larger than {min_size_mb}MB...")
    large_files = []
    try:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            return []
            
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    if size_mb > min_size_mb:
                        large_files.append((filepath, size_mb))
                except Exception as e:
                    pass # Skip access errors
    except Exception as e:
        print(f"Error scanning {directory}: {e}")
    return large_files

def main():
    print("=== VECTIS SAFE FILE SYSTEM SCANNER ===")
    print("This tool identifies large files but does NOT delete them automatically.")
    print("Safety Protocols: ACTIVE (No unexpected deletions allowed)")
    
    user_home = os.path.expanduser("~")
    target_dirs = [
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Desktop"),
        os.path.join(os.getcwd(), "tmp") # VECTIS temp
    ]
    
    all_large_files = []
    
    for d in target_dirs:
        found = scan_directory(d)
        all_large_files.extend(found)
        
    print("\n--- LARGE FILE REPORT (Candidates for Cleanup) ---")
    if not all_large_files:
        print("No large files (>100MB) found in scanned directories.")
    else:
        # Sort by size
        all_large_files.sort(key=lambda x: x[1], reverse=True)
        
        for path, size in all_large_files[:20]:
            print(f"[{size:.1f} MB] {path}")
            
    print("\n[INSTRUCTION]")
    print("Please delete these files manually if they are 'iranai' (unnecessary).")
    print("Use 'del <path>' in terminal if you are sure.")
    
if __name__ == "__main__":
    main()
