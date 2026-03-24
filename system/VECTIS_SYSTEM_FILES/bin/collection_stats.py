"""
VECTIS 情報収集統計ダッシュボード
これまでに収集したデータの統計を表示
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\data\shukatsu")

def analyze_collection():
    """収集データを分析"""
    files = list(DATA_DIR.glob("*.json"))
    
    if not files:
        print("❌ データが見つかりません")
        return
    
    # 統計情報
    total_files = len(files)
    total_size = sum(f.stat().st_size for f in files)
    
    # 日別カウント
    daily_counts = defaultdict(int)
    source_counts = defaultdict(int)
    relevance_counts = defaultdict(int)
    company_mentions = defaultdict(int)
    
    for f in files:
        # 日付抽出
        name = f.name
        if "_" in name and len(name) > 15:
            date_part = name.split("_")[1][:8]
            if date_part.startswith("2026"):
                daily_counts[date_part] += 1
        
        # 内容分析
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            source = data.get('source', '不明')
            source_counts[source.split('(')[0].strip()] += 1
            
            ai = data.get('ai_analysis', {})
            relevance = ai.get('relevance', '不明')
            relevance_counts[relevance] += 1
            
            company = ai.get('company')
            if company:
                company_mentions[company] += 1
        except:
            pass
    
    # 表示
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           VECTIS 情報収集統計ダッシュボード                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print(f"  📊 総収集件数:  {total_files:,} 件")
    print(f"  💾 総データ量:  {total_size / 1024 / 1024:.2f} MB")
    print(f"  📅 収集日数:    {len(daily_counts)} 日")
    print()
    
    # 日別グラフ
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📈 日別収集量 (直近14日)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    sorted_dates = sorted(daily_counts.keys())[-14:]
    max_count = max(daily_counts[d] for d in sorted_dates) if sorted_dates else 1
    
    for date in sorted_dates:
        count = daily_counts[date]
        bar_len = int((count / max_count) * 30)
        bar = "█" * bar_len
        formatted_date = f"{date[4:6]}/{date[6:8]}"
        print(f"  {formatted_date} │ {bar} {count:>4}件")
    
    print()
    
    # ソース別
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📡 ソース別収集量 (Top 10)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {source[:25]:<25} : {count:>4}件")
    
    print()
    
    # 関連度
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🎯 関連度分布")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for relevance in ['high', 'medium', 'low', '不明']:
        count = relevance_counts.get(relevance, 0)
        emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', '不明': '⚪'}.get(relevance, '⚪')
        print(f"  {emoji} {relevance:<8} : {count:>4}件")
    
    print()
    
    # 企業別
    if company_mentions:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  🏢 言及された企業 (Top 10)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for company, count in sorted(company_mentions.items(), key=lambda x: -x[1])[:10]:
            print(f"  {company[:25]:<25} : {count:>4}件")
    
    print()
    print("═" * 60)
    print()

if __name__ == "__main__":
    analyze_collection()
