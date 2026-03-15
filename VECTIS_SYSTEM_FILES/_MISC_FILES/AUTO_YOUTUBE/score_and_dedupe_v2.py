"""
YouTube要約の新規性スコア計算 & 重複削除スクリプト v2
======================================================
- タイトルの類似度でグループ化
- 同じトピック（Gemini使い方など）の動画をまとめて削除
- 各カテゴリで最も新規性が高いものだけ残す
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# ========== 設定 ==========
NOTES_DIR = Path(r"C:\Users\Yuto\OneDrive - Hiroshima University\app\apps\memory\data\youtube_notes")
DUPLICATES_DIR = NOTES_DIR / "_duplicates"
SCORES_OUTPUT = Path(r"C:\Users\Yuto\OneDrive - Hiroshima University\app\AUTO_YOUTUBE\novelty_scores_v2.json")

# 「同じ話題」と見なすキーワードパターン
TOPIC_PATTERNS = {
    'Gemini使い方': [r'gemini.*(使い方|活用|入門|基礎|初心者|解説|完全|マスター)', r'(使い方|活用).*gemini'],
    'Gemini紹介': [r'gemini.*(凄い|すごい|神|最強|おすすめ|革命)', r'(凄い|すごい|神|最強).*gemini'],
    'ChatGPT比較': [r'chatgpt.*(gemini|超え|比較)', r'gemini.*(chatgpt|超え)'],
    'Googleニュース': [r'(速報|live|ライブ).*ニュース', r'tbs.*news', r'news.*dig'],
    'Pixel紹介': [r'google\s*pixel', r'pixel\s*\d'],
    '地政学': [r'地政学', r'geopolit'],
    '石丸伸二': [r'石丸伸二'],
    '高橋弘樹': [r'高橋弘樹', r'rehacq'],
    'ひろゆき': [r'ひろゆき'],
    '言語学ラジオ': [r'(ゆる|言語学).*ラジオ', r'オノマトペ'],
}

# 各トピックで残す最大件数
MAX_PER_TOPIC = 3

# ========== ユーティリティ関数 ==========

def extract_title_from_filename(filename: str) -> str:
    """ファイル名からタイトルを抽出"""
    name = filename.replace('.md', '')
    if name.startswith('YouTube_'):
        name = name[8:]
    parts = name.rsplit('_', 1)
    if len(parts) == 2 and len(parts[1]) == 11:
        return parts[0]
    return name


def detect_topic(title: str, content: str) -> str:
    """タイトルと内容からトピックを判定"""
    text = (title + ' ' + content).lower()
    
    for topic, patterns in TOPIC_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return topic
    
    return 'その他'


def extract_key_entities(content: str) -> set:
    """コンテンツから重要なエンティティを抽出"""
    entities = set()
    
    # 固有名詞っぽいもの
    # 英語の固有名詞（大文字始まり）
    entities.update(re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', content))
    
    # 日本語の固有名詞っぽいもの（カタカナ3文字以上）
    entities.update(re.findall(r'[ァ-ヴー]{3,}', content))
    
    return entities


def calculate_novelty_score(note: dict, all_notes: list, topic_counts: dict) -> float:
    """新規性スコアを計算"""
    # 基本スコア
    base_score = 1.0
    
    # 同じトピックの動画が多いほど減点
    topic = note['topic']
    topic_count = topic_counts.get(topic, 1)
    
    if topic != 'その他':
        # 同じトピックが多いと大幅減点
        base_score -= min(0.5, (topic_count - 1) * 0.1)
    
    # エンティティの独自性
    my_entities = note['entities']
    other_entities = set()
    for other in all_notes:
        if other['filename'] != note['filename']:
            other_entities.update(other['entities'])
    
    if my_entities:
        unique_entities = my_entities - other_entities
        entity_uniqueness = len(unique_entities) / len(my_entities) if my_entities else 0
        base_score += entity_uniqueness * 0.3
    
    return max(0, min(1, base_score))


# ========== メイン処理 ==========

def main():
    print("=" * 60)
    print("📊 YouTube要約 新規性スコア計算 & 重複削除 v2")
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
            title = extract_title_from_filename(filepath.name)
            topic = detect_topic(title, content)
            entities = extract_key_entities(content)
            
            notes.append({
                'filepath': filepath,
                'filename': filepath.name,
                'title': title,
                'content': content,
                'topic': topic,
                'entities': entities,
                'size': filepath.stat().st_size,
                'mtime': filepath.stat().st_mtime,
            })
        except Exception as e:
            print(f"   ⚠️ 読み込みエラー: {filepath.name} - {e}")
    
    print(f"   ✅ {len(notes)}件のファイルを読み込みました")
    
    # トピック別集計
    print("\n📊 トピック別分布:")
    topic_counts = Counter(n['topic'] for n in notes)
    for topic, count in topic_counts.most_common():
        marker = "🔴" if count > MAX_PER_TOPIC and topic != 'その他' else "🟢"
        print(f"   {marker} {topic}: {count}件")
    
    # 新規性スコア計算
    print("\n🔍 新規性スコア計算中...")
    for note in notes:
        note['novelty_score'] = calculate_novelty_score(note, notes, topic_counts)
    
    # トピック別にソートして、上位以外を削除対象に
    print(f"\n🗑️ 重複検出中（各トピック上位{MAX_PER_TOPIC}件を残す）...")
    
    topic_groups = defaultdict(list)
    for note in notes:
        topic_groups[note['topic']].append(note)
    
    to_remove = []
    to_keep = []
    
    for topic, group in topic_groups.items():
        if topic == 'その他':
            # その他は全部残す
            to_keep.extend(group)
            continue
        
        # 新規性スコアと新しさでソート（新しくてユニークなものを優先）
        sorted_group = sorted(group, key=lambda x: (x['novelty_score'], x['mtime']), reverse=True)
        
        # 上位N件を残す
        to_keep.extend(sorted_group[:MAX_PER_TOPIC])
        to_remove.extend(sorted_group[MAX_PER_TOPIC:])
    
    print(f"   🔴 削除対象: {len(to_remove)}件")
    print(f"   🟢 残す: {len(to_keep)}件")
    
    # 削除対象の詳細
    if to_remove:
        print("\n📋 削除される動画（トピック別）:")
        remove_by_topic = defaultdict(list)
        for note in to_remove:
            remove_by_topic[note['topic']].append(note['title'][:50])
        
        for topic, titles in remove_by_topic.items():
            print(f"\n   【{topic}】({len(titles)}件)")
            for title in titles[:5]:  # 最大5件表示
                print(f"      - {title}")
            if len(titles) > 5:
                print(f"      ... 他 {len(titles) - 5}件")
    
    # ユーザー確認
    print("\n" + "=" * 60)
    confirm = input("🔴 上記のファイルを _duplicates に移動しますか？ (y/N): ").strip().lower()
    
    if confirm == 'y':
        print("\n🗑️ ファイル移動中...")
        moved_count = 0
        for note in to_remove:
            src = note['filepath']
            dst = DUPLICATES_DIR / note['filename']
            try:
                shutil.move(str(src), str(dst))
                moved_count += 1
            except Exception as e:
                print(f"   ⚠️ 移動エラー: {e}")
        
        print(f"   ✅ {moved_count}件を _duplicates フォルダに移動しました")
    else:
        print("   ⏭️ スキップしました")
    
    # スコア保存
    print(f"\n💾 スコアを保存中...")
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'total_files': len(notes),
        'duplicates_detected': len(to_remove),
        'topic_distribution': dict(topic_counts),
        'scores': {
            n['filename']: {
                'title': n['title'],
                'topic': n['topic'],
                'novelty_score': round(n['novelty_score'], 3),
            }
            for n in notes
        },
    }
    
    with open(SCORES_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ {SCORES_OUTPUT} に保存しました")
    
    print("\n" + "=" * 60)
    print("✨ 処理完了！")
    print("=" * 60)


if __name__ == "__main__":
    main()
