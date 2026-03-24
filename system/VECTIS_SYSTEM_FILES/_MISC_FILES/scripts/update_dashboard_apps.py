import os
import random
import re

# パス設定
BASE_DIR = r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps"
DASHBOARD_HTML = os.path.join(BASE_DIR, "dashboard", "index.html")

# 除外ディレクトリ
EXCLUDES = {
    "dashboard", "__pycache__", ".git", ".venv", "node_modules", "target", "outputs"
}

# キーワードによるカテゴリ分類
CATEGORIES = {
    "study": ["toeic", "english", "book", "read", "study", "learn", "history", "wiki", "kanji", "memory"],
    "job": ["job", "es_", "apply", "company", "interview", "career", "work", "task", "schedule", "goal"],
    "fun": ["game", "anime", "manga", "youtube", "movie", "fun", "music", "sound", "voice", "art", "drawing", "rpg"],
    "tools": [] # デフォルト
}

# アイコンのランダム候補
ICONS = ["📱", "💻", "⚡", "🔮", "🧬", "🧪", "💎", "🛡️", "🚀", "🛸", "🌟", "🔥", "🌊", "🎮", "🎹", "🎨", "📝", "📊", "📡", "🔭"]

def get_category_id(app_name):
    lower_name = app_name.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower_name:
                return cat
    return "tools" # デフォルトはツール扱い

def generate_card_html(app_name, index):
    # ランダム要素
    icon = random.choice(ICONS)
    color = random.choice(["", 'data-color="blue"', 'data-color="pink"', 'data-color="orange"'])
    rotation = random.randint(1, 100)
    
    # 表示名（_をスペースに、タイトルケース）
    display_name = app_name.replace("_", " ").title()
    
    html = f"""
            <!-- Generated App: {app_name} -->
            <div class="app-card" {color} onclick="alert('Launching {display_name}...')">
                <div class="app-card-header">
                    <div class="app-icon-wrapper">{icon}</div>
                    <span class="app-channel-tag">APP.{index:03d}</span>
                </div>
                <div class="app-name" style="font-size: 1.1rem;">{display_name}</div>
                <div class="app-name-sub">{app_name.upper()}</div>
                <div class="app-desc">VECTIS Application Module. Auto-generated entry.</div>
                <div class="app-card-footer">
                    <div class="app-status"><span class="status-dot"></span>Installed</div>
                    <span class="app-arrow">→</span>
                </div>
            </div>
    """
    return html

