import os
import subprocess
from datetime import datetime

# Path to the local repository
repo_path = r"C:\Users\Yuto\Desktop\app"
os.chdir(repo_path)

def run_git_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(command)}: {e.stderr}")
        return None

def sync_with_github():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting sync...")
    
    # 1. Add all changes
    run_git_command(["git", "add", "."])
    
    # 2. Check for changes
    status = run_git_command(["git", "status", "--porcelain"])
    if not status:
        print("No changes detected. Sync skipped.")
        return

    # 3. Commit changes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Autonomous Sync: {timestamp}"
    run_git_command(["git", "commit", "-m", commit_message])
    
    # 4. Push to remote
    print("Pushing to GitHub (origin/main)...")
    run_git_command(["git", "push", "origin", "main"])
    print("Sync complete!")

if __name__ == "__main__":
    sync_with_github()
