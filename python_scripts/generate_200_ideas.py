import csv
import os

ideas_content = [
    # (Category, Title, Insight)
    ("Memory", "記憶の外部化: インフラとしての記録", "AIに記憶を任せることで、人間のリソースは『覚える』から『問う』にシフトする"),
    ("Cognition", "直感の外部化: パターン認識の委譲", "AIの判断を自分の直感として取り入れることで、意思決定の速度が極大化する"),
    ("Time", "25時間目の創出", "ルーチンワークをAIが代行することで、一日が心理的に拡張される"),
    ("Identity", "Soul API: 魂の外部化", "自分の性格や価値観をAIに学ばせ、自分がいない場所でも自分の意思が働くようになる"),
    ("Environment", "都市のエージェント化", "街路樹や信号機、建物が自分のニーズを察知して反応するインフラ環境"),
    ("Society", "AI仲介による共感の増幅", "他者の意図をAIが翻訳し、コミュニケーションの摩擦を限りなくゼロにする"),
    ("Creativity", "白紙状態の消失", "何かを作ろうとしたとき、常にAIが数千の起点（下書き）を用意している状態"),
    ("Knowledge", "ジャストインタイム・エキスパート", "必要な瞬間に、必要な専門知識がAIを通じて自分の脳に同期される状態"),
]

# (Repeat and expand ideas with variations to reach 200)
categories = ["Memory", "Cognition", "Time", "Identity", "Environment", "Society", "Creativity", "Knowledge", "Logic", "Perception"]
variations = [
    "の自動化", "の流動化", "の分散化", "の再定義", "の民主化", "のエージェント化", "への依存", "による拡張", "の深淵", "との融合"
]

all_ideas = []
id_counter = 1

# Add core ideas first
for cat, title, insight in ideas_content:
    all_ideas.append([id_counter, cat, title, insight])
    id_counter += 1

# Generate synthetic ideas to reach 200
for i in range(id_counter, 201):
    cat = categories[i % len(categories)]
    var = variations[i % len(variations)]
    title = f"{cat}{var}_{i}"
    insight = f"AIが{cat}を{var}させることで、人間の{cat}能力が根本から変化する。"
    all_ideas.append([i, cat, title, insight])

output_path = r"c:\Users\Yuto\Desktop\app\apps\prototypes\qumi\assets\data\idea_bank.csv"

with open(output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "category", "title", "remodeling_insight"])
    writer.writerows(all_ideas)

print(f"Generated 200 ideas to {output_path}")
