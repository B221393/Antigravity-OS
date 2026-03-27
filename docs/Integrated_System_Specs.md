# システム全体仕様・エンジニアリング・マニュアル (System Architecture & Engineering Manual)

**Version:** 3.0.0 (Concrete Evolution)
**Codename:** ANTIGRAVITY-CORE
**Operational Mode:** FULLY AUTONOMOUS DELEGATION (Powered by Copilot Engine)

---

## 1. システム定義 (System Definition)
本システムは、ユーザー（下村様）のキャリア形成と技術探求を自律的に支援・拡張する「自律型技術拡張コア（Core Expansion System）」である。抽象的なメタファーを排除し、以下の具体的機能によって構成される。

### 1.1 コア・コンポーネント (Core Components)
1.  **CAREER-UNIT**: 応募企業の管理、ES作成、面接対策シートの生成。
2.  **VISUAL-UNIT**: 3D物理シミュレーター、データ基盤の3Dビジュアライザーの生成。
3.  **SYNC-UNIT**: GitHubを用いたバージョン管理と「真実のソース」の維持。
4.  **OPERATOR（司令塔）**: 下村様の意思を解釈し、Copilotエンジンに具体的・非曖昧なタスクを発行するAIパートナー。

---

## 2. 厳密なファイル・アーキテクチャ (Strict File Architecture)

| パス (Path) | 定義 (Definition) | 役割 (Role) |
|:---|:---|:---|
| `/VECTIS_SYSTEM_FILES/CAREER/` | **キャリア資産層** | スケジュール、企業進捗、ES原稿、対策シート |
| `/apps/dev_loop/` | **自律開発成果層** | Copilotエンジンによって生成されたApp #01〜#NN |
| `/dashboard/` | **インターフェース層** | 進捗状況をHTML/CSSで可視化する統合HUD |
| `/python_scripts/` | **自動化エンジン層** | 同期、メール連携、データ更新等のバックエンドスクリプト |
| `Integrated_System_Specs.md` | **システム記述層** | **【本ファイル】** 全仕様と現状の真実のソース |

### 2.1 自律開発成果物リスト (Autonomous Assets)
*   `/apps/dev_loop/game_01/`: ORBITAL EXPLORER (App #1)
*   `/apps/dev_loop/game_02/`: NEON CITY GENERATOR (App #2)
*   `/apps/dev_loop/game_03/`: TERRAIN VOID (App #3)
*   `/apps/dev_loop/game_04/`: NEURAL CONNECTION VISUALIZER (App #4)
*   `/apps/dev_loop/game_05/`: PULSE DYNAMICS (App #5)
*   `/apps/dev_loop/game_06/`: FLUID VORTEX (App #6)
*   `/apps/dev_loop/game_07/`: SENSOR HUB VISUALIZER (App #7)
*   `/apps/dev_loop/game_08/`: VOXEL EXPANSION (App #8)
*   `/apps/dev_loop/game_09/`: KNOWLEDGE NEBULA (App #9)
*   `/apps/dev_loop/game_10/`: SIGNAL BRIDGE (App #10)
*   `/apps/dev_loop/game_11/`: BANDWIDTH TUNER (App #11)
*   `/apps/dev_loop/game_12/`: NEXUS SEARCH (App #12)
*   `/apps/dev_loop/game_13/`: INTELLIGENCE MAP (App #13)
*   `/apps/dev_loop/game_14/`: QUANTUM FLOCKING (App #14)
*   `/apps/dev_loop/game_15/`: FLUID TOPOLOGY (App #15)
*   `/apps/dev_loop/game_16/`: NEXUS OVERRIDE (App #16)

---

## 3. 自律開発（プログラム生成）プロトコル (Autonomous Dev Protocol)

後続のCopilotエンジンは、以下のルールに従ってプログラムを生成・拡張すること。

1.  **曖昧さの排除**: 「面白いもの」「いい感じの背景」という指示を禁止する。「Three.jsを用いたボクセル増殖アルゴリズムの実装」「材料力学に基づく梁のたわみ計算の実装」など、物理的・論理的な定義を用いる。
2.  **実用性の担保**: すべてのAppは、下村様の「技術的能力の証明（ポートフォリオ）」として機能する品質であること。
3.  **依存関係の最小化**: ローカル環境での実行を前提とし、CDN経由のライブラリ（Three.js等）を優先し、外部APIキーを必要とする機能は、token.pickle等の既存基盤を介すること。

---

## 4. 現在のタスク・キュー (Active Task Queue)

1.  **TASK_01_ES_SUBMISSION**: パナソニック、パーソルAVCのES提出（ステータス：Pending）。
2.  **TASK_02_CALENDAR_SYNC**: Googleカレンダー情報の自動リスト化（ステータス：Connecting）。
3.  **TASK_03_APP_GEN**: App #12 Nexus Search の構築。

---

## 5. 司令塔からCopilotへの共通定型命令 (Command Templates)
Copilotに投げる際は、以下の形式を遵守すること。
> 「ターゲット: `/apps/dev_loop/game_NN/index.html`。技術: [具体的な技術スタック]。機能: [具体的な振る舞い]。目的: [下村様のどのような強みを視覚化するか]。」

---

## 📡 主任アーキテクトより
下村様、曖昧さを排除し、システムとしての「仕様（スペック）」に徹した記述へアップグレードしました。
「統合思考OS」などの抽象的な呼び方は、「ANTIGRAVITY-CORE」という機能的なエンジン名へと移行し、すべてのプログラム生成をCopilotエンジンへ論理的に委ねる準備が整いました。
以後、すべての「拡張」はこの厳密な仕様書に基づいて実施されます。
