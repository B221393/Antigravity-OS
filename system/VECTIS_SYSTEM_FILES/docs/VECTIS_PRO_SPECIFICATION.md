# VECTIS Professional Workstation - System Specification

**Version**: 4.4.0 (Auto-Glossary Build)  
**Date**: 2026-01-21  
**Architect**: VECTIS Intelligence System  
**Framework**: Python (Tkinter / Standard Libs)

---

## 1. 概要 (Overview)

**VECTIS Professional Workstation** は、情報収集・知識形成・体系化をワンストップで行うための**自律型インテリジェンス・クライアント**です。
Webブラウザ技術を排除し、OSネイティブなGUIを採用することで、「道具としての応答速度」と「思考を邪魔しない高密度な情報表示」を実現しています。

本バージョン(v4.3.0)では、ユーザーの操作（タッチ辞書）とバックグラウンドのAI処理（収集エンジン）が、**「収集キュー」**を介して有機的に連携する**「循環型ナレッジ生成システム」**を実装しました。

---

## 2. コア・アーキテクチャ (Core Architecture)

システムは以下の3つのモジュールが非同期に連携して動作します。

### 🔄 The Knowledge Loop (知識の循環)

1. **Frontend (GUI)**: ユーザーが記事を閲覧し、未知の単語をキューに投入する。
2. **Middleware (Queue)**: JSONファイルがリクエストを一時保持する。
3. **Backend (Engine)**: AIがキューを処理し、深い知識（記事）を生成してDBに書き戻す。

```mermaid
[User/GUI] --(Touch & Add)--> [Discovery Queue] --(Auto Poll)--> [Collector Engine]
                                                                        |
[Knowledge DB] <--(Write New Article)-----------------------------------+
      |
      +----(Sync/Read)----> [User/GUI]
```

---

## 3. 機能詳細 (Functional Specifications)

### 3.1 収集モード・コントローラ (Collection Mode Controller)

GUI上のプルダウン操作により、バックエンドAIの収集戦略を動的に切り替えます。設定は `config/collection_modes.json` に即時保存され、次回エンジンの起動時に反映されます。

| モードID | 名称 | 戦略プロンプト特性 | 主なソース |
| :--- | :--- | :--- | :--- |
| **General** | 汎用 | 幅広い視座、一般教養、時事ニュース | Web全般 |
| **Shukatsu** | 就活特化 | 2027卒向け、インターン、キャリア形成、企業分析 | 就活媒体、企業のIR |
| **Tech** | 技術トレンド | LLM、アーキテクチャ、特定言語(Rust/Python) | Tech Blog, GitHub, arXiv |
| **Philosophy** | 哲学・教養 | 古典、概念の定義、歴史的背景 | 論文、専門書データベース |

### 3.2 ライブ・タッチ辞書 (Live Touch Dictionary)

記事閲覧中に「情報収集」を中断させないためのインライン機能です。

* **トリガー**: テキスト選択 + ダブルクリック
* **動作**:
    1. Wikipedia API (または軽量LLM) にバックグラウンドで問い合わせ。
    2. 作業を阻害しないポップアップウィンドウで概要を表示。
    3. **[収集キューに追加]** ボタンにより、その単語を「次回の深掘り生成対象」として予約。

### 3.3 バックグラウンド収集連携 (Incidental Collection)

ユーザーが閲覧作業を行っている・いないに関わらず、システムは以下のロジックで「ついでに」情報を集め続けます。

* **Discovery Engine**: 30分ごとに `universe.json` (ニュース) をスキャンし、現在のモード（例：就活）に合致するキーワードを勝手に抽出してキューに入れる。
* **Deep Collector**: キューに溜まったキーワード（ユーザー入稿 + AI自動抽出）を順次処理し、1万文字レベルの記事を生成する。

---

## 4. データ構造 (Data Schema)

### 4.1 Discovery Queue (`discovery_queue.json`)

ユーザーとAIの「リクエスト」が合流する場所です。

```json
{
  "queue": [
    {
      "keyword": "RAGアーキテクチャ",
      "priority": "high",
      "status": "pending",
      "mode": "tech",
      "added_source": "user_touch_dictionary",
      "timestamp": "2026-01-21T17:30:00"
    },
    {
      "keyword": "2027卒インターン早期選考",
      "priority": "normal",
      "status": "pending",
      "mode": "shukatsu",
      "added_source": "auto_discovery_engine",
      "timestamp": "2026-01-21T17:35:00"
    }
  ]
}
```

---

## 5. UI/UX デザイン規定 (Design Rules)

* **No HTML**: Web技術への依存を排除。Tkinterによるネイティブ描画を厳守。
* **Information Density**: 余白は情報の敵。1px単位でグリッドを詰め、一覧性を最大化する。
* **Feedback**: 裏で動く処理（同期、API通信）は必ずステータスバーまたはプログレスバーで可視化する。ユーザーに「止まっている」と思わせてはならない。

---

## 6. 今後のロードマップ

1. **PDF/E-Book連携**: ローカルのPDF資料を読み込み、ナレッジベースに統合する機能。
2. **音声対話モード**: プロフェッショナルUIのまま、音声でAI Commanderに指示を出す機能。

---

*This specification is managed by VECTIS System Architect (Antigravity).*
