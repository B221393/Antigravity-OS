"""
Text Router デモ実行スクリプト
知識蓄積機能のテストを自動実行
"""
import time
import os
import json
from datetime import datetime

# デモ用テキストサンプル
demo_texts = [
    {
        "text": "講談社の編集者になりたい。読者の心を揺さぶるストーリーを作りたい。大学では文芸サークルで編集長をやっていた経験がある。",
        "expected_category": "就活・ES関連",
        "description": "就活ES用の思考"
    },
    {
        "text": "Pythonでファイルを読み込むときはwith open()を使う。これでファイルを自動的に閉じてくれるから便利。例外処理も簡単。",
        "expected_category": "プログラミング",
        "description": "プログラミングTips"
    },
    {
        "text": "今日は藤井聡太の対局を見た。序盤の角換わりから中盤の攻め合いが素晴らしかった。将棋は本当に奥が深い。",
        "expected_category": "将棋",
        "description": "将棋の感想"
    },
    {
        "text": "TOEICの勉強を始めた。Part5の文法問題から攻略していく。毎日30分は英語に触れる習慣をつけたい。",
        "expected_category": "英語・TOEIC",
        "description": "英語学習メモ"
    },
    {
        "text": "今日の予定: 午前中にES提出、午後は面接対策、夜は友達と就活の相談。忙しいけど頑張ろう。",
        "expected_category": "スケジュール",
        "description": "タスクメモ"
    }
]

print("=" * 60)
print("🔀 TEXT ROUTER - 知識蓄積デモ")
print("=" * 60)
print()

# 保存先ディレクトリ
knowledge_dir = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\knowledge_cards\outputs\cards"
ego_dir = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\memory\data"

print("📁 保存先ディレクトリ:")
print(f"   Knowledge Cards: {knowledge_dir}")
print(f"   Ego Memory:      {ego_dir}")
print()

# 既存ファイル数をカウント
knowledge_before = len([f for f in os.listdir(knowledge_dir) if f.endswith('.kcard')]) if os.path.exists(knowledge_dir) else 0
ego_before = len([f for f in os.listdir(ego_dir) if f.startswith('ego_thought_')]) if os.path.exists(ego_dir) else 0

print(f"📊 現在の蓄積数:")
print(f"   Knowledge Cards: {knowledge_before}件")
print(f"   Ego Memories:    {ego_before}件")
print()

print("=" * 60)
print("💡 デモ用テキストサンプル")
print("=" * 60)
print()
print("以下のテキストをText Routerに入力すると、")
print("自動的に分類されて知識として蓄積されます:")
print()

for i, demo in enumerate(demo_texts, 1):
    print(f"【サンプル {i}】 {demo['description']}")
    print(f"カテゴリ予測: {demo['expected_category']}")
    print(f"テキスト: \"{demo['text'][:50]}...\"")
    print()

print("=" * 60)
print()
print("🎯 Text Routerの使い方:")
print()
print("1. 起動したText Routerウィンドウを確認")
print("2. 左側のテキストエリアに上記のサンプルをコピペ")
print("3. 「🚀 仕分け開始」ボタンをクリック")
print("4. 自動的にカテゴリ判定 + 知識カード + エゴメモリに保存")
print("5. 該当アプリの起動を確認")
print()

print("=" * 60)
print()
print("📚 蓄積される知識の例:")
print()
print("Knowledge Card (.kcard):")
print(json.dumps({
    "title": "就活・ES関連 - 2026-01-16",
    "genre": "就活・ES関連",
    "rarity": "Epic",
    "timestamp": "2026-01-16 20:00:00",
    "content": "講談社の編集者になりたい...",
    "source": "Text Router - 自動仕分け"
}, ensure_ascii=False, indent=2))
print()

print("Ego Memory (.json):")
print(json.dumps({
    "type": "thought",
    "category": "就活・ES関連",
    "timestamp": "2026-01-16T20:00:00",
    "content": "講談社の編集者になりたい...",
    "context": {
        "source": "text_router",
        "auto_captured": True
    }
}, ensure_ascii=False, indent=2))
print()

print("=" * 60)
print()
print("✅ Text Routerが起動しました！")
print("   上記のサンプルテキストを試してみてください。")
print()
print("🎉 使えば使うほど知識が蓄積され、")
print("   あなた専用のAI知識ライブラリが完成します！")
print()
print("=" * 60)

# 待機して、ユーザーが試した後の結果を確認
input("\n⏸️  テキストを試した後、Enterキーを押して結果を確認してください...")

print()
print("=" * 60)
print("📊 蓄積結果の確認")
print("=" * 60)
print()

# 蓄積後のファイル数をカウント
knowledge_after = len([f for f in os.listdir(knowledge_dir) if f.endswith('.kcard')]) if os.path.exists(knowledge_dir) else 0
ego_after = len([f for f in os.listdir(ego_dir) if f.startswith('ego_thought_')]) if os.path.exists(ego_dir) else 0

print(f"📈 蓄積数の変化:")
print(f"   Knowledge Cards: {knowledge_before}件 → {knowledge_after}件 (+{knowledge_after - knowledge_before})")
print(f"   Ego Memories:    {ego_before}件 → {ego_after}件 (+{ego_after - ego_before})")
print()

if knowledge_after > knowledge_before:
    print("✅ 知識カードが新しく作成されました！")
    print(f"   場所: {knowledge_dir}")
    
    # 最新のファイルを表示
    kcard_files = sorted(
        [f for f in os.listdir(knowledge_dir) if f.endswith('.kcard')],
        key=lambda x: os.path.getmtime(os.path.join(knowledge_dir, x)),
        reverse=True
    )[:5]
    
    print()
    print("📚 最新の知識カード:")
    for f in kcard_files:
        print(f"   - {f}")
    print()

if ego_after > ego_before:
    print("✅ エゴメモリが新しく作成されました！")
    print(f"   場所: {ego_dir}")
    
    # 最新のファイルを表示
    ego_files = sorted(
        [f for f in os.listdir(ego_dir) if f.startswith('ego_thought_')],
        key=lambda x: os.path.getmtime(os.path.join(ego_dir, x)),
        reverse=True
    )[:5]
    
    print()
    print("🧠 最新のエゴメモリ:")
    for f in ego_files:
        print(f"   - {f}")
    print()

print("=" * 60)
print()
print("🎊 デモ完了！")
print()
print("💡 次のステップ:")
print("   1. Knowledge Cardsアプリで知識を閲覧")
print("   2. Ego Personaアプリで分身と会話")
print("   3. ES Assistantの「分身生成」で自動ES作成")
print()
print("=" * 60)
