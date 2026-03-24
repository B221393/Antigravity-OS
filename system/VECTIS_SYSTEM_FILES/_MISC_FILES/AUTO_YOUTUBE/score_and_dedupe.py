"""
YouTube要約の新規性スコア計算 & 重複削除スクリプト
===================================================
- 各要約の内容をキーワード抽出して類似度を計算
- 新規性スコア: 他の動画と被っていないほど高い
- 重複（80%以上類似）は _duplicates フォルダに移動
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib

# ========== 設定 ==========
NOTES_DIR = Path(r"C:\Users\Yuto\OneDrive - Hiroshima University\app\apps\memory\data\youtube_notes")
DUPLICATES_DIR = NOTES_DIR / "_duplicates"
SCORES_OUTPUT = Path(r"C:\Users\Yuto\OneDrive - Hiroshima University\app\AUTO_YOUTUBE\novelty_scores.json")

# 類似度のしきい値（これ以上で重複と判定）
SIMILARITY_THRESHOLD = 0.65

# ========== ユーティリティ関数 ==========

def extract_keywords(text: str) -> set:
    """テキストからキーワードを抽出"""
    # 日本語と英語の単語を抽出
    # 日本語: 2文字以上の連続
    jp_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}', text)
    # 英語: 3文字以上の単語
    en_words = re.findall(r'[A-Za-z]{3,}', text)
    
    # ストップワード除外
    stop_words = {
        # 日本語
        'これ', 'それ', 'あれ', 'この', 'その', 'ある', 'いる', 'する', 'なる', 'できる',
        'という', 'として', 'について', 'ため', 'こと', 'もの', 'ところ', 'よう', 'など',
        'から', 'まで', 'より', 'ほど', 'くらい', 'ぐらい', 'だけ', 'しか', 'ばかり',
        '動画', '視聴', '紹介', '解説', '説明', '方法', '使い方', '徹底', '完全',
        # 英語
        'the', 'and', 'for', 'that', 'with', 'this', 'from', 'have', 'are', 'was',
        'were', 'been', 'being', 'has', 'had', 'will', 'would', 'could', 'should',
        'youtube', 'video', 'watch', 'https', 'www', 'com'
    }
    
    keywords = set()
    for w in jp_words + [w.lower() for w in en_words]:
        if w not in stop_words and len(w) >= 2:
            keywords.add(w)
    
    return keywords


def calculate_similarity(keywords1: set, keywords2: set) -> float:
    """2つのキーワードセット間のJaccard類似度を計算"""
    if not keywords1 or not keywords2:
        return 0.0
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    return intersection / union if union > 0 else 0.0


def extract_title_from_filename(filename: str) -> str:
    """ファイル名からタイトルを抽出"""
    # YouTube_タイトル_ID.md の形式
    name = filename.replace('.md', '')
    if name.startswith('YouTube_'):
        name = name[8:]
    # 最後の _xxxxx はIDなので除去
    parts = name.rsplit('_', 1)
    if len(parts) == 2 and len(parts[1]) == 11:  # YouTube IDは11文字
        return parts[0]
    return name


def get_topic_category(keywords: set) -> str:
    """キーワードからトピックカテゴリを推定"""
    categories = {
        'AI・テクノロジー': {'gemini', 'ai', 'chatgpt', 'google', 'openai', 'pixel', 'llm', '人工知能', '生成'},
        '地政学・国際': {'地政学', 'ベネズエラ', 'トランプ', '中国', 'ロシア', '米国', 'アメリカ', '国際'},
        '言語学': {'言語', '方言', '言葉', 'オノマトペ', '文法', '敬語', '日本語', '韓国語'},
        'ビジネス・経済': {'経済', '投資', '株', '決算', '企業', 'ビジネス', '起業', '年金'},
        'ニュース・時事': {'速報', 'live', 'ニュース', '事件', '地震', '津波', '選挙'},
        '教養・学問': {'歴史', '哲学', '科学', '数学', '物理', '心理学', '研究'},
        'エンタメ': {'映画', '音楽', 'ゲーム', 'アニメ', 'マンガ', 'お笑い'},
    }
    
    for category, cat_keywords in categories.items():
        if keywords & cat_keywords:
            return category
    return 'その他'


# ========== メイン処理 ==========

def main():
    print("=" * 60)
    print("📊 YouTube要約 新規性スコア計算 & 重複削除")
    print("=" * 60)
    
    # 重複フォルダ作成
    DUPLICATES_DIR.mkdir(exist_ok=True)
    
    # 全ファイル読み込み
    print("\n📂 ファイル読み込み中...")
    notes = []
    
    for filepath in NOTES_DIR.glob("YouTube_*.md"):
        if filepath.parent.name == "_duplicates":
            continue
        
        try:
            content = filepath.read_text(encoding='utf-8')
            keywords = extract_keywords(content)
            title = extract_title_from_filename(filepath.name)
            
            notes.append({
                'filepath': filepath,
                'filename': filepath.name,
                'title': title,
                'content': content,
                'keywords': keywords,
                'category': get_topic_category(keywords),
                'size': filepath.stat().st_size,
                'mtime': filepath.stat().st_mtime,
            })
        except Exception as e:
            print(f"   ⚠️ 読み込みエラー: {filepath.name} - {e}")
    
    print(f"   ✅ {len(notes)}件のファイルを読み込みました")
    
    # カテゴリ別集計
    print("\n📊 カテゴリ別分布:")
    category_counts = Counter(n['category'] for n in notes)
    for cat, count in category_counts.most_common():
        print(f"   {cat}: {count}件")
    
    # 類似度計算 & 重複検出
    print(f"\n🔍 類似度計算中（しきい値: {SIMILARITY_THRESHOLD*100:.0f}%）...")
    
    duplicates = []  # (index, similar_to_index, similarity)
    novelty_scores = {}  # filename -> score
    
    for i, note1 in enumerate(notes):
        max_similarity = 0.0
        similar_to = None
        
        for j, note2 in enumerate(notes):
            if i >= j:  # 自分自身と、すでに比較済みはスキップ
                continue
            
            sim = calculate_similarity(note1['keywords'], note2['keywords'])
            
            if sim > max_similarity:
                max_similarity = sim
                similar_to = j
            
            # 重複判定（しきい値超え & 古い方を削除対象に）
            if sim >= SIMILARITY_THRESHOLD:
                # 新しい方を残す（mtime比較）
                if note1['mtime'] < note2['mtime']:
                    duplicates.append((i, j, sim))
                else:
                    duplicates.append((j, i, sim))
        
        # 新規性スコア = 1 - 最大類似度（被りが少ないほど高い）
        novelty = 1.0 - max_similarity
        novelty_scores[note1['filename']] = {
            'novelty_score': round(novelty, 3),
            'max_similarity': round(max_similarity, 3),
            'similar_to': notes[similar_to]['title'] if similar_to else None,
            'category': note1['category'],
            'title': note1['title'],
        }
    
    # 重複のユニーク化
    duplicates_to_remove = set()
    for dup_idx, keep_idx, sim in duplicates:
        duplicates_to_remove.add(dup_idx)
    
    print(f"   ✅ 類似度計算完了")
    print(f"   🔴 重複検出: {len(duplicates_to_remove)}件")
    
    # 新規性スコアでソート（低い順 = 被りが多い順）
    sorted_by_novelty = sorted(novelty_scores.items(), key=lambda x: x[1]['novelty_score'])
    
    print("\n🔴 新規性が低い動画TOP10（被りが多い）:")
    for filename, data in sorted_by_novelty[:10]:
        print(f"   [{data['novelty_score']:.2f}] {data['title'][:40]}...")
        print(f"        └─ 類似: {data['similar_to'][:30] if data['similar_to'] else 'N/A'}...")
    
    print("\n🟢 新規性が高い動画TOP10（ユニーク）:")
    for filename, data in sorted_by_novelty[-10:]:
        print(f"   [{data['novelty_score']:.2f}] {data['title'][:50]}")
    
    # 重複ファイルの移動
    if duplicates_to_remove:
        print(f"\n🗑️ 重複ファイルを移動中...")
        moved_count = 0
        for idx in duplicates_to_remove:
            note = notes[idx]
            src = note['filepath']
            dst = DUPLICATES_DIR / note['filename']
            try:
                shutil.move(str(src), str(dst))
                moved_count += 1
                print(f"   ➡️ {note['title'][:40]}...")
            except Exception as e:
                print(f"   ⚠️ 移動エラー: {e}")
        
        print(f"   ✅ {moved_count}件を _duplicates フォルダに移動しました")
    
    # スコア保存
    print(f"\n💾 スコアを保存中...")
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'total_files': len(notes),
        'duplicates_removed': len(duplicates_to_remove),
        'category_distribution': dict(category_counts),
        'scores': novelty_scores,
    }
    
    with open(SCORES_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ {SCORES_OUTPUT} に保存しました")
    
    print("\n" + "=" * 60)
    print("✨ 処理完了！")
    print(f"   📁 残りファイル: {len(notes) - len(duplicates_to_remove)}件")
    print(f"   🗑️ 削除（移動）: {len(duplicates_to_remove)}件")
    print("=" * 60)


if __name__ == "__main__":
    main()
