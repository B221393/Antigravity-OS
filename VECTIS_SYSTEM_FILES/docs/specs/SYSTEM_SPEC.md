# EGO OS システム仕様書

**Version:** 2.0  
**Updated:** 2026-01-20  
**Author:** Antigravity + GLM-4.7-Flash Collaboration

---

## 1. 概要

EGOは、**パーソナル知識管理・自動情報収集・AI学習**を統合したデスクトップ環境です。  
Google Home / Alexa / Siri のように、チャットで指示を出すと適切なアプリが起動する**統合アシスタント**機能を備えています。

### 1.1 設計思想

- **Zen & Professional**: Apple風の洗練されたミニマルUI
- **時間帯連動**: 9:00-18:00は「Work Mode」、18:00-9:00は「Private Mode」で優先アプリが変化
- **自律稼働**: 情報収集・AI学習はバックグラウンドで常時稼働
- **統合アシスタント**: 右側チャットパネルで全アプリを音声/テキスト操作可能

---

## 2. アーキテクチャ

```text
│                           EGO OS (Browser)                           │
│  ┌──────────────┐  ┌─────────────────────────────┐  ┌─────────────────┐ │
│  │   Sidebar    │  │       Main Content          │  │   AI Assistant  │ │
│  │  (App List)  │  │     (iframe: apps)          │  │   (Chat Panel)  │ │
│  │  240px       │  │     flex: 1                 │  │   320px         │ │
│  └──────────────┘  └─────────────────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      System Bridge (Flask API)                          │
│  Port: 5000                                                             │
│  Endpoints:                                                             │
│    /api/ai      → Ollama (glm-4.7-flash) プロキシ                        │
│    /api/save    → JSONファイル保存                                       │
│    /api/launch  → Python アプリ起動                                      │
│    /static/*    → 静的ファイル配信                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Background Processes                              │
│  ┌─────────────────────┐  ┌─────────────────────┐                       │
│  │ Intelligence Patrol │  │ Auto Drive AI       │                       │
│  │ (run_cli.py)        │  │ (train_headless.py) │                       │
│  │ - YouTube監視       │  │ - 遺伝的アルゴリズム  │                       │
│  │ - News RSS収集      │  │ - ニューラルネット   │                       │
│  │ - 書籍ランキング     │  │ - driving_model.pth │                       │
│  └─────────────────────┘  └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Storage                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ knowledge_cards/outputs/cards/   → 知識カード (JSON)                ││
│  │ OBSIDIAN_WRITING/BOOKSHELF/      → 長文レポート (Markdown)          ││
│  │ youtube_channel/data/universe.json → 統合知識グラフ                 ││
│  │ youtube_channel/data/processed_log.json → 重複排除ログ              ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ファイル構成

```text
c:/Users/Yuto/Desktop/app/
│
├── EGO_OS.html              # メインダッシュボード (3カラム構成)
├── LAUNCH_EGO.bat           # System Bridge 起動スクリプト
├── RUN_INTELLIGENCE_PATROL.bat # 情報収集パトロール起動
├── RUN_AUTO_DRIVE.bat          # AI運転学習起動
│
├── EGO_SYSTEM_FILES/
│   ├── system_bridge.py        # Flask APIサーバー (Port 5000)
│   │
│   ├── apps/
│   │   ├── AI_LAB/
│   │   │   ├── text_router/
│   │   │   │   └── index.html          # Global Router (タスク振り分け)
│   │   │   ├── knowledge_cards/
│   │   │   │   ├── control_center.html  # 知識ベース閲覧
│   │   │   │   └── outputs/cards/       # 収集データ保存先
│   │   │   ├── racing_game/
│   │   │   │   └── racing_game.html     # 2DレースAI可視化
│   │   │   └── driving_3d/
│   │   │       └── driving_3d.html      # 3D運転シミュレータ
│   │   │
│   │   ├── MEDIA/
│   │   │   ├── youtube_channel/
│   │   │   │   ├── run_cli.py           # Intelligence Patrol (メインスクリプト)
│   │   │   │   ├── data/
│   │   │   │   │   ├── channels.json    # 監視YouTubeチャンネル
│   │   │   │   │   ├── universe.json    # 統合知識グラフ
│   │   │   │   │   └── processed_log.json # 処理済みID
│   │   │   │   └── app.py               # Streamlit版 (旧)
│   │   │   └── news_aggregator/
│   │   │       └── app.py               # RSS News収集
│   │   │
│   │   ├── UTILS/
│   │   │   ├── assistant/
│   │   │   │   └── assistant.html       # 右側AIチャットパネル
│   │   │   ├── scheduler/
│   │   │   │   └── index.html           # スケジューラ
│   │   │   ├── job_hunting/
│   │   │   │   └── index.html           # 就活トラッカー
│   │   │   ├── cleaner/
│   │   │   │   └── safe_scan.py         # 大容量ファイルスキャン
│   │   │   └── todo/
│   │   │       └── app.py               # Todoリスト
│   │   │
│   │   └── SYSTEM/
│   │       ├── system_monitor/app.py    # システム監視
│   │       └── process_killer/app.py    # プロセス終了
│   │
│   ├── modules/
│   │   ├── unified_llm.py              # LLM統合クライアント
│   │   ├── antigravity.py              # Antigravity Architect
│   │   └── error_relay.py              # エラーテレメトリ
│   │
│   └── OBSIDIAN_WRITING/
│       └── BOOKSHELF/                  # 長文レポート保存
│           ├── 01_YouTube_Summaries/
│           ├── 02_News_Clips/
│           ├── 03_Book_Trends/
│           └── 04_Auto_Research/
│
└── racing_ai_python/                   # 自動運転AI学習
    ├── train_headless.py               # ヘッドレス学習
    ├── train_headless_speed.py         # 高速学習モード
    ├── driving_model.pth               # 学習済みモデル
    └── settings.json                   # 物理パラメータ
