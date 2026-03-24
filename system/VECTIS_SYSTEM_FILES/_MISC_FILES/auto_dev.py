import os
import time
import subprocess
import requests
import json
import re
import sys
import glob

# ==========================================
# CONFIGURATION
# ==========================================
# Attempt to find running Ollama or default
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3" #Change this to 'phi3', 'mistral', 'gemma' etc. if needed
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Tasks: Polishing Apps 40-100 with Rust/UI improvements
TASK_LIST = [
    # Business & Finance
    "apps/market_watch/app.py に、Yahoo Finance API (yfinance) を使って株価を取得・表示する機能を追加せよ。エラー処理もしっかり書くこと。",
    "apps/password_forge/app.py に、'Memorable Password' (単語の組み合わせ) 生成モードを追加せよ。",
    "apps/color_alchemy/app.py に、補色(Complementary)と類似色(Analogous)を計算して表示するパレット機能を追加せよ。",
    "apps/zen_focus/app.py に、雨音や焚き火音の環境音(mp3)を再生するプレイヤーUIを追加せよ(ファイルがない場合はプレースホルダー表示)。",
    "apps/quick_qr/app.py に、生成したQRコードをPNGとしてダウンロードするボタンを追加せよ。",
    
    # Utilities
    "apps/base_master/app.py に、32進数(Base32)の変換機能を追加せよ。",
    "apps/ascii_artist/app.py に、画像のコントラスト調整スライダーを追加してからASCII変換するように改良せよ。",
    "apps/snippet_hub/app.py に、スニペットをクリップボードにコピーするボタン(st.codeの横には標準であるので、独自ボタンでToast表示)を追加せよ。",
    "apps/era_gengo/app.py に、西暦を入力すると干支(Eto)を表示する機能を追加せよ。",
    "apps/unit_master/app.py に、データサイズ(KB, MB, GB)の変換タブを追加せよ。",
    
    # Advanced
    "apps/decision_matrix/app.py に、評価結果のランキングを棒グラフで可視化する機能を追加せよ。",
    "apps/shift_maker/app.py に、CSV形式でのシフト表エクスポート機能を追加せよ。",
    "apps/risk_register/app.py に、リスクレベル(高・中・低)に応じた行の色分け表示機能を追加せよ。",
    "apps/time_zone_mate/app.py に、主要都市(NY, London, Tokyo, Sydney)の現在時刻をアナログ時計風またはデジタルで並べて表示せよ。",
    
    # System & Bridge
    "apps/memory_viewer/app.py に、特定のキーワードを含む記憶だけを絞り込む検索ボックスを追加せよ。",
    "apps/tube_stats/app.py に、視聴時間の『曜日別ヒートマップ』を表示する機能を追加せよ。",
]

# ==========================================
# AGENT LOGIC
# ==========================================

def log(msg):
    print(f"\033[92m[VECTIS AUTO]\033[0m {msg}")

def ask_ollama(prompt):
    """Call Ollama to write code"""
    log(f"🧠 Thinking about: {prompt[:50]}...")
    
    # VECTIS Context
    full_prompt = (
        "You are an expert Python developer working on 'VECTIS OS'.\n"
        "Your goal is to modify/create Streamlit apps.\n"
        "Output ONLY the complete python code for the file.\n"
        "Do not use markdown blocks like ```python. Just raw code or code in ```.\n"
        "Start with 'import streamlit as st'.\n"
        "Include broad error handling (try-except) to prevent crashes.\n\n"
        f"Request: {prompt}"
    )
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False
        }, timeout=180)
        
        if response.status_code != 200:
            log(f"❌ Ollama Error: {response.text}")
            return None
            
        res_text = response.json().get('response', '')
        
        # Extract Code Block
        code_match = re.search(r"```(?:python)?(.*?)```", res_text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Fallback: if starts with import, assume raw
        if res_text.strip().startswith("import"):
            return res_text.strip()
            
        return res_text.strip()
        
    except Exception as e:
        log(f"❌ Connection Error: {e}")
        return None

def write_file(filepath, content):
    """Save Code"""
    full_path = os.path.join(PROJECT_ROOT, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"💾 Wrote to {filepath}")

def run_test(filepath):
    """Syntax Check (Compile)"""
    log("🧪 Running Verification...")
    full_path = os.path.join(PROJECT_ROOT, filepath)
    try:
        # Syntax check only
        with open(full_path, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, full_path, 'exec')
        log("✅ Syntax: GREEN")
        return True, ""
    except Exception as e:
        log("❌ Syntax: RED")
        return False, str(e)

def main_loop():
    log("🚀 VECTIS AUTOPILOT ENGAGED")
    log(f"🎯 Target: {len(TASK_LIST)} Tasks")
    log(f"🤖 Model: {MODEL}")
    
    start_time = time.time()
    
    for i, task in enumerate(TASK_LIST):
        # Time check (e.g. 3 hours)
        if time.time() - start_time > 3 * 3600:
            log("⏱️ Time limit reached.")
            break

        log(f"\n--- Task {i+1}/{len(TASK_LIST)} ---")
        log(f"Objective: {task}")
        
        # Extract target file path (first word)
        target_file = task.split(" ")[0]
        
        # Generate
        code = ask_ollama(task)
        if not code:
            log("⚠️ Skipping due to generation failure.")
            continue
            
        # Write
        write_file(target_file, code)
        
        # Test & Fix Loop
        retry_count = 0
        while retry_count < 3:
            success, error_msg = run_test(target_file)
            if success:
                break
            
            log(f"🔧 Fixing Error ({retry_count+1}/3): {error_msg[:100]}...")
            fix_prompt = f"The code for {target_file} has a syntax error:\n{error_msg}\nFix the code and return the FULL file content."
            code = ask_ollama(fix_prompt)
            if code:
                write_file(target_file, code)
            retry_count += 1
            
    log("🏁 Mission Complete. All systems upgraded.")

if __name__ == "__main__":
    # Check dependencies
    try:
        import requests
    except:
        print("Installing requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

    main_loop()
