"""
EGO Schedule Collector
情報収集パトロールから締切・イベント情報を抽出し、SCHEDULE.mdに自動追加
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# パス設定
SCHEDULE_MD = Path(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\CAREER\SCHEDULE.md")
SCHEDULE_JSON = Path(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data\SCHEDULE.json")
COLLECTED_EVENTS_LOG = Path(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\data\collected_events.json")

def parse_date(date_str: str) -> Optional[datetime]:
    """様々な形式の日付文字列をパース"""
    if not date_str:
        return None
    
    patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2026-02-03
        r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2026/02/03
        r'(\d{1,2})/(\d{1,2})',           # 2/3 (今年と仮定)
        r'(\d{1,2})月(\d{1,2})日',        # 2月3日
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            try:
                if len(groups) == 3:
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                elif len(groups) == 2:
                    year = datetime.now().year
                    return datetime(year, int(groups[0]), int(groups[1]))
            except ValueError:
                continue
    return None

def load_collected_events() -> list[dict]:
    """既に収集済みのイベントを読み込み"""
    if COLLECTED_EVENTS_LOG.exists():
        try:
            return json.loads(COLLECTED_EVENTS_LOG.read_text(encoding='utf-8'))
        except:
            return []
    return []

def save_collected_event(event: dict):
    """収集したイベントをログに保存"""
    events = load_collected_events()
    
    # 重複チェック（タイトルと日付で判定）
    for e in events:
        if e.get('title') == event.get('title') and e.get('date') == event.get('date'):
            return False  # 既に存在
    
    events.append(event)
    COLLECTED_EVENTS_LOG.write_text(
        json.dumps(events, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    return True

def update_schedule_md(event: dict) -> bool:
    """SCHEDULE.mdに新しいイベントを追加"""
    if not SCHEDULE_MD.exists():
        print(f"⚠️ SCHEDULE.md が見つかりません")
        return False
    
    content = SCHEDULE_MD.read_text(encoding='utf-8')
    
    # 「📌 注目イベント（収集済み）」セクションを探す
    section_marker = "## 📌 注目イベント（収集済み）"
    
    if section_marker not in content:
        # セクションがなければ追加
        content += f"\n\n{section_marker}\n\n| 日付 | イベント |\n| :--- | :--- |\n"
    
    # 新しい行を追加
    date_str = event.get('date', '未定')
    title = event.get('title', '不明')
    company = event.get('company', '')
    
    if company:
        title = f"{company}: {title}"
    
    new_row = f"| {date_str} | {title} |"
    
    # 既に同じ行がないかチェック
    if new_row in content:
        print(f"   ⏭️ 既に登録済み: {title[:30]}...")
        return False
    
    # テーブルの最後に追加
    lines = content.split('\n')
    insert_index = -1
    in_section = False
    
    for i, line in enumerate(lines):
        if section_marker in line:
            in_section = True
        elif in_section and line.startswith('## '):
            # 次のセクションに到達
            insert_index = i
            break
        elif in_section and line.startswith('| ') and '---' not in line and '日付' not in line:
            insert_index = i + 1  # テーブル行の後
    
    if insert_index == -1:
        # セクション末尾に追加
        for i, line in enumerate(lines):
            if section_marker in line:
                # テーブル構造を探す
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].startswith('| ') and '---' in lines[j]:
                        insert_index = j + 1
                        break
                break
    
    if insert_index > 0:
        lines.insert(insert_index, new_row)
        content = '\n'.join(lines)
        SCHEDULE_MD.write_text(content, encoding='utf-8')
        print(f"   ✅ SCHEDULE.mdに追加: {title[:40]}...")
        return True
    
    return False

def collect_from_patrol_result(patrol_data: dict) -> bool:
    """パトロール結果から締切情報を収集"""
    ai_analysis = patrol_data.get('ai_analysis', {})
    deadline = ai_analysis.get('deadline')
    company = ai_analysis.get('company')
    title = patrol_data.get('title', '')
    
    # 締切情報があれば処理
    if deadline:
        parsed_date = parse_date(deadline)
        if parsed_date:
            event = {
                'date': parsed_date.strftime('%Y-%m-%d'),
                'title': title[:50],
                'company': company,
                'source': patrol_data.get('source', ''),
                'link': patrol_data.get('link', ''),
                'collected_at': datetime.now().isoformat()
            }
            
            if save_collected_event(event):
                # 既存のスケジュールを読み込んで重複チェック
                existing_content = SCHEDULE_MD.read_text(encoding='utf-8')
                new_entries_count = 0
                
                # Prepare the item for checking/writing, similar to how update_schedule_md would format it
                date_str = event.get('date', '未定')
                event_title = event.get('title', '不明')
                event_company = event.get('company', '')
                if event_company:
                    event_title = f"{event_company}: {event_title}"
                
                check_str = f"| {date_str} | {event_title} |" # This is the full row to check for
                
                if check_str in existing_content:
                    print(f"   ⏭️ 既に登録済み (SCHEDULE.md): {event_title[:30]}...")
                    # If it's already in SCHEDULE.md, we don't need to add it again.
                    # But save_collected_event already returned True, meaning it was new to the log.
                    # So we just return True here to indicate successful collection.
                    return True 
                else:
                    # If not in SCHEDULE.md, proceed to add it using update_schedule_md
                    if update_schedule_md(event):
                        new_entries_count += 1
                
                if new_entries_count > 0:
                    print(f"✅ {new_entries_count}件のスケジュールを追加しました")
                else:
                    print("✅ 新しいスケジュールはありませんでした（すべて重複または収集なし）")
                return True
    
    return False

def scan_existing_data():
    """既存のパトロールデータをスキャンして締切を収集"""
    data_dir = Path(r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\data\shukatsu")
    
    if not data_dir.exists():
        print("❌ データディレクトリが見つかりません")
        return
    
    print(f"📂 スキャン中: {data_dir}")
    
    found_count = 0
    for json_file in data_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
            if collect_from_patrol_result(data):
                found_count += 1
        except Exception as e:
            continue
    
    print(f"✅ {found_count}件の締切情報を収集しました")

if __name__ == "__main__":
    print("="*50)
    print(" EGO Schedule Collector")
    print("="*50)
    scan_existing_data()
