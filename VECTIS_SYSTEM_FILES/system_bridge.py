
import os
import subprocess
import webbrowser
import threading
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Base directory (Root of the project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'EGO_OS.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route('/api/launch', methods=['POST'])
def launch_app():
    data = request.json
    app_path = data.get('path')
    app_type = data.get('type', 'python')
    
    if not app_path:
        return jsonify({"status": "error", "message": "No path provided"}), 400
    
    # ========== SECURITY: WHITELIST CHECK ==========
    # Only allow launching apps registered in APP_REGISTRY
    ALLOWED_APPS = [
        "AI_LAB/racing_game/racing_game.html",
        "AI_LAB/driving_3d/driving_3d.html",
        "AI_LAB/shogi_dojo/app.py",
        "AI_LAB/text_router/index.html",
        "AI_LAB/knowledge_cards/control_center.html",
        "AI_LAB/vectis_omni/app.py",
        "MEDIA/youtube_channel/app.py",
        "MEDIA/youtube_channel/run_cli.py",
        "MEDIA/news_aggregator/app.py",
        "UTILS/todo/app.py",
        "UTILS/scheduler/index.html",
        "UTILS/job_hunting/index.html",
        "UTILS/book_log/index.html",
        "SYSTEM/system_monitor/app.py",
        "SYSTEM/process_killer/app.py",
    ]
    
    # Normalize and check
    normalized_path = app_path.replace("\\", "/")
    if normalized_path not in ALLOWED_APPS:
        return jsonify({"status": "error", "message": f"SECURITY: App not in whitelist: {app_path}"}), 403
    # ================================================
        
    full_path = os.path.join(BASE_DIR, "EGO_SYSTEM_FILES", "apps", app_path)
    
    # Normalize path
    full_path = os.path.normpath(full_path)
    
    if not os.path.exists(full_path):
        return jsonify({"status": "error", "message": f"Path not found: {full_path}"}), 404

    try:
        if app_type == 'python':
            # Use pythonw to run without console if preferred, or python for console
            # For interactive apps (CLI), we need a new console
            subprocess.Popen(f'start cmd /k python "{full_path}"', shell=True)
            return jsonify({"status": "success", "message": f"Launched {full_path}"})
            
        elif app_type == 'bat':
            subprocess.Popen(f'start "" "{full_path}"', shell=True)
            return jsonify({"status": "success", "message": f"Launched batch {full_path}"})
            
        elif app_type == 'html':
            # Open in new tab or handle in frontend
            # The frontend usually handles HTML via iframe, but if we want to 'launch' it in system browser:
            webbrowser.open(f'file://{full_path}')
            return jsonify({"status": "success", "message": f"Opened HTML in browser"})

        else:
             return jsonify({"status": "error", "message": "Unknown type"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_file():
    data = request.json
    file_path = data.get('path')
    content = data.get('content')
    
    if not file_path or content is None:
        return jsonify({"status": "error", "message": "Missing path or content"}), 400
        
    # Security: Ensure saving within EGO_SYSTEM_FILES
    abs_path = os.path.abspath(os.path.join(BASE_DIR, "EGO_SYSTEM_FILES", file_path))
    if not abs_path.startswith(os.path.join(BASE_DIR, "EGO_SYSTEM_FILES")):
         return jsonify({"status": "error", "message": "Access denied: Path outside safe area"}), 403

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        # Smart Saving: If file exists and content is a list/dict, check if we should append
        if os.path.exists(abs_path) and isinstance(content, dict):
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                
                # If both are lists, merge
                if isinstance(existing, list):
                    existing.append(content)
                    content = existing
                # If specific known files (schedule/todo), handle their structures
                elif isinstance(existing, dict) and "inbox" in existing:
                    existing["inbox"].insert(0, content)
                    content = existing
            except: pass # Fallback to overwrite if corrupt

        import json
        with open(abs_path, 'w', encoding='utf-8') as f:
            if isinstance(content, (dict, list)):
                json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                f.write(str(content))
                
        return jsonify({"status": "success", "message": f"Saved and synced to {file_path}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ai', methods=['POST'])
def call_ai():
    import urllib.request
    import json
    
    data = request.json
    model = data.get('model', 'gemma:2b')
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400

    try:
        # --- RAG IMPLEMENTATION ---
        # 1. Load Universe Data
        rag_context = ""
        universe_path = os.path.join(BASE_DIR, "EGO_SYSTEM_FILES", "apps", "MEDIA", "youtube_channel", "data", "universe.json")
        try:
            if os.path.exists(universe_path):
                with open(universe_path, 'r', encoding='utf-8') as f:
                    u_data = json.load(f)
                    # Get recent/important nodes
                    nodes = u_data.get('nodes', [])
                    # Sort by newness or importance (using timestamp desc)
                    nodes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    top_nodes = nodes[:15] # Top 15 items
                    
                    rag_context = "【システム参照情報 (RAG)】\n"
                    for n in top_nodes:
                        rag_context += f"- [{n.get('group')}] {n.get('title')}: {n.get('summary')}\n"
        except Exception as e:
            print(f"RAG Error: {e}")

        # 2. Construct Enhanced Prompt
        system_instruction = f"""
あなたは EGO OS の「マスター・システム・ルーター」です。
ユーザーの入力を解析し、最適なアプリへの自動振り分け（ルーティング）と回答を行ってください。

【利用可能なアプリ一覧】
- `todo`: タスク管理。やること、忘備録、期限なしのタスク。
- `schedule`: カレンダー。具体的な日時（明日、3月10日、15時〜など）がある予定。
- `knowledge`: 知識ベース。ニュース、技術情報、定義、恒久的に保存したい情報。
- `shukatsu`: 就活トラッカー。ES締切、説明会、企業研究、キャリア関連。
- `racing` / `driving`: AI運転・レースシミュレーターの起動。
- `youtube`: 動画検索やチャンネル監視の指示。
- `shogi`: 将棋の対戦や検討。

【返答ルール】
1. **言語**: 必ず「日本語」のみ。
2. **形式**: 下記のJSONフォーマットのみ。
3. **仕分け**: 入力が特定のアプリ（Todo, 予定, 知識など）にふさわしい場合、`target_app` を指定し、`item_data` に保存用の整形データを抽出してください。

JSONフォーマット:
{{
  "reply": "ユーザーへの挨拶や短い説明（日本語）",
  "action": "chat" (雑談) または "launch" (アプリ起動) または "route" (データ送信のみ) または "ask_route" (送信するか確認),
  "target_app": "アプリID (todo, schedule, knowledge, etc...)",
  "item_data": {{
    "title": "要約タイトル",
    "details": "詳細内容",
    "date": "YYYY-MM-DD (予定の場合)",
    "time": "HH:MM (予定の場合)"
  }}
}}

{rag_context}

ユーザーの質問: "{prompt}"
"""

        # Proxy to Ollama
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": system_instruction,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.3 # Low temperature for stability
            }
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "note": "Is Ollama running?"}), 500

def open_browser():
    # Wait a bit for server to start
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("🚀 EGO SYSTEM BRIDGE starting...")
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000)
