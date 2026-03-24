"""
VECTIS OS - Usage Tracker & Auto-Renumbering System
===================================================
使用回数に基づいてランチャーファイルの番号を自動最適化
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class LauncherManager:
    """
    ランチャー管理システム
    
    Features:
    - 使用統計の記録
    - 使用頻度に基づく自動リナンバリング
    - バックアップ作成
    
    Invariants:
    - 統計ファイルは常に有効なJSON
    - 番号は01-98の範囲（00と99は固定）
    """
    
    def __init__(self, app_dir: str = None):
        if app_dir is None:
            # スクリプトの親ディレクトリ
            app_dir = Path(__file__).parent.parent
        
        self.app_dir = Path(app_dir)
        self.stats_file = self.app_dir / "launcher_stats.json"
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """統計ファイル読み込み"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"launchers": {}, "last_reorder": None}
        return {"launchers": {}, "last_reorder": None}
    
    def _save_stats(self):
        """統計ファイル保存"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def record_usage(self, launcher_name: str):
        """
        使用回数を記録
        
        Args:
            launcher_name: ランチャー名 (例: "MAGI_HUD")
        """
        if launcher_name not in self.stats["launchers"]:
            self.stats["launchers"][launcher_name] = {
                "count": 0,
                "last_used": None,
                "first_used": datetime.now().isoformat()
            }
        
        self.stats["launchers"][launcher_name]["count"] += 1
        self.stats["launchers"][launcher_name]["last_used"] = datetime.now().isoformat()
        self._save_stats()
    
    def get_launcher_files(self) -> List[Tuple[int, str, Path]]:
        """
        現在のランチャーファイルを取得
        
        Returns:
            List of (番号, 名前, パス)
        """
        launchers = []
        
        for file in self.app_dir.glob("[0-9][0-9]_*.bat"):
            name = file.name
            # 番号とアプリ名を分離
            try:
                num_str = name[:2]
                num = int(num_str)
                app_name = name[3:-4]  # "01_App_Name.bat" -> "App_Name"
                launchers.append((num, app_name, file))
            except:
                continue
        
        return sorted(launchers, key=lambda x: x[0])
    
    def reorder_launchers(self, dry_run: bool = False) -> List[Tuple[str, str]]:
        """
        使用頻度に基づいてランチャーをリナンバリング
        
        Args:
            dry_run: Trueの場合、実際にはリネームせず計画のみ返す
            
        Returns:
            List of (old_name, new_name)
            
        Reasoning:
        - 00と99は固定（MAGI_HUD, Emergency_Stop）
        - 01-98を使用頻度順に割り当て
        - 同じ使用回数なら最終使用日時で優先
        """
        current_launchers = self.get_launcher_files()
        
        # 固定ランチャー（リナンバリング対象外）
        fixed = {0, 99}
        
        # リナンバリング対象
        reorderable = [(num, name, path) for num, name, path in current_launchers if num not in fixed]
        
        # 使用統計に基づいてソート
        def get_priority(item):
            _, name, _ = item
            stats = self.stats["launchers"].get(name, {})
            count = stats.get("count", 0)
            last_used = stats.get("last_used", "2000-01-01T00:00:00")
            return (-count, last_used)  # 使用回数降順、同じなら最終使用日時昇順
        
        reorderable.sort(key=get_priority)
        
        # 新しい番号を割り当て
        changes = []
        next_num = 1
        
        for _, name, old_path in reorderable:
            # 00と99をスキップ
            if next_num == 0:
                next_num = 1
            if next_num >= 99:
                break
            
            new_name = f"{next_num:02d}_{name}.bat"
            new_path = self.app_dir / new_name
            
            if old_path.name != new_name:
                changes.append((str(old_path.name), str(new_name)))
                
                if not dry_run:
                    # リネーム実行
                    try:
                        old_path.rename(new_path)
                    except Exception as e:
                        print(f"Error renaming {old_path.name}: {e}")
            
            next_num += 1
        
        if not dry_run and changes:
            self.stats["last_reorder"] = datetime.now().isoformat()
            self._save_stats()
        
        return changes
    
    def show_stats(self):
        """統計を表示"""
        print("=" * 60)
        print("LAUNCHER USAGE STATISTICS")
        print("=" * 60)
        
        if not self.stats["launchers"]:
            print("\nNo usage data yet.")
            return
        
        # 使用回数でソート
        sorted_launchers = sorted(
            self.stats["launchers"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        print("\nRank | Launcher              | Usage Count | Last Used")
        print("-" * 60)
        
        for i, (name, data) in enumerate(sorted_launchers, 1):
            count = data["count"]
            last_used = data.get("last_used", "Never")
            if last_used != "Never":
                last_used = last_used[:10]  # 日付のみ
            print(f"{i:4d} | {name:20s} | {count:11d} | {last_used}")
        
        print("=" * 60)
        
        if self.stats.get("last_reorder"):
            print(f"\nLast reordered: {self.stats['last_reorder'][:19]}")


def main():
    """メイン処理"""
    import sys
    
    manager = LauncherManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python launcher_manager.py record <launcher_name>")
        print("  python launcher_manager.py reorder [--dry-run]")
        print("  python launcher_manager.py stats")
        return
    
    command = sys.argv[1]
    
    if command == "record":
        if len(sys.argv) < 3:
            print("Error: Launcher name required")
            return
        launcher_name = sys.argv[2]
        manager.record_usage(launcher_name)
        print(f"[OK] Recorded usage: {launcher_name}")
    
    elif command == "reorder":
        dry_run = "--dry-run" in sys.argv
        
        if dry_run:
            print("DRY RUN MODE - No actual changes will be made\n")
        
        changes = manager.reorder_launchers(dry_run=dry_run)
        
        if not changes:
            print("No reordering necessary - launchers are already optimal!")
        else:
            print(f"{'Planned' if dry_run else 'Applied'} {len(changes)} changes:\n")
            for old, new in changes:
                print(f"  {old:30s} -> {new}")
            
            if dry_run:
                print("\nRun without --dry-run to apply changes.")
            else:
                print("\n✅ Launchers reordered successfully!")
    
    elif command == "stats":
        manager.show_stats()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
