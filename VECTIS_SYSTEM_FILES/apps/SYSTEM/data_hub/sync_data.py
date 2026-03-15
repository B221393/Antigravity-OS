"""
VECTIS Data Sync System
HTML LocalStorage ⇔ JSON File 自動同期

機能:
- LocalStorageデータをJSON exportから読み込み
- JSONファイルをHTMLで読み込める形式に整形
- 双方向同期をサポート

使用方法:
    python sync_data.py --export   # LocalStorageデータをexport
    python sync_data.py --import   # JSONからLocalStorageに復元
"""

import json
import os
from pathlib import Path
from datetime import datetime

# パス設定
BASE_DIR = Path(__file__).parent
SYNC_DATA_DIR = BASE_DIR / "sync_data"
SYNC_DATA_DIR.mkdir(exist_ok=True)

# 各アプリのデータファイル
DATA_FILES = {
    "reading_log": SYNC_DATA_DIR / "reading_log.json",
    "job_applications": SYNC_DATA_DIR / "job_applications.json",
    "vocab_progress": SYNC_DATA_DIR / "vocab_progress.json",
    "intelligence": SYNC_DATA_DIR / "intelligence.json",
    "unified": SYNC_DATA_DIR / "unified_data.json"
}


def export_template():
    """
    LocalStorageからエクスポートしたJSONファイルのテンプレートを作成
    """
    template = {
        "timestamp": datetime.now().isoformat(),
        "version": "2.0",
        "data": {
            "reading": [],
            "job": [],
            "vocab": {
                "studied": [],
                "mastered": []
            },
            "intel": {
                "job": [],
                "youtube": [],
                "news": []
            },
            "knowledge": {
                "nodes": []
            }
        }
    }
    
    with open(DATA_FILES["unified"], 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Template created: {DATA_FILES['unified']}")
    print("\n📝 使用手順:")
    print("1. Data Hubで「📥 全データエクスポート」をクリック")
    print("2. ダウンロードしたJSONファイルをsync_data/にコピー")
    print("3. python sync_data.py --import を実行")


def process_exported_json(json_file):
    """
    Data Hubからエクスポートされたjsonファイルを処理
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if "data" not in data:
        print("❌ Invalid JSON format")
        return
    
    # 各カテゴリごとに分割保存
    app_data = data["data"]
    
    # Reading Log
    if "reading" in app_data:
        with open(DATA_FILES["reading_log"], 'w', encoding='utf-8') as f:
            json.dump(app_data["reading"], f, ensure_ascii=False, indent=2)
        print(f"✅ Reading Log: {len(app_data['reading'])} items")
    
    # Job Applications
    if "job" in app_data:
        with open(DATA_FILES["job_applications"], 'w', encoding='utf-8') as f:
            json.dump(app_data["job"], f, ensure_ascii=False, indent=2)
        print(f"✅ Job Applications: {len(app_data['job'])} items")
    
    # Vocabulary Progress
    if "vocab" in app_data:
        with open(DATA_FILES["vocab_progress"], 'w', encoding='utf-8') as f:
            json.dump(app_data["vocab"], f, ensure_ascii=False, indent=2)
        studied = len(app_data["vocab"].get("studied", []))
        mastered = len(app_data["vocab"].get("mastered", []))
        print(f"✅ Vocabulary: {studied} studied, {mastered} mastered")
    
    # Intelligence
    if "intel" in app_data:
        with open(DATA_FILES["intelligence"], 'w', encoding='utf-8') as f:
            json.dump(app_data["intel"], f, ensure_ascii=False, indent=2)
        job = len(app_data["intel"].get("job", []))
        youtube = len(app_data["intel"].get("youtube", []))
        print(f"✅ Intelligence: {job} jobs, {youtube} videos")
    
    # Save unified
    with open(DATA_FILES["unified"], 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 All data saved to: {SYNC_DATA_DIR}")


def create_import_script():
    """
    データをLocalStorageにインポートするためのJavaScriptコードを生成
    """
    if not DATA_FILES["unified"].exists():
        print("❌ No unified data found. Run export first.")
        return
    
    with open(DATA_FILES["unified"], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # JavaScriptコード生成
    js_code = f"""
// VECTIS Data Import Script
// ブラウザのコンソールで実行してください

const importData = {json.dumps(data, ensure_ascii=False, indent=2)};

// LocalStorageに保存
localStorage.setItem('vectis_reading_log', JSON.stringify(importData.data.reading));
localStorage.setItem('vectis_job_applications', JSON.stringify(importData.data.job));
localStorage.setItem('vectis_vocab_progress', JSON.stringify(importData.data.vocab));
localStorage.setItem('vectis_intelligence_hub', JSON.stringify(importData.data.intel));
localStorage.setItem('vectis_knowledge_sync', JSON.stringify(importData.data.knowledge));
localStorage.setItem('vectis_unified_data', JSON.stringify(importData));

console.log('✅ Data imported successfully!');
console.log('Total items:', 
    importData.data.reading.length + 
    importData.data.job.length + 
    (importData.data.vocab.studied?.length || 0)
);
"""
    
    import_script = SYNC_DATA_DIR / "import_to_browser.js"
    with open(import_script, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"✅ Import script created: {import_script}")
    print("\n📝 使用手順:")
    print("1. Data Hubをブラウザで開く")
    print("2. F12キーで開発者ツールを開く")
    print("3. Consoleタブを選択")
    print(f"4. {import_script} の内容をコピー&ペーストして実行")


def generate_stats_report():
    """
    同期データの統計レポートを生成
    """
    if not DATA_FILES["unified"].exists():
        print("❌ No data found")
        return
    
    with open(DATA_FILES["unified"], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*50)
    print("📊 VECTIS Data Statistics Report")
    print("="*50)
    print(f"Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"Version: {data.get('version', 'N/A')}")
    print()
    
    app_data = data.get("data", {})
    
    # Reading Log
    reading = app_data.get("reading", [])
    print(f"📚 Reading Log: {len(reading)} books")
    if reading:
        latest = reading[0]
        print(f"   Latest: {latest.get('title', 'N/A')}")
    
    # Job Applications
    jobs = app_data.get("job", [])
    print(f"\n💼 Job Applications: {len(jobs)} applications")
    if jobs:
        statuses = {}
        for job in jobs:
            status = job.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        for status, count in statuses.items():
            print(f"   {status}: {count}")
    
    # Vocabulary
    vocab = app_data.get("vocab", {})
    studied = len(vocab.get("studied", []))
    mastered = len(vocab.get("mastered", []))
    print(f"\n📖 Vocabulary Progress:")
    print(f"   Studied: {studied}")
    print(f"   Mastered: {mastered}")
    print(f"   Total: {studied + mastered}")
    
    # Intelligence
    intel = app_data.get("intel", {})
    print(f"\n🧠 Intelligence:")
    print(f"   Jobs: {len(intel.get('job', []))}")
    print(f"   YouTube: {len(intel.get('youtube', []))}")
    print(f"   News: {len(intel.get('news', []))}")
    
    print("\n" + "="*50)


def main():
    import sys
    
    print("🔄 VECTIS Data Sync System")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python sync_data.py --template   # テンプレート作成")
        print("  python sync_data.py --import     # JSONから同期")
        print("  python sync_data.py --export     # インポートスクリプト生成")
        print("  python sync_data.py --stats      # 統計表示")
        return
    
    command = sys.argv[1]
    
    if command == "--template":
        export_template()
    
    elif command == "--import":
        # unified_data.jsonがあればそれを処理
        if DATA_FILES["unified"].exists():
            process_exported_json(DATA_FILES["unified"])
        else:
            print("❌ sync_data/unified_data.json not found")
            print("Data Hubからエクスポートしたファイルをここに配置してください")
    
    elif command == "--export":
        create_import_script()
    
    elif command == "--stats":
        generate_stats_report()
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
