# 🤖 Virtual Agentic TDD Workflow

I adopt a multi-agent TDD workflow to ensure high-quality code generation. When I request a complex feature or use the trigger phrase `/tdd`, act according to the following 4-step process.

### Protocol

Do not jump straight to coding. Simulate the following "Virtual Agents" sequentially. Stop and ask for my confirmation after Phase 2 (Architecture) if the task is complex.

### Phase 1: 🕵️ Issue Analyzer (Role: Product Manager)

* **Goal:** Clarify requirements and identify edge cases.
* **Action:** Analyze the user's request.
* **Output format:**
  * **Summary:** What is the core problem?
  * **Key Requirements:** Bullet points of functionalities.
  * **Constraints:** Performance needs (e.g., Shogi engine speed), libraries, etc.

### Phase 2: 📐 Test Architect (Role: Senior Engineer / Opus-level thinking)

* **Goal:** Design the test strategy *before* implementation.
* **Action:** Create a test plan based on Phase 1.
* **Output format:**
  * **Test Cases:** List of scenarios (Normal, Error, Edge cases).
  * **Mocking Strategy:** What external dependencies need mocking?
  * **File Structure:** Where should the test files go?

### Phase 3: 🧪 TDD Implementer (Role: Lead Developer / Sonnet-level coding)

* **Goal:** Implement tests and functional code.
* **Action:**
    1. **Red:** Write the failing test code first.
    2. **Green:** Write the minimum functional code to pass the test.
    3. **Refactor:** Optimize readability and performance (especially for Python/Fortran parts).
* **Output:** Provide the complete, runnable code blocks for both tests and implementation.

### Phase 4: 📝 Reviewer (Role: QA / Maintainer)

* **Goal:** Final quality check.
* **Action:** Review the generated code from Phase 3.
* **Checklist:**
  * Does it meet all requirements from Phase 1?
  * Are variable names descriptive?
  * Is there any redundant code?
  * (If applicable) Is the computational complexity optimized?

---

## 🚀 Road Maintenance & Verification (System Operation)

To ensure the "Integrated Roads" (Vectis Ecosystem) are functioning correctly, follow this daily protocol.

### 1. Launch & Cleanup

* **Start All:** Run `EGO_START_ALL.bat`. This handles port allocation (8501-8505).

* **Stop All:** Run `EGO_STOP_ALL.bat`. This kills all background Streamlit processes to clean up "window pollution".

### 2. Verification Checklist (Confirm after every change)

* [ ] **Port 8501 (Job Hunter/Onishi):** Does the 3D Map and Typing app load?

* [ ] **Port 8502 (TOEIC):** Does the Part 1 image appear and sequential mode work?
* [ ] **Port 8504 (Monitor):** Are the API costs and Voice logs updating?
* [ ] **Hub Navigation:** Can you switch between apps using the top-left menu fluently?
* [ ] **Activity Log:** Does saving a score in TOEIC actually append to `activity_log.md`?

> [!IMPORTANT]
> If a "Site cannot be reached" error occurs, run `EGO_STOP_ALL.bat` and then try `EGO_START_ALL.bat` again to reset the ports.

---

## 📺 自分ステーション (Dashboard Design)

> **ステータス: 🔄 ただいま更新中！**
>
> 2025.01.07 - 佐久間宣行さんのサイト（nob-sakuma.com）を参考にしたレトロTV放送局テーマにリニューアル中。

### デザインコンセプト

* **テーマ**: レトロTV放送局 × ネオンサイン

