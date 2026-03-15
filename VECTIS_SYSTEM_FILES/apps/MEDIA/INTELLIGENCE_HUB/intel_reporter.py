"""
EGO INTEL REPORTER (System Bridge)
=====================================
最新のインテリジェンスを AI Agent への共有コンテキストとして
AI_CONTEXT_BRIDGE.md に同期するスクリプト。
"""

import os
import json
from datetime import datetime

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")
DEEP_KNOWLEDGE_FILE = os.path.join(DATA_DIR, "deep_knowledge.json")
BRIDGE_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../AI_CONTEXT_BRIDGE.md"))

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None

def update_bridge():
    universe = load_json(UNIVERSE_FILE)
    deep_kb = load_json(DEEP_KNOWLEDGE_FILE)
    
    report = []
    report.append(f"\n## 🌟 LATEST INTELLIGENCE FLASH [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    report.append("バックグラウンド処理により以下の最新ナレッジが更新されました。\n")
    
    # 最新のユニバースノード (3件)
    if universe and "nodes" in universe:
        report.append("### 🛰️ 最新のニュース・トピック")
        for node in universe["nodes"][-3:]:
            report.append(f"- **{node.get('title')}** ({node.get('group', 'General')})")
    
    # 最新のディープ・ナレッジ (1件)
    if deep_kb and "chapters" in deep_kb:
        report.append("\n### 📖 最新の深掘り記事（百科事典）")
        last_ch = deep_kb["chapters"][-1]
        report.append(f"- **{last_ch.get('title')}**")
        report.append(f"  > {last_ch.get('overview', '')[:100]}...")

    report.append("\n---")
    
    # AI_CONTEXT_BRIDGE.md に追記（または特定セクションの更新）
    # 今回はシンプルに最新の3報告を維持する形にする
    try:
        if os.path.exists(BRIDGE_FILE):
            with open(BRIDGE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 既存の報告セクションを完全にリフレッシュする
            marker = "## 🌟 LATEST INTELLIGENCE FLASH"
            sections = content.split("---")
            
            # ヘッダー（最初のセクション）を維持
            header = sections[0].split(marker)[0].strip()
            
            # 新しいレポート
            new_report = "\n".join(report)
            
            # 他の永続的なセクション (DIRECTIVESなど) を抽出
            remaining_sections = []
            for s in sections[1:]:
                if marker not in s and "SYSTEM HEALTH REPORT" not in s:
                    if s.strip():
                        remaining_sections.append(s.strip())
            
            # システムヘルスレポートは直近3件のみ維持
            health_reports = []
            for s in sections:
                if "SYSTEM HEALTH REPORT" in s:
                    health_reports.append(s.strip())
            health_reports = health_reports[-3:]
            
            # 再構築
            final_parts = [header, new_report]
            final_parts.extend(remaining_sections)
            final_parts.extend(health_reports)
            
            new_content = "\n\n---\n\n".join(final_parts)
            
            with open(BRIDGE_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"✅ System Bridge Updated: {BRIDGE_FILE}")
        else:
            with open(BRIDGE_FILE, "w", encoding="utf-8") as f:
                f.write("# AI CONTEXT BRIDGE\n" + "\n".join(report))
            print(f"✅ Bridge Created: {BRIDGE_FILE}")
            
    except Exception as e:
        print(f"❌ Bridge Update Failed: {e}")

if __name__ == "__main__":
    update_bridge()
