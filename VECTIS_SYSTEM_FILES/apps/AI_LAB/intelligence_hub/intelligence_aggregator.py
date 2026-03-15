"""
EGO Intelligence Hub - Data Aggregator
情報収集結果を統合してJSONファイルとして出力

使用方法:
    python intelligence_aggregator.py

出力:
    - intelligence_hub_data.json (HTMLから読み込み可能)
    - OBSIDIAN_WRITING/INTELLIGENCE/ (マークダウン形式)
"""

import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import json
import glob
from datetime import datetime
from pathlib import Path

# パス設定
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent.parent.parent
OBSIDIAN_DIR = ROOT_DIR / "OBSIDIAN_WRITING"
BOOKSHELF_DIR = OBSIDIAN_DIR / "BOOKSHELF"
INTELLIGENCE_DIR = OBSIDIAN_DIR / "INTELLIGENCE"
OCR_DROPZONE = Path.home() / "Desktop" / "OCR_DROPZONE"

# 出力先JSON
OUTPUT_JSON = BASE_DIR / "intelligence_hub_data.json"


def scan_bookshelf():
    """
    BOOKSHELFから情報収集結果をスキャン
    """
    intelligence = {
        "job": [],
        "youtube": [],
        "news": [],
        "research": [],
        "visual": []
    }
    
    if not BOOKSHELF_DIR.exists():
        print(f"⚠️  BOOKSHELF not found: {BOOKSHELF_DIR}")
        return intelligence
    
    # 就活情報（Job Hunting）
    job_files = list(BOOKSHELF_DIR.glob("**/就活*.md")) + list(BOOKSHELF_DIR.glob("**/Job*.md"))
    for file in job_files[:10]:  # 最新10件
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else file.stem
                
                intelligence["job"].append({
                    "title": title,
                    "source": "Job Patrol",
                    "date": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d'),
                    "preview": content[:200].replace('\n', ' '),
                    "path": str(file.relative_to(ROOT_DIR)),
                    "category": "job"
                })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # YouTube情報
    youtube_files = list(BOOKSHELF_DIR.glob("**/YouTube*.md")) + list(BOOKSHELF_DIR.glob("**/動画*.md"))
    for file in youtube_files[:10]:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else file.stem
                
                intelligence["youtube"].append({
                    "title": title,
                    "source": "YouTube Intelligence",
                    "date": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d'),
                    "preview": content[:200].replace('\n', ' '),
                    "path": str(file.relative_to(ROOT_DIR)),
                    "category": "youtube"
                })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # News & Research
    research_files = list(BOOKSHELF_DIR.glob("**/*研究*.md")) + list(BOOKSHELF_DIR.glob("**/*AI*.md"))
    for file in research_files[:10]:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else file.stem
                
                intelligence["research"].append({
                    "title": title,
                    "source": "Research Feed",
                    "date": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d'),
                    "preview": content[:200].replace('\n', ' '),
                    "path": str(file.relative_to(ROOT_DIR)),
                    "category": "research"
                })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
            print(f"Error reading {file}: {e}")
    
    # Visual Cortex (OCR)
    if OCR_DROPZONE.exists():
        ocr_files = list(OCR_DROPZONE.glob("*.md"))
        for file in ocr_files[:20]:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    # Use filename as title for visual data
                    title = file.stem
                    
                    intelligence["visual"].append({
                        "title": f"[OCR] {title}",
                        "source": "Visual Cortex",
                        "date": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d'),
                        "preview": content[:200].replace('\n', ' '),
                        "path": str(file), # Absolute path for now, or relative if possible
                        "category": "visual"
                    })
            except Exception as e:
                print(f"Error reading OCR file {file}: {e}")

    return intelligence


def save_json(intelligence):
    """
    Intelligence HubのHTMLから読み込めるJSON形式で保存
    """
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_count": sum(len(v) for v in intelligence.values()),
        "intelligence": intelligence
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON saved: {OUTPUT_JSON}")
    print(f"📊 Total: {data['total_count']} items")
    print(f"   - Job: {len(intelligence['job'])}")
    print(f"   - YouTube: {len(intelligence['youtube'])}")
    print(f"   - Research: {len(intelligence['research'])}")


def create_intelligence_index():
    """
    INTELLIGENCE/index.md に統合インデックスを作成
    """
    INTELLIGENCE_DIR.mkdir(exist_ok=True)
    
    index_path = INTELLIGENCE_DIR / "index.md"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"# 🧠 EGO Intelligence Index\n\n")
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 📊 Sources\n\n")
        f.write("- 💼 Job Patrol: 就活・求人情報\n")
        f.write("- 📺 YouTube Intelligence: 動画・トレンド分析\n")
        f.write("- 🔍 Personal Intelligence: 統合情報収集\n")
        f.write("- 📰 News Feed: ニュース・研究\n")
        f.write("- 👁️ Visual Cortex: 画像認識ログ\n\n")
        
        f.write("## 🌐 Integration\n\n")
        f.write("- [Intelligence Hub](../apps/AI_LAB/intelligence_hub/index.html)\n")
        f.write("- [Knowledge Network](../apps/AI_LAB/knowledge_cards/control_center.html)\n")
        f.write("- [Job Dashboard](../apps/UTILS/job_hunting/index.html)\n\n")
        
        f.write("## 📁 Data Location\n\n")
        f.write(f"```\n{OUTPUT_JSON}\n```\n")
    
    print(f"✅ Index created: {index_path}")


def main():
    print("🧠 EGO Intelligence Hub - Data Aggregator")
    print("=" * 50)
    
    # 1. BOOKSHELFスキャン
    print("\n📚 Scanning BOOKSHELF...")
    intelligence = scan_bookshelf()
    
    # 2. JSON保存
    print("\n💾 Saving JSON...")
    save_json(intelligence)
    
    # 3. インデックス作成
    print("\n📝 Creating index...")
    create_intelligence_index()
    
    print("\n✅ Intelligence aggregation complete!")
    print(f"\n📂 Open: EGO_SYSTEM_FILES/apps/AI_LAB/intelligence_hub/index.html")


if __name__ == "__main__":
    main()
