import glob
import re
import sys
import os
import json
import time
import subprocess
import argparse
from datetime import datetime

# Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

# Import LLM
try:
    from modules.unified_llm_client import ask_llm
except ImportError:
    ask_llm = None

# 基本設定
VAULT_PATH = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data\universal_intelligence_vault.json"
BASE_DIR = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB"

def run_universal_loop(company, es_path):
    print(f"🚀 UNIVERSAL ES REFINE LOOP STARTED for: {company}")
    print(f"📄 Targeting: {es_path}")
    print("------------------------------------------")
    
    cycle = 1
    while True:
        print(f"\n🔄 CYCLE {cycle} - {time.ctime()}")
        
        # 1. パトロールの起動
        # 企業名を含めたクエリでライブ検索を実行
        query = f"{company} 最も注力している事業 技術戦略 2026 2027 求める人物像"
        print(f"📡 Step 1: Scanning latest intelligence for {company}...")
        try:
            subprocess.run(["python", "shukatsu_patrol.py", query], cwd=BASE_DIR, timeout=120)
        except Exception as e:
            print(f"⚠️ Patrol Warning: {e}")

        # 2. RAGマッチングと反映
        print("🧠 Step 2: Optimizing ES with Universal & Company-specific Keywords...")
        
        # 最新のインテリジェンスをロード
        intelligence_files = sorted(glob.glob(os.path.join(BASE_DIR, "data/shukatsu/SHUKATSU_*.json")), reverse=True)
        latest_intel = []
        for fpath in intelligence_files[:5]:  # 最新5件を使用
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    latest_intel.append(json.load(f))
            except: pass
            
        if not latest_intel:
            print("   ⚠️ No intelligence found. Skipping refinement.")
        else:
            # ESの読み込み
            try:
                with open(es_path, "r", encoding="utf-8") as f:
                    current_es = f.read()
                
                # Refine
                new_es = refine_es_content(current_es, latest_intel, company)
                
                if new_es and new_es != current_es:
                    # Backup
                    backup_path = es_path.replace(".md", f"_BACKUP_{int(time.time())}.md")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(current_es)
                    
                    # Update
                    with open(es_path, "w", encoding="utf-8") as f:
                        f.write(new_es)
                    print(f"   ✨ ES UPDATED! Backup saved to: {os.path.basename(backup_path)}")
                else:
                    print("   🍵 ES is already optimal. No changes made.")
            except Exception as e:
                print(f"   ❌ Refinement Error: {e}")

        print(f"✅ CYCLE {cycle} COMPLETE. Next check in 10 seconds (Turbo Mode)...")
        cycle += 1
        time.sleep(10)

def refine_es_content(current_text, intelligence_list, company_name):
    """
    ESとインテリジェンスを合成し、より「完璧」に近いESを生成する
    """
    if not ask_llm:
        return None
        
    # インテリジェンスの要約
    intel_summary = ""
    for item in intelligence_list:
        intel_summary += f"- {item.get('title')}: {item.get('ai_analysis', {}).get('strategic_analysis', {}).get('action_plan', '')}\n"

    prompt = f"""
あなたの任務は、KDDIのエントリーシート(ES)を「圧倒的に通過するレベル」まで磨き上げるだけでなく、複数の切り口（Variations）を提示し、それらを厳密に採点することです。

    【タスク】
    以下の現在のESをベースに、3つの異なるアプローチでブラッシュアップ案を作成し、それぞれの評価を行ってください。

    **案1：【泥臭さ・体力特化（Manure Ver）】**
    *   現在のESの方向性。「馬糞」「埃」「物理的シグナル」などの具体的で少し汚れた単語を使い、圧倒的なリアリティとタフさを強調する。

    **案2：【継承・知性特化（Legacy Ver）】**
    *   「熱力学」「流体力学」の知見を強調し、現場のベテランの暗黙知を科学的に翻訳する「知的な橋渡し役」としての側面を強調する。

    **案3：【使命感・インフラ特化（Guardian Ver）】**
    *   災害復旧や通信障害対応など、「当たり前を守る」ことへの執念を強調する。

    【出力フォーマット】
    Markdown形式で以下のように出力してください。
    
    # ES Refinement Proposals

    ## Option A: Manure Focus (泥臭さ)
    （設問2全文）
    （設問3全文）
    **Score**: X/100 (理由)

    ## Option B: Legacy Focus (知性)
    （設問2全文）
    （設問3全文）
    **Score**: X/100 (理由)

    ## Option C: Guardian Focus (指名感)
    （設問2全文）
    （設問3全文）
    **Score**: X/100 (理由)

    ## Final Recommendation
    （最も推奨する案を選定）

    【重要：共通の禁止事項】
    1. 抽象語（コミュニケーション、努力、リーダーシップ）の禁止。
    2. 精神論のみはNG。必ず「物理的行動（掃除、観察、データ化）」を入れること。
    3. キーワード「KDDI VISION 2030」等は維持。

    【最新インテリジェンス & キャリア戦略】
    {intel_summary}
    *   **キャリア戦略**: 「社内副業」や「KDDI DX University」を活用し、インフラ（現場）の知見を持ったデータサイエンティストを目指すキャリアパスを示唆すること。
    *   **キーワード**: 「現場発のDX」「設備の声をデータ化」「社内副業で視野拡大」


    【現在のES】
    {current_text}

"""
    try:
        response = ask_llm(prompt)
        # Markdownブロックの除去
        if "```markdown" in response:
            response = response.split("```markdown")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        return response.strip()
    except Exception as e:
        print(f"Refinement LLM Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", default="KDDI")
    parser.add_argument("--path", default=r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\CAREER\KDDI_ES_FINAL.md")
    args = parser.parse_args()
    
    run_universal_loop(args.company, args.path)
