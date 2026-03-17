# 統合思考OS：現在のシステム全仕様 (Full Specifications)
**更新日:** 2026-03-17  
**システム状態:** ACTIVE / FULL-SYNC

## 1. 3D構造解析エンジン (QUAKE-CHECK 3D PRO)
物理的なリアリティと高精度なビジュアルを両立した、地盤および建物の地震挙動シミュレーター。

*   **レンダリング:** 
    *   Three.js (r128) UMDビルド採用。
    *   HiDPI (高精細) 解像度対応、PBR (物理ベース) マテリアルによる質感再現。
    *   4K解像度のシャドウマップによる精緻な影の描写。
*   **物理ロジック:**
    *   **慣性しなり (Sway):** 上層階ほど大きく揺れる「位相差」と「慣性」を各ノードに実装。
    *   **シーン・モード:** 2階建て住宅、大規模工場（大スパン）、免震ビル（オフィス）の3種を搭載。
    *   **構造解析視覚化:** 震度1〜7のレンジに応じた固有周期と減衰計算。
*   **環境:** 青空と芝生の屋外環境、OrbitControlsによる自由なカメラワーク。

## 2. 統合ダッシュボード (INTELLIGENCE HUD)
デスクトップ背景としての利用を想定した、情報集約UI。

*   **構成:**
    *   **Schedule Widget:** `SCHEDULE.md` から直近のデッドライン（パーソルAVC等）を自動反映。
    *   **Mail Widget:** 最新のGmail通知と日付関係を視覚化。
    *   **Strategy Widget:** 就活戦略のコア・マインド（Input/Output/勇気）をスローガンとして表示。
*   **デザイン:** ガラスモーフィズムを採用したプレミアムな背景、AI生成(cybernetic_dashboard_bg)による高画質壁紙。

## 3. GitHub 同期システム (SYNC ENGINE)
GitHubの `main` ブランチを「真実のソース」として常に同一の状態に保つ機構。

*   **リポジトリ:** `b221393/my-syukatu-app`
*   **ブランチ管理:** 常時 `main` ブランチへ自動プッシュ。
*   **同期タイミング:** 
    *   ファイルの変更完了時。
    *   `git_sync_mcp.py` によるファイルウォッチ監視（自動Commit/Push）。
*   **整合性確保:** `git pull --rebase` および必要に応じた `fetch & reset` により、常にGitHub側の最新漢字（状態）をローカルに強制同期。

## 4. MCP & オート・パイロット (SELF-EVOLVING SYSTEM)
ユーザーが不在または休息中でも、システム自ら進捗を生み出すための機能。

*   **接続サーバー:**
    *   **Rube MCP:** Slack操作（メッセージ送信、チャンネル管理）。
    *   **Pencil MCP:** キャンバス・思考の視覚化。
    *   **Git-Sync:** リポジトリの自動同期。
*   **自律実行ワークフロー (`/auto-run`):**
    *   `// turbo-all` アノテーションにより、事前の承認なしでコマンドを実行し、タスク（ES修正、シミュレーター改良）を完結させる。
    *   実装完了後のGitHubプッシュ、およびSlackへの進捗報告を完全自動化。

## 5. 関連ファイル構成
*   `/quake_sim_3d/`: 3Dシミュレーター本体 (index.html, script.js, style.css)
*   `/dashboard/`: 統合HUD UI (index.html, style.css, background.png)
*   `/VECTIS_SYSTEM_FILES/CAREER/`: スケジュール、戦略ログ、ES草案
*   `/_agent/workflows/auto-run.md`: オートパイロット手順書
*   `/apps/dev_loop/game_01/`: ORBITAL EXPLORER (App #1)
*   `/apps/dev_loop/game_02/`: NEON CITY GENERATOR (App #2)
*   `/apps/dev_loop/game_03/`: TERRAIN VOID (App #3)
*   `/apps/dev_loop/game_04/`: NEURAL CONNECTION VISUALIZER (App #4)
*   `/apps/dev_loop/game_05/`: PULSE DYNAMICS (App #5)
*   `/apps/dev_loop/game_06/`: FLUID VORTEX (App #6)
*   `/apps/dev_loop/game_07/`: SENSOR HUB VISUALIZER (App #7)

---
**システムメッセージ:**
本OSは現在、下村さんの「外部脳」として、データの蓄積と自律的な技術開発を継続可能な状態にあります。体調の回復を優先し、残りのタスクは `/auto-run` ワークフローに委ねることが可能です。