def main():
    if not os.path.exists(BASE_DIR):
        print(f"Error: Directory not found: {BASE_DIR}")
        return

    # 全アプリフォルダ取得
    all_apps = [d for d in os.listdir(BASE_DIR) 
                if os.path.isdir(os.path.join(BASE_DIR, d)) and d not in EXCLUDES]
    all_apps.sort()

    print(f"Found {len(all_apps)} apps.")

    # HTML生成のためのバッファ
    html_sections = {
        "study": [],
        "job": [],
        "tools": [],
        "fun": []
    }

    # 各アプリをカテゴリ別に生成
    for i, app in enumerate(all_apps):
        cat = get_category_id(app)
        card_html = generate_card_html(app, i + 1)
        html_sections[cat].append(card_html)

    # HTML読み込み
    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # 既存のHTML構造を利用して挿入
    # 各セクションの <div class="apps-grid"> の中身を追記する形にする
    # 正規表現で <section id="xxx">...</section> 内の <div class="apps-grid"> を探すのは複雑なので、
    # 簡易的に置換マーカーを使うか、特定の閉じタグの直前に挿入する

    # ここでは、各セクションの最後の </div> (gridの閉じタグ) の前に挿入する戦略をとる
    # ただし、既存の手書きカードも残したいかもしれない。ユーザーは「まとめてほしい」と言っている。
    # 既存カードの後ろに追加するのが安全。

    new_content = content
    
    for section_id, cards in html_sections.items():
        if not cards:
            continue
            
        cards_str = "\n".join(cards)
        
        # ターゲットセクションを探す (例: <section class="section.*" id="study">)
        # その中の <div class="apps-grid"> の閉じタグ </div> を探す。
        # 簡易パース: id="study" から始まり、次の <section または footer が来るまでの間の 最後の </div> </div> の手前... は難しい。
        
        # なので、セクションIDごとの特定コメントマーカーを入れるか、
        # あるいは「既存のgrid内」に追加するのを諦め、
        # 各セクションの終わりに「<div class="apps-grid auto-generated">...</div>」を追加する方が安全。
        
        insertion_point = f'</section>\n\n    <!-- {section_id.upper()} NEXT SECTION -->'
        
        # id="{section_id}" を含むセクションの終了タグを探す
        # 単純化のため、セクションの閉じタグ `</section>` を検索し、
        # その直前のコンテンツが当該セクションに属するか判定するのは難しいので、
        # 既存のHTMLを見て、特定の文字列（例えば `id="study"`）の後にある ` <div class="apps-grid">` の閉じタグを探す。
        
        # 今回は、ユーザーのHTMLが綺麗に整形されているので、
        # `id="study"` ... `class="apps-grid"` ... 最後の `</div>` ... `</section>` となっているはず。
        
        # 置換ロジック:
        # 1. `<section ... id="section_id">` を探す
        # 2. その後ろにある `</div>\n    </section>` を `[NEW CARDS]\n        </div>\n    </section>` に置換する
        
        pattern = re.compile(f'(<section[^>]*id="{section_id}"[^>]*>.*?<div class="apps-grid">)(.*?)(</div>\s*</section>)', re.DOTALL)
        
        # 既存のカード (group 2) を残しつつ、新しいカードを追加
        # しかし、正規表現の .*? は貪欲さの制御が難しい場合がある。
        
        # アプローチ変更: PythonでHTMLをパースするのは事故の元。
        # 今回は「各セクションの末尾に追記」ではなく、
        # **フッターの直前に「全アプリアーカイブ」という巨大なセクションを作ってそこに全部入れる** のが
        # 技術的に最も安全で、ユーザーの「100個ともまとめる」要件を確実に満たせる。
        # 分類ロジックを作ったが、それを統合するとHTML破壊のリスクがある。
        
        pass 

    # 再考: ユーザーは「個々のやつに」と言っている。StudyにはStudyを、という意味だ。
    # 安全に挿入するために、文字列操作を行う。
    
    updated_content = content
    
    categories_map = {
        "study": "study",
        "job": "job",
        "tools": "tools",
        "fun": "fun"
    }

    for cat_key, html_cards in html_sections.items():
        target_id = categories_map.get(cat_key)
        if not target_id: continue
        
        # 検索マーカー: id="{target_id}"
        start_idx = updated_content.find(f'id="{target_id}"')
        if start_idx == -1: continue
        
        # 次のセクション開始位置またはフッター開始位置を探す（そこが限界点）
        next_section_idx = updated_content.find('<section', start_idx + 1)
        if next_section_idx == -1:
             next_section_idx = updated_content.find('<footer', start_idx + 1)
        
        # 範囲内にある最後の `</div>` (gridの閉じタグ) を探したいが、入れ子になっているので難しい。
        # 代わりに、 `<div class="apps-grid">` を探し、その直後に挿入するのではなく、中身に追加したい。
        # 単純に `class="apps-grid">` を見つけて、その直後は既存カードの先頭。
        # 既存カードの末尾に追加したい。
        
        # 一番簡単なハック: `class="apps-grid">` を `class="apps-grid"> [NEW CARDS]` に置換すると先頭に入ってしまう。
        # `</div>` `</section>` のパターンを使う。
        
        # 範囲内の文字列を抽出
        section_content = updated_content[start_idx:next_section_idx]
        
        # 最後の `</div>` の前の `</div>` ... インデントに頼る。
        # ソースを見ると `    </section>` の前は `        </div>` (apps-gridの閉じ) である可能性が高い。
        
        # リスクはあるが、`</div>\n    </section>` をターゲットにする。
        target_str = '</div>\n    </section>'
        replacement = '\n' + "\n".join(html_cards) + '\n        </div>\n    </section>'
        
        # このセクション範囲内でのみ置換を行う
        # string replaceは全体に効くので注意。
        
        # 区間置換
        new_section_content = section_content.replace(target_str, replacement, 1) # 1回だけ置換
        
        updated_content = updated_content[:start_idx] + new_section_content + updated_content[next_section_idx:]

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Dashboard updated successfully.")

if __name__ == "__main__":
    main()
