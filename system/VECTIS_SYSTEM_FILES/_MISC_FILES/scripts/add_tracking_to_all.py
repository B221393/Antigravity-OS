"""
VECTIS OS - Batch Add Usage Tracking
=====================================
既存の全ランチャーに使用記録コードを一括追加
"""

import os
import re
from pathlib import Path

def add_tracking_to_launcher(launcher_path: Path):
    """
    ランチャーファイルに使用記録コードを追加
    
    Args:
        launcher_path: .batファイルのパス
    """
    # ファイル読み込み
    with open(launcher_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # すでに記録コードがある場合はスキップ
    if "launcher_manager.py record" in content:
        print(f"  [SKIP] {launcher_path.name} - Already has tracking")
        return False
    
    # アプリ名を抽出 (例: "01_Main_HUD.bat" -> "Main_HUD")
    match = re.match(r'\d{2}_(.+)\.bat', launcher_path.name)
    if not match:
        print(f"  [SKIP] {launcher_path.name} - Invalid name format")
        return False
    
    app_name = match.group(1)
    
    # 挿入位置を探す
    # "call .venv\Scripts\activate.bat" の後に挿入
    lines = content.split('\n')
    insert_index = -1
    
    for i, line in enumerate(lines):
        if 'activate.bat' in line.lower():
            insert_index = i + 1
            break
    
    if insert_index == -1:
        # activateが見つからない場合、cd /d の後
        for i, line in enumerate(lines):
            if line.strip().startswith('cd /d'):
                insert_index = i + 1
                break
    
    if insert_index == -1:
        print(f"  [SKIP] {launcher_path.name} - Can't find insertion point")
        return False
    
    # トラッキングコードを挿入
    tracking_code = [
        '',
        'REM === 使用回数を記録 ===',
        f'python scripts/launcher_manager.py record "{app_name}"',
        ''
    ]
    
    for i, code_line in enumerate(tracking_code):
        lines.insert(insert_index + i, code_line)
    
    # ファイルに書き戻し
    new_content = '\n'.join(lines)
    
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  [OK] {launcher_path.name} - Added tracking for '{app_name}'")
    return True


def main():
    """すべてのランチャーに使用記録を追加"""
    app_dir = Path(__file__).parent.parent
    
    print("=" * 60)
    print("VECTIS - Batch Add Usage Tracking")
    print("=" * 60)
    print()
    
    # すべての番号付きランチャーを取得
    launchers = list(app_dir.glob("[0-9][0-9]_*.bat"))
    
    if not launchers:
        print("No launchers found!")
        return
    
    print(f"Found {len(launchers)} launchers. Adding tracking code...\n")
    
    added_count = 0
    for launcher in sorted(launchers):
        if add_tracking_to_launcher(launcher):
            added_count += 1
    
    print()
    print("=" * 60)
    print(f"Added tracking to {added_count}/{len(launchers)} launchers")
    print("=" * 60)
    print()
    print("Usage tracking is now enabled!")
    print("Run launchers normally, and their usage will be recorded.")
    print()
    print("To view stats: SHOW_USAGE_STATS.bat")
    print("To reorder:    REORDER_LAUNCHERS.bat")


if __name__ == "__main__":
    main()
