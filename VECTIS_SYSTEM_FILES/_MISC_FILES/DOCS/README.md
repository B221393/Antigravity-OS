# 📘 VECTIS OS - 統合ドキュメント

**Version 2.1.0** - Local LLM & Onishi Integration Update

---

## 🚀 クイックスタート

### 最速起動

```powershell
# クイックメニューから選択
QUICK_MENU.bat

# または直接起動
00_MAGI_HUD.bat              # 右下ステータス表示
09_Control_Center.bat         # 設定パネル
10_Knowledge_Network.bat      # 知識可視化
```

---

## 📦 新機能 (v2.1.0)

### 1. **統合LLMシステム** 🤖

**場所**: `VECTIS_SYSTEM_FILES/modules/unified_llm.py`

**機能**:

- Gemini, Ollama, Phi-3, Groq を統一管理
- API制限時に自動フォールバック
- 完全無料化可能 (Ollama使用時)
- レート制限なし

**使い方**:

```python
from modules.unified_llm import create_llm_client

llm = create_llm_client()
response = llm.generate("あなたのプロンプト")
```

**設定**: `VECTIS_SYSTEM_FILES/config/llm_config.json`

**ドキュメント**: `VECTIS_SYSTEM_FILES/docs/SYSTEM_UPGRADE_REPORT.md`

---

### 2. **大西o24配列サポート** ⌨️

**統合箇所**:

- ✅ **MAGI HUD** - 視覚的インジケーター + 3行キーマップ表示
- ✅ **Control Center** - iPhone風トグルスイッチ
- ✅ **設定ファイル** - `config/llm_config.json`

**使い方**:

```powershell
# AutoHotkey起動 (実際のキーリマッピング)
VECTIS_SYSTEM_FILES\apps\onishi\01_大西配列を開始する.bat

# MAGI HUD起動 (インジケーター表示)
00_MAGI_HUD.bat

# インジケーターをクリックしてON/OFF
```

**キー配列**:

```
Q→q  W→l  E→u  R→,  T→.  Y→f  U→w  I→r  O→y  P→p
A→e  S→i  D→a  F→o  G→-  H→k  J→t  K→n  L→s  ;→h
Z→z  X→x  C→c  V→v  B→;  N→g  M→d  ,→m  .→j  /→b
```

**ドキュメント**: `VECTIS_SYSTEM_FILES/docs/ONISHI_O24_INTEGRATION.md`

---

### 3. **Knowledge Network (3D可視化)** 📊

**場所**: `VECTIS_SYSTEM_FILES/apps/knowledge_cards/knowledge_network.html`

**機能**:

- Physics-based force-directed graph
- 3D depth simulation
- インタラクティブなノード展開
- 自動回転機能

**操作**:

- `クリック` - ノード選択・展開
- `ESC` - ビューリセット
- `SPACE` - 自動回転ON/OFF

**起動**: `10_Knowledge_Network.bat`

---

### 4. **Control Center (設定パネル)** ⚙️

**場所**: `VECTIS_SYSTEM_FILES/apps/knowledge_cards/control_center.html`

**機能**:

- iPhone風UI (iOS 17スタイル)
- 大西配列トグルスイッチ
- LLMプロバイダー設定
- TOEIC優先度調整
- ローカルストレージ連携

**起動**: `09_Control_Center.bat`

---

### 5. **Obsidian Vault (メモ管理)** 📝

**場所**: `VECTIS_SYSTEM_FILES/modules/obsidian_vault.py`

**機能**:

- 日付ベースフォルダー構造 (`2026-01-11/`)
- 自動デイリーノート生成
- テンプレート対応
- 全文検索

**使い方**:

```python
from modules.obsidian_vault import quick_note, today_note

# 今日のデイリーノート
path = today_note()

# クイックノート
quick_note("Meeting Notes", "内容...", tags=["work"])
```

**場所**: `VECTIS_SYSTEM_FILES/obsidian_vault/`

---

## 🗂️ ファイル構成

```
app/
├── 00_MAGI_HUD.bat                    # MAGI HUD起動
├── 09_Control_Center.bat              # 設定パネル
├── 10_Knowledge_Network.bat           # 知識可視化
├── QUICK_MENU.bat                     # クイックメニュー (NEW!)
├── LAUNCH_MAGI_HUD.bat                # MAGI HUD (旧)
│
├── VECTIS_SYSTEM_FILES/
│   ├── apps/
│   │   ├── desktop_hud/
│   │   │   └── hud.py                 # MAGI HUD本体
│   │   ├── knowledge_cards/
│   │   │   ├── control_center.html   # 設定パネル
│   │   │   └── knowledge_network.html# 3D可視化
│   │   └── onishi/
│   │       ├── onishi_layout_v2.ahk  # AutoHotkey
│   │       └── 01_大西配列を開始する.bat
│   │
│   ├── modules/
│   │   ├── unified_llm.py             # 統合LLM
│   │   ├── keyboard_layout.py         # 大西配列管理
│   │   └── obsidian_vault.py          # メモ管理
│   │
│   ├── config/
│   │   ├── llm_config.json            # 統合設定
│   │   └── README.md                  # 設定ガイド
│   │
│   ├── docs/
│   │   ├── SYSTEM_UPGRADE_REPORT.md   # LLMシステム
│   │   ├── ONISHI_O24_INTEGRATION.md  # 大西配列
│   │   ├── ADDITIONAL_FEATURES.md     # 追加機能
│   │   └── LOCAL_LLM_SETUP.md         # ローカルLLM
│   │
│   └── obsidian_vault/                # メモ保存先
│       └── 2026-01-11/
│           └── daily.md
```

---

## 🎯 主要システム一覧