* **カラー**: ネオンライム (#CCFF00) / エレクトリックブルー (#00AAFF) / ホットピンク (#FF00AA)
* **エフェクト**: 走査線、グリッチ、ON AIRバッジ、フリッカーアニメーション
* **フォント**: Zen Kaku Gothic New (日本語) / Share Tech Mono (英語)

### アプリ一覧 (4カテゴリ)

#### 📚 学習チャンネル (CH.01-04)

| CH | 名前 | 英語名 | Port | 説明 |
|----|------|--------|------|------|
| 01 | 英語道場 | TOEIC MASTERY | 8502 | TOEIC 990点を目指すAI学習 |
| 02 | 大西道場 | ONISHI TYPING | 8501 | 大西配列タイピング練習 |
| 03 | 教養チャンネル | HISTORY MASTER | 8505 | 日本史・一般常識 |
| 04 | 雑学王 | TRIVIA | 8516 | 雑学・豆知識 |

#### 💼 就活チャンネル (JOB.01-06)

| JOB | 名前 | 英語名 | Port | 説明 |
|-----|------|--------|------|------|
| 01 | 就活ナビ | JOB HUNTING | 8501 | 業界研究・企業分析・3D知識マップ |
| 02 | 就活司令部 | JOB HQ | 8517 | 進捗管理・面接対策 |
| 03 | ES工房 | ES MASTER | 8506 | ES添削・敬語チェック |
| 04 | 早耳ニュース | SCOUT | 8509 | 早期選考・インターン情報収集 |
| 05 | 電話メモ | PHONE APPLY | 8518 | 電話応募メモ・敬語テンプレ |
| 06 | 予定管理 | SCHEDULER | 8519 | 面接・ES締切管理 |

#### 🔧 ツールチャンネル (TOOL.01-08)

| TOOL | 名前 | 英語名 | Port | 説明 |
|------|------|--------|------|------|
| 01 | 今日のひとくち | NEURAL DIGEST | 8503 | Gemini会話→知識カード変換 |
| 02 | 動画かみくだき | YOUTUBE STREAM | 8511 | YouTube自動要約 |
| 03 | 思い出マップ | MEMORY 3D | 8512 | 日記・メモの3D可視化 |
| 04 | カード工房 | CREATOR | 8507 | 知識カード作成・編集 |
| 05 | システム監視 | MONITOR | 8504 | APIコスト・ログ監視 |
| 06 | 利用分析 | STATS | 8510 | 学習統計・成長グラフ |
| 07 | スマホ遠隔 | MOBILE | 8514 | Mobile MCP連携 |
| 08 | 操作ガイド | HELP | 8508 | 使い方・FAQ |

#### 🎮 お楽しみチャンネル (FUN.01-03)

| FUN | 名前 | 英語名 | Port | 説明 |
|-----|------|--------|------|------|
| 01 | アニメ物理計算 | ANIME PHYSICS | 8515 | アニメの物理現象を計算 |
| 02 | つながりゲーム | LINK GAME | 8513 | 知識連結パズル |
| 03 | Discord遠隔 | DISCORD BOT | 8520 | Discord経由PC操作 |

### ダッシュボードファイル

* **本番**: `apps/dashboard/index.html`

* **バックアップ**: `apps/dashboard/index_v2.html`

---

## 🎨 統一デザインシステム (アプリ内部)

### 使用方法 (Streamlitアプリ)

各アプリで以下のモジュールをインポートして使用：

```python
from modules.style import apply_vectis_style, get_station_header
from modules.nav import render_global_road, render_station_footer

# ページ設定
st.set_page_config(page_title="🎯 英語道場 | 自分ステーション", page_icon="🎯")
apply_vectis_style()

# サイドバー
with st.sidebar:
    render_global_road()

# ヘッダー
st.markdown(get_station_header(
    title="🎯 英語道場",
    subtitle="TOEIC 990点を目指す",
    channel_id="CH.01"
), unsafe_allow_html=True)

# ... メインコンテンツ ...

# フッター
render_station_footer()
```

### カラーテーマ

各アプリは独自のアクセントカラーを持てる：

| アプリ種別 | アクセントカラー | CSS変数 |
|-----------|---------------|---------|
| デフォルト | ネオンライム | `--neon-lime: #CCFF00` |
| 学習系 | ライムグリーン | `--neon-lime` |
| 就活系 | エレクトリックブルー | `--electric-blue: #00AAFF` |
| ツール系 | ホットピンク | `--hot-pink: #FF00AA` |
| お楽しみ | サンセットオレンジ | `--sunset-orange: #FF9900` |

### 統一コンポーネント

* `.station-card` - カード型コンテナ
* `.station-badge` / `.station-badge-blue/pink/orange` - ラベルバッジ
* `.status-online` - ステータスインジケーター
* `get_station_header()` - 統一ヘッダー生成
* `render_station_footer()` - 統一フッター

### 🚀 Quick CLI Tools (Terminal Quick Actions)

Use these commands in the terminal (PowerShell) for instant intelligence operations.

* **`.\s <query>`** : **Deep Search**. Uses Gemini to perform a deep-dive analysis of any topic.
  * Example: `.\s "Quantum Computing vs AI"`
  * Results are automatically saved to `s_history.json` for the 3D Knowledge Map.

* **`.\y <url>`** : **YouTube Summary**. Extracts transcript and generates a structured summary of a YouTube video.
  * Example: `.\y https://www.youtube.com/watch?v=xxxxx`
  * Requires `youtube-transcript-api`.
  * Results are saved to `s_history.json`.

---

## 📝 Additional Orders Protocol

To prevent interruptions during task execution, the user may write additional orders to a specific file.

* **File Path**: `EGO_SYSTEM_FILES\ADDITIONAL_ORDERS.md`
* **Agent Responsibility**:
    1. After completing the current task, **CHECK** this file content.
    2. If there are new orders, acknowledge them and proceed accordingly.
    3. Do NOT stop the current execution flow to check this file until the current task is done, unless explicitly instructed.

---

## 📚 Intelligence Bookshelf Protocol (Knowledge Management)

All gathered intelligence, research, and automated summaries must be consolidated into the `EGO_SYSTEM_FILES\OBSIDIAN_WRITING\BOOKSHELF` directory. This acts as the centralized knowledge repository ("The Bookshelf").

### Directory Structure (Standard)

* **`01_YouTube_Summaries/`**: Stores summaries and key insights from YouTube videos.
  * Naming: `[YYYY-MM-DD] Video Title (Channel).md`
* **`02_News_Clips/`**: Summaries of RSS news and articles.
  * Naming: `[YYYY-MM-DD] Article Title (Source).md`
* **`03_X_Threads/`**: Summarized X (Twitter) threads and trend analysis.
  * Naming: `[YYYY-MM-DD] Topic or Account.md`
* **`04_Auto_Research/`**: Deep dive reports generated by Auto Researcher / Deep Search.
  * Naming: `[YYYY-MM-DD] Topic Name.md`
* **`05_Manual_Notes/`**: User's manual copies, excerpts, and raw notes.

### Rules

1. **Format**: All files must be in Markdown (`.md`).
2. **Metadata**: All files should include a header with Source URL, Date, and Tags (e.g., `#job-hunting`).
3. **Consolidation**: Apps should default to saving "Readable Content" here, rather than hidden JSON files, whenever possible.
