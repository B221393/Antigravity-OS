"""
Ego System テスト＆修正完了スクリプト
Text Routerでテスト用のエゴメモリを作成
"""
import os
import json
from datetime import datetime

# 保存先
ego_dir = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\memory\data"
os.makedirs(ego_dir, exist_ok=True)

print("="*60)
print("🧠 Ego System - テスト用メモリ作成")
print("="*60)
print()

# テスト用のエゴメモリを作成
test_memories = [
    {
        "category": "就活・ES関連",
        "content": "講談社の編集者になりたい。読者の心を揺さぶるストーリーを作りたい。大学では文芸サークルで編集長をやっていた経験がある。",
        "context_note": "就職活動への強い意欲"
    },
    {
        "category": "プログラミング",
        "content": "Pythonでデータ分析をするのが好き。特にPandasとMatplotlibを使ったビジュアライゼーションが得意。",
        "context_note": "技術的な興味"
    },
    {
        "category": "将棋",
        "content": "藤井聡太の対局を見るのが趣味。特に序盤の角換わりが好き。いつか将棋AIを作ってみたい。",
        "context_note": "趣味と学習意欲"
    },
    {
        "category": "日記・メモ",
        "content": "毎日コツコツ努力することが大切だと思う。小さな積み重ねが大きな成果になる。",
        "context_note": "価値観と信念"
    },
    {
        "category": "英語・TOEIC",
        "content": "TOEICで800点を目指している。毎日30分は英語に触れる習慣をつけたい。",
        "context_note": "学習目標"
    }
]

created = 0
for i, mem in enumerate(test_memories):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    ego_data = {
        "type": "thought",
        "category": mem["category"],
        "timestamp": datetime.now().isoformat(),
        "content": mem["content"],
        "context": {
            "source": "ego_system_test",
            "auto_captured": False,
            "note": mem["context_note"],
            "routed_category": mem["category"]
        },
        "metadata": {
            "length": len(mem["content"]),
            "has_keywords": True,
            "test_memory": True
        }
    }
    
    filename = f"ego_thought_{timestamp}_test_{i+1}.json"
    filepath = os.path.join(ego_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(ego_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ [{i+1}/5] {filename}")
    print(f"   カテゴリ: {mem['category']}")
    print(f"   内容: {mem['content'][:50]}...")
    print()
    
    created += 1
    
    # 各ファイル作成の間に少し待機
    import time
    time.sleep(0.1)

print("="*60)
print(f"✅ {created}個のテストメモリを作成しました")
print()
print(f"📁 保存先: {ego_dir}")
print()

# 確認
all_ego_files = [f for f in os.listdir(ego_dir) if f.startswith("ego_thought_")]
print(f"📊 現在の合計エゴメモリ数: {len(all_ego_files)}個")
print()

print("="*60)
print("🎯 次のステップ:")
print()
print("1. Ego Personaアプリを起動:")
print("   streamlit run EGO_SYSTEM_FILES\\apps\\ego_persona\\app.py --server.port 8510")
print()
print("2. ブラウザで http://localhost:8510 を開く")
print()
print("3. サイドバーでメモリを確認")
print()
print("4. Egoと会話してみる:")
print("   例: 「私について教えて」")
print("   例: 「将棋について話そう」")
print("   例: 「就活のアドバイスをください」")
print()
print("="*60)
print()
print("✨ Ego Personaが修正され、Text Routerとの連携も有効化されました！")
print("   これからText Routerで入力したテキストは自動的にEgoが学習します。")
print()
