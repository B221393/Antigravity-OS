import os
import time
import subprocess
import sys

# パス設定
BASE_DIR = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB"
PATROL_SCRIPT = "shukatsu_patrol.py"
RAG_SCRIPT = "kddi_rag_engine.py"

DASHBOARD_PATH = os.path.join(BASE_DIR, "REFINE_DASHBOARD.md")

def update_dashboard(cycle, status, detail=""):
    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 KDDI ES INFINITE REFINE LIVE DASHBOARD\n\n")
        f.write(f"- **最終更新**: {time.ctime()}\n")
        f.write(f"- **現在のサイクル**: {cycle}\n")
        f.write(f"- **ステータス**: {status}\n\n")
        if detail:
            f.write(f"## 📡 ログ詳細\n{detail}\n")
        f.write(f"\n---\n*このレポートは自動生成されています。提出直前まで研ぎ澄まされ続けます。*")

def run_loop():
    print("🚀 KDDI ES INFINITE REFINE LOOP STARTED")
    print("------------------------------------------")
    cycle = 1
    while True:
        status_msg = f"CYCLE {cycle} 進行中..."
        update_dashboard(cycle, "インテリジェンス収集中...", "最新のKDDI動向をスキャンしています。")
        print(f"\n🔄 CYCLE {cycle} - {time.ctime()}")
        
        # 1. 最新情報のパトロール (120秒制限)
        print("📡 Step 1: Gathering Latest KDDI Intelligence...")
        try:
            subprocess.run(["python", PATROL_SCRIPT, "--one-shot"], cwd=BASE_DIR, timeout=120)
        except Exception as e:
            print(f"⚠️ Patrol Warning: {e}")

        update_dashboard(cycle, "ES推敲中...", "収集した情報をESに注入・最適化しています。")
        # 2. RAGエンジンによるESとの照合と反映
        print("🧠 Step 2: Running RAG Optimization Engine...")
        try:
            subprocess.run(["python", RAG_SCRIPT], cwd=BASE_DIR)
        except Exception as e:
            print(f"⚠️ RAG Warning: {e}")

        update_dashboard(cycle, "待機中 (Next in 5 min)", "次回のブラッシュアップ・サイクルに向けて待機しています。")
        print(f"✅ CYCLE {cycle} COMPLETE. Sleeping for 300 seconds...")
        cycle += 1
        time.sleep(300)

if __name__ == "__main__":
    run_loop()
