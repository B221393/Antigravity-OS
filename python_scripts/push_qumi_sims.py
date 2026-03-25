import os
import sys
import json
import base64
import urllib.request
import urllib.error

TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set.")
    sys.exit(1)

REPO = "B221393/Qumi"
BRANCH = "main"

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['object']['sha']
    except Exception as e:
        print(f"Error getting latest commit: {e}")
        sys.exit(1)

def get_tree_sha(commit_sha):
    url = f"https://api.github.com/repos/{REPO}/git/commits/{commit_sha}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['tree']['sha']
    except Exception as e:
        print(f"Error getting tree sha: {e}")
        sys.exit(1)

def create_blob(content):
    url = f"https://api.github.com/repos/{REPO}/git/blobs"
    data = json.dumps({
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "encoding": "base64"
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['sha']
    except Exception as e:
        print(f"Error creating blob: {e}")
        sys.exit(1)

def create_tree(base_tree_sha, tree_data):
    url = f"https://api.github.com/repos/{REPO}/git/trees"
    data = json.dumps({
        "base_tree": base_tree_sha,
        "tree": tree_data
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['sha']
    except Exception as e:
        print(f"Error creating tree: {e}")
        sys.exit(1)

def create_commit(message, tree_sha, parent_sha):
    url = f"https://api.github.com/repos/{REPO}/git/commits"
    data = json.dumps({
        "message": message,
        "tree": tree_sha,
        "parents": [parent_sha]
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['sha']
    except Exception as e:
        print(f"Error creating commit: {e}")
        sys.exit(1)

def update_ref(commit_sha):
    url = f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}"
    data = json.dumps({
        "sha": commit_sha,
        "force": False
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}, method="PATCH")
    try:
        with urllib.request.urlopen(req) as response:
            print("Successfully updated reference.")
    except Exception as e:
        print(f"Error updating ref: {e}")
        sys.exit(1)

def main():
    print("Starting deployment of simulation files...")
    latest_commit_sha = get_latest_commit_sha()
    base_tree_sha = get_tree_sha(latest_commit_sha)

    tree_data = []
    sims_dir = r"Qumi_Core\frontend\public\sims"
    
    for filename in os.listdir(sims_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(sims_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            blob_sha = create_blob(content)
            tree_data.append({
                "path": f"ui/public/sims/{filename}",
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })
            print(f"Uploaded {filename}")

    new_tree_sha = create_tree(base_tree_sha, tree_data)
    new_commit_sha = create_commit("feat: upload all 16 simulation files for ui/public/sims/", new_tree_sha, latest_commit_sha)
    update_ref(new_commit_sha)
    print("All files pushed successfully!")

if __name__ == "__main__":
    main()