| # | 名前 | 説明 | 起動 |
|---|------|------|------|
| 00 | **MAGI HUD** | 右下ステータス表示 | `00_MAGI_HUD.bat` |
| 01 | Main HUD | デスクトップHUD | `01_Main_HUD.bat` |
| 02 | YouTube CLI | チャンネルダイジェスト | `02_YouTube_CLI.bat` |
| 03 | YouTube Web | Web版 | `03_YouTube_Web.bat` |
| 04 | Ego Engine | 自己分析 | `04_Ego_Engine.bat` |
| 05 | TOEIC Mastery | 英語学習 | `05_TOEIC_Mastery.bat` |
| 06 | Vectis Hub | 中央ハブ | `06_Vectis_Hub.bat` |
| 07 | Wiki Lite | 知識ベース | `07_Wiki_Lite.bat` |
| 08 | Auto Watcher | バックグラウンド監視 | `08_Auto_Watcher.bat` |
| 09 | **Control Center** | 設定パネル | `09_Control_Center.bat` |
| 10 | **Knowledge Network** | 3D可視化 | `10_Knowledge_Network.bat` |
| 99 | Emergency Stop | 緊急停止 | `99_Emergency_Stop.bat` |

---

## ⚙️ 設定ファイル

### `config/llm_config.json`

```json
{
  "default_provider": "ollama",
  "providers": {
    "ollama": {
      "enabled": true,
      "url": "http://localhost:11434",
      "model": "llama3.2"
    },
    "gemini": {
      "enabled": false,
      "api_key_env": "GEMINI_API_KEY"
    }
  },
  "features": {
    "keyboard_layout": "qwerty",
    "toeic_priority": "low"
  }
}
```

---

## 🔧 セットアップ

### 1. ローカルLLM (Ollama)

```powershell
# Ollamaインストール
# https://ollama.ai/

# モデルダウンロード
ollama pull llama3.2

# 起動確認
ollama list
```

### 2. 大西配列

```powershell
# AutoHotkey v2 インストール必須
# https://www.autohotkey.com/

# 起動
VECTIS_SYSTEM_FILES\apps\onishi\01_大西配列を開始する.bat

# トグル: Ctrl+Alt+S
# 終了: Ctrl+Alt+Q
```

### 3. Python環境

```powershell
cd VECTIS_SYSTEM_FILES
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 📊 機能比較表

| 機能 | Before | After (v2.1.0) |
|------|--------|----------------|
| LLM | Gemini固定 | 4種類から選択 |
| API依存 | 必須 | オプション |
| コスト | 有料プラン推奨 | 完全無料可能 |
| レート制限 | 10req/min | 無制限 (Ollama) |
| オフライン | 不可 | 可能 |
| キーボード | QWERTY固定 | 大西o24対応 |
| TOEIC優先度 | 通常 | LOW設定済 |

---

## 📖 ドキュメント索引

### 概要

- 📄 **このファイル** - 統合ドキュメント
- 📄 `README_SPEC_SIMPLE.md` - 簡易仕様書
- 📄 `README_SPEC_DETAILED.md` - 詳細仕様書

### システム別

- 📘 `docs/SYSTEM_UPGRADE_REPORT.md` - LLMシステム強化
- 📘 `docs/ONISHI_O24_INTEGRATION.md` - 大西配列統合
- 📘 `docs/ADDITIONAL_FEATURES.md` - 追加機能まとめ
- 📘 `docs/LOCAL_LLM_SETUP.md` - ローカルLLM導入

### マニュアル

- 📗 `MAGI_HUD_MANUAL.md` - MAGI HUD操作方法
- 📗 `config/README.md` - 設定ファイルガイド

---

## 🐛 トラブルシューティング

### MAGI HUDが表示されない

```powershell
# Pythonパス確認
VECTIS_SYSTEM_FILES\.venv\Scripts\python.exe --version

# 依存関係確認
cd VECTIS_SYSTEM_FILES
.venv\Scripts\python.exe -m pip list
```

### Streamlitエラー

```powershell
cd VECTIS_SYSTEM_FILES
.venv\Scripts\python.exe -m pip install streamlit
```

### Ollama接続エラー

```powershell
# サービス起動確認
ollama list

# 手動起動
ollama serve
```

### 大西配列が動作しない

```powershell
# AutoHotkey v2 確認
# v1ではなくv2が必要

# スクリプト再起動
VECTIS_SYSTEM_FILES\apps\onishi\02_大西配列を終了して元に戻す.bat
VECTIS_SYSTEM_FILES\apps\onishi\01_大西配列を開始する.bat
```

---

## 🎯 よくある質問

**Q: どのLLMプロバイダーがおすすめ?**
A: 無料・オフライン・無制限の**Ollama (llama3.2)** がおすすめです。

**Q: 大西配列はどうやって有効化?**
A: AutoHotkeyスクリプトを起動 → MAGI HUDでインジケーターをクリック

**Q: 設定はどこで変更?**
A: `09_Control_Center.bat` で起動するiPhone風UIで変更可能

**Q: オフラインで使える?**
A: Ollama使用時は完全オフライン動作可能

---

## 🚀 次のステップ

1. **QUICK_MENU.bat** でクイックアクセス
2. **Control Center** で設定調整
3. **MAGI HUD** で日常的なステータス確認
4. **Knowledge Network** で知識可視化

---

## 📞 サポート

**設定確認**:

```powershell
VECTIS_SYSTEM_FILES\scripts\check_llm_status.py
```

**ログ確認**:

```powershell
# MAGI HUDは標準出力に出力
```

---

**VECTIS OS v2.1.0 - より強力に、より使いやすく** ✨
