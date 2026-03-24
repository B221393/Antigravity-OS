"""
EGO Universe Duplicate Cleaner
==================================
universe.json から重複ノードを削除し、データをクリーンアップする

使用方法:
  python cleanup_duplicates.py --dry-run  # 削除対象を確認（実際には削除しない）
  python cleanup_duplicates.py            # 実際に削除を実行
"""

import os
import sys
import json
import hashlib
import shutil
from datetime import datetime
from difflib import SequenceMatcher

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def similarity(a, b):
    """2つの文字列の類似度を計算 (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def normalize_title(title):
    """タイトルを正規化（比較用）"""
    # 記号、数字のバリエーションを正規化
    import re
    title = re.sub(r'[：:\-・→]', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip().lower()

def get_title_hash(title):
    """タイトルのハッシュを取得"""
    return hashlib.md5(normalize_title(title).encode()).hexdigest()[:8]

def load_universe():
    """universe.json を読み込み"""
    if not os.path.exists(UNIVERSE_FILE):
        print(f"[ERROR] {UNIVERSE_FILE} not found!")
        return None
    
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_universe(data, dry_run=False):
    """universe.json を保存"""
    if dry_run:
        print("[DRY-RUN] 実際の保存はスキップされました")
        return
    
    # バックアップ作成
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"universe_backup_{timestamp}.json")
    shutil.copy(UNIVERSE_FILE, backup_path)
    print(f"[BACKUP] {backup_path}")
    
    # 保存
    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] {UNIVERSE_FILE}")

def find_duplicates(nodes, threshold=0.70):
    """
    重複ノードを検出
    Returns: {keep_id: [duplicate_ids]}
    """
    duplicates = {}
    seen = {}  # normalized_title -> node
    duplicate_ids = set()
    
    for node in nodes:
        title = node.get("title", "")
        norm_title = normalize_title(title)
        node_id = node.get("id", "")
        
        if node_id in duplicate_ids:
            continue
            
        # 完全一致チェック
        if norm_title in seen:
            existing = seen[norm_title]
            existing_id = existing.get("id", "")
            if existing_id not in duplicates:
                duplicates[existing_id] = []
            duplicates[existing_id].append(node_id)
            duplicate_ids.add(node_id)
            continue
        
        # 類似度チェック
        found_similar = False
        for existing_title, existing_node in seen.items():
            if similarity(norm_title, existing_title) >= threshold:
                existing_id = existing_node.get("id", "")
                if existing_id not in duplicates:
                    duplicates[existing_id] = []
                duplicates[existing_id].append(node_id)
                duplicate_ids.add(node_id)
                found_similar = True
                break
        
        if not found_similar:
            seen[norm_title] = node
    
    return duplicates, duplicate_ids

def cleanup_universe(dry_run=False):
    """メインのクリーンアップ処理"""
    print("=" * 60)
    print("🧹 EGO Universe Duplicate Cleaner")
    print("=" * 60)
    
    data = load_universe()
    if not data:
        return
    
    nodes = data.get("nodes", [])
    links = data.get("links", [])
    
    print(f"\n[BEFORE]")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Links: {len(links)}")
    
    # 重複検出
    print(f"\n[ANALYZING] 重複を検出中...")
    duplicates, duplicate_ids = find_duplicates(nodes)
    
    if not duplicate_ids:
        print("✅ 重複は見つかりませんでした！")
        return
    
    print(f"\n[DUPLICATES FOUND] {len(duplicate_ids)} 件の重複")
    
    # サンプル表示
    print("\n[SAMPLE] 重複の例:")
    sample_count = 0
    for keep_id, dup_ids in list(duplicates.items())[:5]:
        keep_node = next((n for n in nodes if n.get("id") == keep_id), None)
        if keep_node:
            print(f"  ✓ KEEP: {keep_node.get('title', '')[:40]}...")
            for dup_id in dup_ids[:2]:
                dup_node = next((n for n in nodes if n.get("id") == dup_id), None)
                if dup_node:
                    print(f"    ✗ DROP: {dup_node.get('title', '')[:40]}...")
            sample_count += 1
    
    # 重複を削除
    new_nodes = [n for n in nodes if n.get("id") not in duplicate_ids]
    
    # リンクも更新（削除されたノードへのリンクを除去）
    new_links = [
        l for l in links 
        if l.get("source") not in duplicate_ids and l.get("target") not in duplicate_ids
    ]
    
    data["nodes"] = new_nodes
    data["links"] = new_links
    
    print(f"\n[AFTER]")
    print(f"  Nodes: {len(new_nodes)} (削除: {len(nodes) - len(new_nodes)})")
    print(f"  Links: {len(new_links)} (削除: {len(links) - len(new_links)})")
    
    # 保存
    save_universe(data, dry_run)
    
    print("\n✅ クリーンアップ完了！")
    
    return {
        "before_nodes": len(nodes),
        "after_nodes": len(new_nodes),
        "removed": len(duplicate_ids)
    }

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("⚠️  DRY-RUN モード: 実際の変更は行われません\n")
    cleanup_universe(dry_run=dry_run)
