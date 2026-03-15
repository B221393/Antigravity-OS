# 🚀 ランチャー一覧 (_launchers/)

> **全ランチャースクリプトの格納場所**
> 最終更新: 2026-02-23

---

## メインランチャー

| ファイル | 説明 | 補足 |
|----------|------|------|
| `LAUNCHER_MAIN.bat` | **統合ランチャー**（メニュー形式） | 全機能アクセス可能 |

## Intelligence / 情報収集

| ファイル | 説明 | 補足 |
|----------|------|------|
| `INTELLIGENCE_PATROL.bat` | 自動情報収集パトロール | ブックシェルフモード |
| `INTELLIGENCE_CHAOS.bat` | 好奇心モードパトロール | KARAPAIA等 |
| `YouTube_CLI.bat` | YouTube分析（CLI） | ターミナルUI |
| `YouTube_Web.bat` | YouTube分析（Web） | port 8519 |
| `EGO_INTELLIGENCE_VIEWER.bat` | ダッシュボード閲覧 | HTML直接表示 |

## ダッシュボード / GUI

| ファイル | 説明 | 補足 |
|----------|------|------|
| `LAUNCH_HUB.bat` | メインハブ起動 | vectis_hub.py |
| `START_EGO.bat` | ネイティブGUI起動 | EGO_OMNI_EXPLORER.py |
| `START_OMNI.bat` | OMNI Explorer起動 | EGO_OMNI_EXPLORER.py |
| `OMNI_DASHBOARD.bat` | OMNIコマンドセンター | Streamlit port 8501 |
| `ZEN_UI.bat` | ゼンUI（最小構成） | Streamlit port 8502 |
| `DESKTOP_HUD_OLD.bat` | デスクトップHUD | レガシー |
| `VISUAL_CODER_3D.bat` | ビジュアルコーダー3D | React/npm |

## 学習・トレーニング

| ファイル | 説明 | 補足 |
|----------|------|------|
| `SPI_DOJO.bat` | SPI対策道場 | — |
| `ONISHI_DOJO.bat` | 大西配列タイピング | — |
| `INTERVIEW_HUB.bat` | 面接練習ハブ | HTML直接表示 |
| `START_PRACTICE.bat` | 練習ツール統合 | — |

## キャリア

| ファイル | 説明 | 補足 |
|----------|------|------|
| `GO_CAREER.bat` | キャリアツールメニュー | 要パス確認 |

## 外部連携

| ファイル | 説明 | 補足 |
|----------|------|------|
| `START_DRIVE_RELAY.bat` | Google Drive連携 | — |
| `START_LOCAL_BRAIN.bat` | ローカルLLM起動 | — |
| `Voice_Typer.bat` | 音声入力 | — |
| `update_schedule.bat` | スケジュール更新 | — |

## 管理系

| ファイル | 説明 | 補足 |
|----------|------|------|
| `RUST_COMMAND_CENTER.bat` | Rustプロジェクト管理 | — |
| `upload_sources_to_nlm.ps1` | NotebookLMアップロード | PowerShell |

---

## 使い方

```bat
:: 統合ランチャーを起動
_launchers\LAUNCHER_MAIN.bat

:: 個別に起動
_launchers\INTELLIGENCE_PATROL.bat
```
