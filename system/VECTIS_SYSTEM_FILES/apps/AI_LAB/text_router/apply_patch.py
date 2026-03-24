"""
Text Router知識蓄積機能追加スクリプト
"""
import codecs

# ファイルを読み込み
with codecs.open(r'c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\text_router\app.py', 'r', 'utf-8') as f:
    lines = f.readlines()

# 追加するコード
knowledge_code = [
    "        \r\n",
    "        # 🌟 知識として蓄積（教養とエゴ）\r\n",
    "        self.save_as_knowledge(text, best_category, scores)\r\n",
    "        self.save_to_ego_memory(text, best_category)\r\n",
]

# 430行目（インデックス429）の後に挿入
insert_pos = 430  # 430行目の後 (0-indexed では429)
for i, code_line in enumerate(knowledge_code):
    lines.insert(insert_pos + i, code_line)

# ダイアログメッセージを変更 (元の434行が今437行になっている)
# "「{best_category}」に振り分けられました。\\n\\nこのアプリを起動しますか？"
# を探して置換
for i, line in enumerate(lines):
    if i >= 430 and i <= 445:  # 範囲を絞る
        if 'に振り分けられました' in line and 'このアプリを起動しますか' in line:
            lines[i] = '            f"「{best_category}」に振り分けられました。\\n\\n✅ 知識カードとエゴメモリに保存しました。\\n\\nこのアプリを起動しますか？"\r\n'
            print(f"✅ Line {i+1}: Updated dialog message")
            break

# ファイルに書き戻す
with codecs.open(r'c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\text_router\app.py', 'w', 'utf-8') as f:
    f.writelines(lines)

print("✅ Text Router has been updated with knowledge accumulation features!")
print("📚 Knowledge cards will be saved to: knowledge_cards/outputs/cards/")
print("🧠 Ego memories will be saved to: memory/data/")
