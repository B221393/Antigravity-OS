"""
VECTIS Schedule Archiver
過ぎたイベントをアーカイブセクションに移動
"""

import re
from pathlib import Path
from datetime import datetime

SCHEDULE_MD = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\CAREER\SCHEDULE.md")

def parse_date_from_row(row: str) -> datetime | None:
    """テーブル行から日付をパース"""
    patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2026-02-03
        r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2026/02/03
        r'\*\*(\d{1,2})/(\d{1,2})\*\*',  # **2/3**
    ]
    
    for pattern in patterns:
        match = re.search(pattern, row)
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

def archive_past_events():
    """過ぎたイベントをアーカイブに移動"""
    if not SCHEDULE_MD.exists():
        print("❌ SCHEDULE.md が見つかりません")
        return
    
    content = SCHEDULE_MD.read_text(encoding='utf-8')
    lines = content.split('\n')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 過去イベント用リスト
    past_events = []
    future_lines = []
    
    # 注目イベントセクションを処理
    in_collected_section = False
    collected_header_done = False
    
    for line in lines:
        # 注目イベントセクションの開始
        if "注目イベント（収集済み）" in line:
            in_collected_section = True
            future_lines.append(line)
            continue
        
        # 次のセクションで終了
        if in_collected_section and line.startswith('## ') and "注目イベント" not in line:
            in_collected_section = False
        
        # テーブル行を処理
        if in_collected_section and line.startswith('| ') and '---' not in line and '日付' not in line:
            date = parse_date_from_row(line)
            if date:
                if date < today:
                    past_events.append(line)
                    continue  # 未来行リストには追加しない
        
        future_lines.append(line)
    
    # アーカイブセクションを追加（または更新）
    archive_section = "\n## 📦 過去のイベント（アーカイブ）\n\n<details>\n<summary>クリックで展開</summary>\n\n| 日付 | イベント |\n| :--- | :--- |\n"
    
    for event in sorted(past_events, reverse=True):
        archive_section += event + "\n"
    
    archive_section += "\n</details>\n"
    
    # 既存のアーカイブセクションを削除
    new_content = '\n'.join(future_lines)
    archive_pattern = r'\n## 📦 過去のイベント（アーカイブ）.*?(?=\n## |\Z)'
    new_content = re.sub(archive_pattern, '', new_content, flags=re.DOTALL)
    
    # 壁紙更新セクションの前にアーカイブを挿入
    wallpaper_section = "## 🔄 壁紙更新"
    if wallpaper_section in new_content:
        new_content = new_content.replace(wallpaper_section, archive_section + "\n---\n\n" + wallpaper_section)
    else:
        new_content += archive_section
    
    # 更新時刻を更新
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_content = re.sub(r'\*\*最終更新\*\*: .+', f'**最終更新**: {now_str}', new_content)
    
    SCHEDULE_MD.write_text(new_content, encoding='utf-8')
    print(f"✅ {len(past_events)}件の過去イベントをアーカイブしました")

if __name__ == "__main__":
    print("="*50)
    print(" VECTIS Schedule Archiver")
    print("="*50)
    archive_past_events()