```

---

## 4. コンポーネント詳細

### 4.1 EGO OS Dashboard (`EGO_OS.html`)

| 項目 | 内容 |
| ---- | ---- |
| **左サイドバー** | アプリ一覧（カテゴリ分類）、検索フィルター |
| **中央エリア** | 選択アプリの表示（iframe または起動ボタン） |
| **右側パネル** | AIアシスタント（assistant.html を iframe 埋め込み） |
| **時間帯連動** | 9-18時: Work Mode、18-9時: Private Mode |
| **テーマ** | Work=ライト、Private=ダークモード自動切替 |

### 4.2 AI Assistant (`assistant.html`)

| 項目 | 内容 |
| ---- | ---- |
| **入力** | テキスト入力（Enter送信対応） |
| **AI** | glm-4.7-flash (Ollama経由、System Bridge /api/ai) |
| **機能** | ユーザー入力を解析し、適切なアプリを提案・起動 |
| **出力** | JSON `{ reply, action, target_app, confidence }` |

**APP_REGISTRY (対応アプリ一覧):**

```javascript
const APP_REGISTRY = {
    "racing":    { path:"AI_LAB/racing_game/racing_game.html",   type:"html", name:"Racing AI" },
    "driving":   { path:"AI_LAB/driving_3d/driving_3d.html",    type:"html", name:"Driving 3D" },
    "shogi":     { path:"AI_LAB/shogi_dojo/app.py",            type:"python", name:"Shogi Dojo" },
    "youtube":   { path:"MEDIA/youtube_channel/app.py",        type:"python", name:"YouTube Monitor" },
    "news":      { path:"MEDIA/news_aggregator/app.py",        type:"python", name:"News Patrol" },
    "todo":      { path:"UTILS/todo/app.py",                   type:"python", name:"Todo List" },
    "schedule":  { path:"UTILS/scheduler/index.html",          type:"html", name:"Scheduler" },
    "job":       { path:"UTILS/job_hunting/index.html",        type:"html", name:"Job Tracker" },
    "knowledge": { path:"AI_LAB/knowledge_cards/control_center.html", type:"html", name:"Knowledge Base" },
    "router":    { path:"AI_LAB/text_router/index.html",       type:"html", name:"Global Router" }
};
```

### 4.3 System Bridge (`system_bridge.py`)

| エンドポイント | メソッド | 機能 |
| ------------- | ------- | ---- |
| `/api/ai` | POST | Ollama (glm-4.7-flash) へプロキシ |
| `/api/save` | POST | JSONファイル保存 |
| `/api/launch` | POST | Pythonアプリ起動 |
| `/*` | GET | 静的ファイル配信 |

### 4.4 Intelligence Patrol (`run_cli.py`)

**情報ソース:**

| カテゴリ | ソース |
| ------- | ------ |
| **YouTube** | Pivot, ReHacQ, NewsPicks, etc. (channels.json) |
| **News (Standard)** | GIGAZINE, TechCrunch, Publickey, Wired, NHK, arXiv AI, Nature |
| **News (Chaos)** | HONZ, ALL REVIEWS, UTokyo Research, Bijutsu Techo |
| **Books** | HONZ, Book Bang, 紀伊國屋ランキング |
| **Job (Shukatsu)** | Google News就活, Mynavi, Nikkei Career |

**処理フロー:**

1. 各ソースをスキャン
2. 既処理ID (`processed_log.json`) と照合し重複排除
3. 新規アイテムを `glm-4.7-flash` で要約
4. Universe (`universe.json`) に登録
5. Bookshelf にMarkdownレポート保存
6. 就活関連はカレンダーに自動登録

**自動パトロール間隔:** 30分ごと

### 4.5 Auto Drive AI

| ファイル | 役割 |
| ------- | ---- |
| `train_headless.py` | ヘッドレス学習（GUI無し） |
| `train_headless_speed.py` | 高速進化学習 |
| `driving_model.pth` | 保存済みニューラルネット |
| `settings.json` | 物理パラメータ（速度、加速度、回転速度） |

**ニューラルネット構造:**  
`Input(32) → 128 → 128 → 64 → 32 → Output(4)`  
（Leaky ReLU activation）

**学習アルゴリズム:** 遺伝的アルゴリズム  

- Population: 50  
- Mutation Rate: 0.1  
- Elite: 10%  

---

## 5. データフォーマット

### 5.1 Knowledge Card (JSON)

```json
{
  "title": "Client Meeting for Project X",
  "content": "Meeting with client regarding Project X tomorrow at 10am",
  "routing": {
    "cat": "Note",
    "icon": "📝"
  },
  "ai_analysis": {
    "title": "Client Meeting for Project X",
    "category": "Job",
    "summary": "Client meet, Proj. X"
  },
  "created_at": "2026-01-20T01:31:25.496Z"
}
```

### 5.2 Universe Node (JSON)

```json
{
  "id": "node_12345",
  "title": "AI Ethics Overview",
  "summary": "Comprehensive analysis of AI ethics...",
  "group": "Philosophy",
  "importance_score": 8,
  "created_at": "2026-01-20T10:00:00Z",
  "links": ["node_12340", "node_12341"]
}
```

### 5.3 Schedule Event (JSON)

```json
{
  "Date": "2026-01-25",
  "Time": "09:00",
  "Event": "[就活] Softbank ES Deadline",
  "Type": "DEADLINE",
  "Priority": 10,
  "Status": "Pending"
}
```

---

## 6. 起動手順

### 6.1 通常起動

```batch
# 1. System Bridgeを起動（必須）
LAUNCH_EGO.bat

# 2. ブラウザでアクセス
http://localhost:5000/EGO_OS.html

# 3. (任意) 情報収集パトロールを起動
RUN_INTELLIGENCE_PATROL.bat

# 4. (任意) 自動運転学習を起動
RUN_AUTO_DRIVE.bat
```

### 6.2 各バッチファイル

| ファイル | 機能 |
| ------- | ---- |
| `LAUNCH_EGO.bat` | System Bridge (Flask) 起動 |
| `RUN_INTELLIGENCE_PATROL.bat` | 情報収集パトロール（無限ループ） |
| `RUN_AUTO_DRIVE.bat` | 自動運転AI学習 |

---

## 7. 使用技術

| 領域 | 技術 |
| ---- | ---- |
| **フロントエンド** | HTML5, CSS3 (Vanilla), JavaScript (ES6+) |
| **バックエンド** | Python 3.x, Flask, Flask-CORS |
| **AI** | Ollama (glm-4.7-flash), PyTorch |
| **データ** | JSON, Markdown |
| **RSS解析** | feedparser, xml.etree |
| **YouTube** | yt-dlp, youtube_transcript_api |

---

## 8. 今後の拡張予定

| 機能 | 状態 |
| ---- | ---- |
| 音声入力 (Web Speech API) | 実装準備済み |
| ウェイクワード ("Hey EGO") | 未実装 |
| Chrome拡張機能化 | 未実装 |
| モバイル対応 | 未実装 |
| Wikipedia風知識ベースUI | 作成中 |

---

## 9. 注意事項

1. **Ollama が必要:** `ollama run glm-4.7-flash` で事前に起動
2. **RAM制限:** 4GB以下ではECOモード（1Bモデル）に自動切替
3. **CORS:** System Bridge がプロキシするため、ブラウザから直接Ollamaにアクセス不要
4. **ファイル削除:** `safe_scan.py` は大容量ファイルをレポートするのみ（自動削除はしない）

---

---
