"""
EGO System Health Audit (CAMEL Discussion)
==============================================
30分に一度起動し、インテリジェンス収集が正常に動いているか
2人のAIエージェント（監査役とマネージャー）が議論し、報告します。
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, init

init() # Colorama

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../.."))
DATA_DIR = os.path.join(BASE_DIR, "../../MEDIA/youtube_channel/data")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")
QUEUE_FILE = os.path.join(DATA_DIR, "discovery_queue.json")
SHUKATSU_DIR = os.path.join(DATA_DIR, "shukatsu")

# API設定
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

sys.path.insert(0, os.path.join(ROOT_DIR, "EGO_SYSTEM_FILES"))
try:
    from modules.unified_llm_client import ask_llm
except:
    print(Fore.RED + "LLM Client not found" + Fore.RESET)
    exit(1)

def get_file_stats():
    stats = {}
    
    # Universe Stats
    if os.path.exists(UNIVERSE_FILE):
        mtime = os.path.getmtime(UNIVERSE_FILE)
        stats['universe_last_update'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        stats['universe_active'] = (time.time() - mtime) < 86400 # 24時間以内か (頻繁な更新は必須ではない)
    
    # Queue Stats
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                q = json.load(f)
                stats['pending_items'] = len([i for i in q if i.get('status') == 'pending'])
        except: pass

    # Shukatsu Stats (27卒向け最新ファイル確認)
    if os.path.exists(SHUKATSU_DIR):
        files = [os.path.join(SHUKATSU_DIR, f) for f in os.listdir(SHUKATSU_DIR) if f.endswith('.json')]
        if files:
            latest = max(files, key=os.path.getmtime)
            mtime = os.path.getmtime(latest)
            stats['shukatsu_last_update'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            stats['shukatsu_active'] = (time.time() - mtime) < 7200 # 2時間以内か
    
    return stats

def run_camel_audit():
    stats = get_file_stats()
    stats_str = json.dumps(stats, indent=2, ensure_ascii=False)
    
    print(Fore.CYAN + f"\n[SYSTEM AUDIT] Starting CAMEL Health Check at {datetime.now().strftime('%H:%M:%S')}" + Fore.RESET)
    print(Fore.WHITE + f"Current Stats:\n{stats_str}\n" + Fore.RESET)

    # Agent 1: System Auditor (分析)
    print(Fore.YELLOW + "🧐 System Auditor is reviewing the metrics..." + Fore.RESET)
    auditor_prompt = f"""あなたはEGOの「システム分析官」です。
以下のシステム稼働統計を見て、情報収集が正常に行われているか（滞っていないか）を鋭く分析してください。
特に「27卒就活情報」と「Universeの更新」が止まっていないか注目してください。

統計データ:
{stats_str}

分析結果を簡潔に、箇条書きで述べてください。"""
    
    analysis = ask_llm(auditor_prompt)
    if not analysis: return
    print(Fore.MAGENTA + f"\n[Auditor Analysis]\n{analysis}\n" + Fore.RESET)

    # Agent 2: Operations Manager (指令生成)
    print(Fore.YELLOW + "💼 Operations Manager is devising an action plan..." + Fore.RESET)
    manager_prompt = f"""あなたはEGOの「運用マネージャー」です。
分析官の指摘を読み、もしシステムに異常（1時間以上の停止など）があれば、
AIアシスタント（Antigravity）に向けて**「具体的な復旧指令」**を出してください。
正常であれば「正常稼働中」とだけ答えてください。

【指令の形式例】
🚨 緊急指令: [止まっている機能名] が停止しています。直ちに [想定される対策] を実行してください。

分析官の指摘:
{analysis}"""

    instruction = ask_llm(manager_prompt)
    if not instruction: return
    print(Fore.RED + f"\n[Manager Instruction to Assistant]\n{instruction}\n" + Fore.RESET)

    # ブリッジへの記録
    bridge_path = os.path.join(ROOT_DIR, "EGO_SYSTEM_FILES/AI_CONTEXT_BRIDGE.md")
    if os.path.exists(bridge_path):
        with open(bridge_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### 🩺 SYSTEM HEALTH REPORT [{datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")
            if "🚨" in instruction:
                f.write(f"**[CRITICAL INSTRUCTION]**\n{instruction}\n")
            else:
                f.write(f"Status: {instruction}\n")

if __name__ == "__main__":
    run_camel_audit()
