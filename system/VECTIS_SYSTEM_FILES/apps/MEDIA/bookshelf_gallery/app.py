from flask import Flask, render_template, jsonify
import os
import glob
import re
import subprocess
import threading

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BOOKSHELF_DIR = ../../../OBSIDIAN_WRITING/BOOKSHELF
BOOKSHELF_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../OBSIDIAN_WRITING/BOOKSHELF"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books')
def get_books():
    books = []
    # Search all subfolders
    pattern = os.path.join(BOOKSHELF_DIR, "**/*.md")
    files = glob.glob(pattern, recursive=True)
    
    # Sort by modification time (newest first)
    files.sort(key=os.path.getmtime, reverse=True)
    
    for f in files[:50]: # Limit to 50 newest
        filename = os.path.basename(f)
        
        # Parse content for summary/tags (simple)
        desc = "No description"
        category = "General"
        
        try:
            with open(f, 'r', encoding='utf-8') as file_obj:
                content = file_obj.read(1000) # Read first 1000 chars
                # Try to find YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        # Extract tags
                        tag_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
                        if tag_match:
                            category = tag_match.group(1).replace("#", "").replace(",", " ").strip()
                
                # Extract first paragraph as desc
                body = content.split("---")[-1].strip()
                lines = body.split("\n")
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        desc = line.strip()[:100] + "..."
                        break
        except: pass

        books.append({
            "title": filename.replace(".md", ""),
            "desc": desc,
            "category": category,
            "path": f
        })
        
    return jsonify(books)

@app.route('/api/read/<path:book_path>')
def read_book(book_path):
    # Security check: ensure path is within bookshelf
    if not os.path.abspath(book_path).startswith(BOOKSHELF_DIR):
        return "Access Denied", 403
        
    try:
        with open(book_path, 'r', encoding='utf-8') as f:
            content = f.read()
            html_content = markdown_to_html_simple(content)
            return jsonify({"content": html_content})
    except Exception as e:
        return str(e), 500

    except Exception as e:
        return str(e), 500

@app.route('/api/patrol/chaos')
def trigger_chaos():
    return launch_app("03_JOB_PATROL.bat")

@app.route('/api/launch/<app_id>')
def launch_app_route(app_id):
    # Mapping of logical IDs to actual BAT files on Desktop
    # Assuming app.py is 4 levels deep: apps/MEDIA/bookshelf_gallery/app.py -> Desktop/app
    
    app_map = {
        "driving": "02_DRIVING_AI.bat",
        "patrol": "03_JOB_PATROL.bat",
        "es": "04_ES_WRITER.bat",
        "ego": "05_MY_EGO.bat",
        "chat": "06_CHAT_ROOM.bat",
        "router": "07_TEXT_ROUTER.bat",
        "main": "01_EGO_MAIN_SYSTEM.bat"
    }

    target = app_map.get(app_id)
    if not target:
        # Fallback: maybe they passed the bat name directly?
        return jsonify({"status": "Error", "message": "Unknown Application ID"}), 404
        
    def run_launcher():
        # Path to bat file relative to apps/MEDIA/bookshelf_gallery/app.py
        # ../../../../ points to c:\Users\Yuto\Desktop\app
        bat_path = os.path.abspath(os.path.join(BASE_DIR, "../../../../" + target))
        
        if os.path.exists(bat_path):
            print(f"Launching {bat_path}...")
            # Use 'start' command to launch purely redundant independent process
            # "start" in shell needs an empty title argument first: start "" "path"
            subprocess.run(f'start "" "{bat_path}"', shell=True) 
        else:
            print(f"File not found: {bat_path}")

    thread = threading.Thread(target=run_launcher)
    thread.start()
    
    return jsonify({"status": "Launched", "message": f"System Launching: {target}"})

@app.route('/api/all_apps')
def get_all_apps():
    # Scans EGO_SYSTEM_FILES/apps for all sub-apps
    apps_root = os.path.abspath(os.path.join(BASE_DIR, "../../")) # apps/
    
    found_apps = []
    
    # Categories to scan
    categories = ["MEDIA", "UTILS", "AI_LAB"] # "SYSTEM" is usually internal items
    
    for cat in categories:
        cat_path = os.path.join(apps_root, cat)
        if os.path.exists(cat_path):
            for item in os.listdir(cat_path):
                app_path = os.path.join(cat_path, item)
                if os.path.isdir(app_path):
                    # Check if it looks like an app (has .py, .html, .js)
                    has_entry = False
                    entry_script = ""
                    entry_type = "unknown"
                    
                    # Heuristic for entry point
                    if os.path.exists(os.path.join(app_path, "run_cli.py")):
                        has_entry = True; entry_script = "run_cli.py"; entry_type="cli"
                    elif os.path.exists(os.path.join(app_path, "app.py")):
                        has_entry = True; entry_script = "app.py"; entry_type="gui"
                    elif os.path.exists(os.path.join(app_path, "main.py")):
                        has_entry = True; entry_script = "main.py"; entry_type="gui"
                    elif os.path.exists(os.path.join(app_path, "index.html")):
                        has_entry = True; entry_script = "index.html"; entry_type="web"
                        
                    if has_entry:
                        found_apps.append({
                            "id": item,
                            "name": item.replace("_", " ").title(),
                            "category": cat,
                            "path": os.path.join(cat, item, entry_script).replace("\\", "/"),
                            "type": entry_type
                        })
    
    return jsonify(found_apps)

@app.route('/api/launch_direct')
def launch_direct():
    # Launches a script from apps/ folder directly
    # Query param: path (e.g. MEDIA/youtube_channel/run_cli.py)
    from flask import request
    target_rel = request.args.get('path')
    if not target_rel: return "Missing path", 400
    
    def run_spawn():
        # Construct full path
        apps_root = os.path.abspath(os.path.join(BASE_DIR, "../../"))
        full_path = os.path.join(apps_root, target_rel)
        
        if not os.path.exists(full_path):
            print(f"Not found: {full_path}")
            return

        cmd = ""
        wd = os.path.dirname(full_path)
        
        if full_path.endswith(".py"):
            # If CLI, needs terminal. If GUI, pythonw generally better but let's stick to python for stability.
            # Using 'start cmd /k' keeps window open for CLIs
            cmd = f'start "{target_rel}" cmd /k python "{full_path}"'
        elif full_path.endswith(".html"):
            cmd = f'start "" "{full_path}"'
            
        if cmd:
            subprocess.run(cmd, shell=True, cwd=wd)

    thread = threading.Thread(target=run_spawn)
    thread.start()
    return jsonify({"status": "Launched", "message": f"Opening {target_rel}..."})

def markdown_to_html_simple(md):
    try:
        import markdown
        return markdown.markdown(md, extensions=['fenced_code', 'tables'])
    except ImportError:
        import html
        return f"<pre style='white-space: pre-wrap; font-family: inherit; color: #ddd;'>{html.escape(md)}</pre>"

if __name__ == '__main__':
    print(f"Bookshelf Dir: {BOOKSHELF_DIR}")
    app.run(port=5050, debug=True)
