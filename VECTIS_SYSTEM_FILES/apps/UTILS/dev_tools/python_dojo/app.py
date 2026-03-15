
import streamlit as st
import os
import sys
import json
import random
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Page Config
st.set_page_config(page_title="🐍 Python道場 | 自分ステーション", page_icon="🐍", layout="wide")

# --- STYLES: VECTIS CORE ---
apply_vectis_style()
st.markdown("""
<style>
    /* Python Dojo specific styles */
    h1, h2, h3 { color: #FFD43B !important; }
    
    .code-input textarea {
        font-family: 'Share Tech Mono', 'Consolas', monospace !important;
        font-size: 16px !important;
        background-color: #1a1a2e !important;
        color: #00ff88 !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(0, 255, 100, 0.2), rgba(0, 200, 100, 0.1));
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(255, 50, 50, 0.2), rgba(200, 50, 50, 0.1));
        border: 2px solid #ff3366;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .hint-box {
        background: linear-gradient(135deg, rgba(255, 212, 59, 0.2), rgba(200, 180, 50, 0.1));
        border: 2px solid #FFD43B;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .progress-bar {
        background: rgba(50, 50, 80, 0.5);
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #FFD43B, #00ff88);
        height: 100%;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("### 🎯 学習モード")
    mode = st.radio("モードを選択", ["📚 レッスン", "🎮 チャレンジ", "📊 進捗確認"], label_visibility="collapsed")

# ==================== LESSON DATA ====================
LESSONS = [
    {
        "id": 1,
        "title": "🎉 はじめてのPython",
        "description": "print()関数で画面に文字を表示しよう！",
        "difficulty": "★☆☆☆☆",
        "steps": [
            {
                "instruction": "「Hello, World!」と画面に表示してみよう",
                "hint": "print() の中に文字列を入れます。文字列は 'シングルクォート' か \"ダブルクォート\" で囲みます。",
                "expected": "print('Hello, World!')",
                "alternatives": ['print("Hello, World!")', "print( 'Hello, World!' )", 'print( "Hello, World!" )'],
                "explanation": "print() は画面に文字を表示する関数です。これがプログラミングの第一歩！"
            },
            {
                "instruction": "今度は「Python楽しい！」と表示してみよう",
                "hint": "さっきと同じように print() を使いますが、中身を変えましょう。",
                "expected": "print('Python楽しい！')",
                "alternatives": ['print("Python楽しい！")', "print('Python楽しい!')", 'print("Python楽しい!")'],
                "explanation": "日本語もそのまま表示できます。Pythonは多言語対応です！"
            },
            {
                "instruction": "数字の 2024 を表示してみよう",
                "hint": "数字はクォートで囲まなくても大丈夫です。",
                "expected": "print(2024)",
                "alternatives": ['print( 2024 )'],
                "explanation": "数字（整数）はクォート不要。これを「整数型(int)」と呼びます。"
            }
        ]
    },
    {
        "id": 2,
        "title": "📦 変数を使おう",
        "description": "データに名前をつけて保存しよう！",
        "difficulty": "★★☆☆☆",
        "steps": [
            {
                "instruction": "変数 name に自分の名前（例: 'Yuto'）を代入しよう",
                "hint": "変数名 = '値' の形式です。",
                "expected": "name = 'Yuto'",
                "alternatives": ['name = "Yuto"', "name='Yuto'", 'name="Yuto"'],
                "explanation": "変数は値を保存する「箱」のようなものです。後で再利用できます！"
            },
            {
                "instruction": "変数 age に数字（例: 22）を代入しよう",
                "hint": "数字にはクォートは不要です。",
                "expected": "age = 22",
                "alternatives": ['age=22', "age =22", "age= 22"],
                "explanation": "数字を変数に入れると、後で計算に使えます。"
            },
            {
                "instruction": "変数 name の中身を print() で表示しよう",
                "hint": "print(変数名) と書きます。変数名にはクォートをつけません。",
                "expected": "print(name)",
                "alternatives": ['print( name )'],
                "explanation": "変数の中身を見るときは print() に変数名を渡します。"
            }
        ]
    },
    {
        "id": 3,
        "title": "🔢 計算しよう",
        "description": "Pythonで四則演算をマスターしよう！",
        "difficulty": "★★☆☆☆",
        "steps": [
            {
                "instruction": "10 + 5 の結果を print() で表示しよう",
                "hint": "print() の中で直接計算できます。",
                "expected": "print(10 + 5)",
                "alternatives": ['print(10+5)', "print( 10 + 5 )"],
                "explanation": "+ は足し算。Pythonは電卓のように使えます！"
            },
            {
                "instruction": "100 から 25 を引いた結果を表示しよう",
                "hint": "引き算は - を使います。",
                "expected": "print(100 - 25)",
                "alternatives": ['print(100-25)', "print( 100 - 25 )"],
                "explanation": "- は引き算。簡単ですね！"
            },
            {
                "instruction": "8 × 7 の結果を表示しよう",
                "hint": "掛け算は * (アスタリスク) を使います。× ではありません！",
                "expected": "print(8 * 7)",
                "alternatives": ['print(8*7)', "print( 8 * 7 )"],
                "explanation": "掛け算は * です。キーボードの Shift + 8 で入力できます。"
            },
            {
                "instruction": "50 ÷ 10 の結果を表示しよう",
                "hint": "割り算は / (スラッシュ) を使います。",
                "expected": "print(50 / 10)",
                "alternatives": ['print(50/10)', "print( 50 / 10 )"],
                "explanation": "割り算は / です。結果は小数（float型）になります。"
            }
        ]
    },
    {
        "id": 4,
        "title": "📝 リストを作ろう",
        "description": "複数のデータをまとめて管理しよう！",
        "difficulty": "★★★☆☆",
        "steps": [
            {
                "instruction": "fruits という変数に ['りんご', 'バナナ', 'みかん'] を代入しよう",
                "hint": "リストは [] で囲み、要素は , で区切ります。",
                "expected": "fruits = ['りんご', 'バナナ', 'みかん']",
                "alternatives": ['fruits = ["りんご", "バナナ", "みかん"]'],
                "explanation": "リストは複数の値をまとめて扱える便利な型です！"
            },
            {
                "instruction": "fruits の最初の要素を print() で表示しよう",
                "hint": "インデックスは 0 から始まります。fruits[0] のように書きます。",
                "expected": "print(fruits[0])",
                "alternatives": ['print( fruits[0] )'],
                "explanation": "リストのインデックスは 0 から始まります。これはプログラミングの基本！"
            },
            {
                "instruction": "fruits に 'ぶどう' を追加しよう",
                "hint": ".append() メソッドを使います。",
                "expected": "fruits.append('ぶどう')",
                "alternatives": ['fruits.append("ぶどう")'],
                "explanation": ".append() でリストの末尾に要素を追加できます。"
            }
        ]
    },
    {
        "id": 5,
        "title": "🔁 繰り返しを覚えよう",
        "description": "for文で同じ処理を何度も実行しよう！",
        "difficulty": "★★★★☆",
        "steps": [
            {
                "instruction": "for i in range(5): と書いて、5回繰り返す準備をしよう",
                "hint": "range(5) は 0, 1, 2, 3, 4 の5つの数字を生成します。",
                "expected": "for i in range(5):",
                "alternatives": ['for i in range(5) :'],
                "explanation": "for文は繰り返し処理の基本。range(5) で5回繰り返します。"
            },
            {
                "instruction": "for文の中で print(i) を書こう（先頭にスペース4つ）",
                "hint": "Pythonではインデント（字下げ）が重要！スペース4つまたはTabキーで。",
                "expected": "    print(i)",
                "alternatives": ['    print( i )'],
                "explanation": "インデントで「ブロック」を表現します。これがPythonの特徴！"
            }
        ]
    },
    {
        "id": 6,
        "title": "❓ 条件分岐をマスター",
        "description": "if文で条件によって処理を変えよう！",
        "difficulty": "★★★★☆",
        "steps": [
            {
                "instruction": "score = 85 という変数を作ろう",
                "hint": "変数に数字を代入します。",
                "expected": "score = 85",
                "alternatives": ['score=85'],
                "explanation": "まずはテストの点数を変数に入れます。"
            },
            {
                "instruction": "if score >= 80: と書いて、条件分岐の準備をしよう",
                "hint": ">= は「以上」を意味します。",
                "expected": "if score >= 80:",
                "alternatives": ['if score>=80:', 'if score >= 80 :'],
                "explanation": "if文は条件が True のときだけ中の処理を実行します。"
            },
            {
                "instruction": "if文の中で print('合格！') を書こう",
                "hint": "for文と同じように、インデントが必要です。",
                "expected": "    print('合格！')",
                "alternatives": ['    print("合格！")'],
                "explanation": "条件を満たしたときだけ「合格！」と表示されます。"
            }
        ]
    },
    {
        "id": 7,
        "title": "🎮 ぷよぷよプログラミング",
        "description": "ゲームの仕組みでPythonの基本を理解しよう！",
        "difficulty": "★★★★★",
        "steps": [
            {
                "instruction": "ぷよぷよの「盤面」をリストで作ろう（空っぽのリスト）",
                "hint": "空のリストは [] で作ります。 変数名は stage_board にしましょう。",
                "expected": "stage_board = []",
                "alternatives": ['stage_board=[]'],
                "explanation": "公式コードでは `Stage.board` と呼ばれます。Pythonではリストで表現します。これは「配列」の概念です。"
            },
            {
                "instruction": "盤面にぷよを3つ追加してみよう（appendを3回）",
                "hint": "stage_board.append(1) のように書きます。カンマで区切って3つ入れてもOKです。",
                "expected": "stage_board = [1, 2, 3]",
                "alternatives": ["stage_board = [1, 2, 1]", "stage_board=[1,2,3]", "stage_board.append(1)"],
                "explanation": "ぷよぷよが積まれていく様子は、リストに要素が追加されるのと同じです。これが `Player.createNewPuyo` の第一歩！"
            },
            {
                "instruction": "「もしリストの長さが4以上なら」というif文を書こう",
                "hint": "長さは len(リスト名) でわかります。 >= 4 を使います。",
                "expected": "if len(stage_board) >= 4:",
                "alternatives": ['if len(stage_board)>=4:'],
                "explanation": "これが `Stage.checkErase`（消去判定）の基本！「4つ繋がったら」という条件分岐です。"
            },
            {
                "instruction": "for puyo in stage_board: と書いて、全てのぷよを確認しよう",
                "hint": "リストの中身を順番に見るループです。",
                "expected": "for puyo in stage_board:",
                "alternatives": ['for puyo in stage_board :'],
                "explanation": "これが `Stage.checkFall`（落下判定）や描画ループの基本。一個ずつぷよの状態を確認します。"
            }
        ]
    }
]

# ==================== PROGRESS TRACKING ====================
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "data", "progress.json")

def load_progress():
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"completed_steps": [], "total_correct": 0, "total_attempts": 0, "streak": 0}

def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

# ==================== MAIN UI ====================
st.markdown(get_station_header(
    title="🐍 PYTHON道場",
    subtitle="一行ずつ、確実にマスター",
    channel_id="PY.01"
), unsafe_allow_html=True)

progress = load_progress()

if mode == "📚 レッスン":
    st.markdown("## 📚 レッスン一覧")
    st.markdown("好きなレッスンを選んで、一歩ずつPythonをマスターしよう！")
    
    # Lesson selection
    lesson_titles = [f"{l['title']} ({l['difficulty']})" for l in LESSONS]
    selected_lesson_idx = st.selectbox("レッスンを選択", range(len(LESSONS)), format_func=lambda i: lesson_titles[i])
    
    lesson = LESSONS[selected_lesson_idx]
    
    st.markdown(f"### {lesson['title']}")
    st.markdown(f"*{lesson['description']}*")
    st.markdown(f"難易度: {lesson['difficulty']}")
    
    # Step tracking
    step_key = f"lesson_{lesson['id']}_step"
    if step_key not in st.session_state:
        st.session_state[step_key] = 0
    
    current_step = st.session_state[step_key]
    total_steps = len(lesson['steps'])
    
    # Progress bar
    progress_pct = (current_step / total_steps) * 100
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_pct}%;"></div>
    </div>
    <p style="text-align: center; margin-top: 5px;">ステップ {current_step} / {total_steps}</p>
    """, unsafe_allow_html=True)
    
    if current_step >= total_steps:
        st.markdown("""
        <div class="success-box">
            <h2>🎉 レッスン完了！</h2>
            <p>素晴らしい！このレッスンをすべてクリアしました！</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 もう一度最初から"):
            st.session_state[step_key] = 0
            st.rerun()
    else:
        step = lesson['steps'][current_step]
        
        st.markdown("---")
        st.markdown(f"### ステップ {current_step + 1}: {step['instruction']}")
        
        # Code input
        user_code = st.text_input(
            "コードを入力してください:",
            key=f"code_input_{lesson['id']}_{current_step}",
            placeholder="ここにPythonコードを書いてね..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            check_button = st.button("✅ チェック", use_container_width=True)
        
        with col2:
            hint_button = st.button("💡 ヒント", use_container_width=True)
        
        with col3:
            skip_button = st.button("⏭️ スキップ", use_container_width=True)
        
        if hint_button:
            st.markdown(f"""
            <div class="hint-box">
                <strong>💡 ヒント:</strong> {step['hint']}
            </div>
            """, unsafe_allow_html=True)
        
        if check_button and user_code:
            # Normalize: remove extra spaces, compare
            normalized_input = user_code.strip()
            normalized_expected = step['expected'].strip()
            alternatives = [alt.strip() for alt in step.get('alternatives', [])]
            
            is_correct = (normalized_input == normalized_expected) or (normalized_input in alternatives)
            
            if is_correct:
                st.markdown(f"""
                <div class="success-box">
                    <h3>✅ 正解！</h3>
                    <p><strong>解説:</strong> {step['explanation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Update progress
                step_id = f"{lesson['id']}_{current_step}"
                if step_id not in progress['completed_steps']:
                    progress['completed_steps'].append(step_id)
                    progress['total_correct'] += 1
                progress['total_attempts'] += 1
                progress['streak'] += 1
                save_progress(progress)
                
                st.balloons()
                
                if st.button("➡️ 次のステップへ"):
                    st.session_state[step_key] += 1
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ おしい！もう一度やってみよう</h3>
                    <p>入力したコード: <code>{normalized_input}</code></p>
                    <p>ヒントを見てみよう！</p>
                </div>
                """, unsafe_allow_html=True)
                
                progress['total_attempts'] += 1
                progress['streak'] = 0
                save_progress(progress)
        
        if skip_button:
            st.session_state[step_key] += 1
            st.rerun()
        
        # Show expected answer (collapsed)
        with st.expander("🔓 答えを見る（どうしてもわからないとき）"):
            st.code(step['expected'], language='python')
            st.markdown(f"**解説:** {step['explanation']}")

elif mode == "🎮 チャレンジ":
    st.markdown("## 🎮 ランダムチャレンジ")
    st.markdown("ランダムな問題に挑戦して、スキルを試そう！")
    
    # Random challenge
    if 'challenge_step' not in st.session_state:
        random_lesson = random.choice(LESSONS)
        random_step = random.choice(random_lesson['steps'])
        st.session_state['challenge_step'] = (random_lesson, random_step)
    
    lesson, step = st.session_state['challenge_step']
    
    st.markdown(f"### 🎯 {step['instruction']}")
    st.markdown(f"*（{lesson['title']} より）*")
    
    user_code = st.text_input("コードを入力:", key="challenge_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ チェック", key="challenge_check", use_container_width=True):
            normalized = user_code.strip()
            expected = step['expected'].strip()
            alts = [a.strip() for a in step.get('alternatives', [])]
            
            if normalized == expected or normalized in alts:
                st.markdown("""
                <div class="success-box">
                    <h3>🎉 正解！すごい！</h3>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                
                progress['total_correct'] += 1
                progress['total_attempts'] += 1
                progress['streak'] += 1
                save_progress(progress)
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h3>❌ 残念...</h3>
                    <p>正解: <code>{expected}</code></p>
                </div>
                """, unsafe_allow_html=True)
                
                progress['total_attempts'] += 1
                progress['streak'] = 0
                save_progress(progress)
    
    with col2:
        if st.button("🔄 次の問題へ", key="next_challenge", use_container_width=True):
            random_lesson = random.choice(LESSONS)
            random_step = random.choice(random_lesson['steps'])
            st.session_state['challenge_step'] = (random_lesson, random_step)
            st.rerun()

elif mode == "📊 進捗確認":
    st.markdown("## 📊 あなたの学習進捗")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ 正解数", progress['total_correct'])
    
    with col2:
        accuracy = (progress['total_correct'] / progress['total_attempts'] * 100) if progress['total_attempts'] > 0 else 0
        st.metric("🎯 正答率", f"{accuracy:.1f}%")
    
    with col3:
        st.metric("🔥 連続正解", progress['streak'])
    
    st.markdown("---")
    
    # Completed lessons overview
    total_possible = sum(len(l['steps']) for l in LESSONS)
    completed = len(progress['completed_steps'])
    
    st.markdown(f"### 📈 全体進捗: {completed} / {total_possible} ステップ完了")
    
    overall_pct = (completed / total_possible * 100) if total_possible > 0 else 0
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {overall_pct}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🏆 レッスン別進捗")
    
    for lesson in LESSONS:
        lesson_steps = [s for s in progress['completed_steps'] if s.startswith(f"{lesson['id']}_")]
        lesson_pct = len(lesson_steps) / len(lesson['steps']) * 100
        status = "✅ 完了" if len(lesson_steps) == len(lesson['steps']) else f"{len(lesson_steps)}/{len(lesson['steps'])}"
        
        st.markdown(f"**{lesson['title']}** - {status}")
        st.progress(lesson_pct / 100)
    
    if st.button("🗑️ 進捗をリセット"):
        save_progress({"completed_steps": [], "total_correct": 0, "total_attempts": 0, "streak": 0})
        st.rerun()

st.markdown("---")
render_station_footer()
