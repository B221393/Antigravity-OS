# 📄 VECTIS OS - 簡易仕様書

**Version**: 2.1.0  
**更新日**: 2026-01-11  
**概要**: Local LLM & Onishi Integration Update

---

## 🎯 システム概要

VECTIS OSは、個人の知識管理・生産性向上を目的とした統合デスクトップ環境です。

**主な特徴**:

- 🤖 複数LLMプロバイダー統合
- ⌨️ 大西o24配列サポート
- 📊 知識の3D可視化
- 🎯 タスク・締切管理
- 📝 自動メモ管理

---

## 🏗️ アーキテク

チャ

### システム構成

```
┌─────────────────────────────────────┐
│         VECTIS OS Core              │
├─────────────────────────────────────┤
│  UI Layer                           │
│  ├─ MAGI HUD (Tkinter)             │
│  ├─ Control Center (HTML/JS)        │
│  └─ Knowledge Network (Canvas)      │
├─────────────────────────────────────┤
│  Business Logic                     │
│  ├─ Unified LLM                     │
│  ├─ Keyboard Layout Manager         │
│  └─ Obsidian Vault                  │
├─────────────────────────────────────┤
│  Data Layer                         │
│  ├─ llm_config.json                 │
│  ├─ Obsidian Vault (Markdown)       │
│  └─ Usage Stats (JSON)              │
└─────────────────────────────────────┘
```

---

## 📦 主要コンポーネント

### 1. Unified LLM System

**目的**: 複数LLMプロバイダーの統一管理

**対応プロバイダー**:

- Gemini (Google)
- Ollama (Local)
- Phi-3 (Microsoft/Local)
- Groq

**機能**:

- 自動フォールバック
- レート制限回避
- API独立化

### 2. MAGI HUD

**目的**: リアルタイムステータス表示

**機能**:

- 締切カウントダウン
- クイック入力 (MEMO/SEARCH/TODO/INBOX)
- 大西配列インジケーター
- 3行キーマップ表示

**技術**: Tkinter (Python)

### 3. Control Center

**目的**: システム設定の統合管理

**機能**:

- 大西配列トグル (iPhone風)
- LLMプロバイダー選択
- TOEIC優先度調整
- ローカルストレージ連携

**技術**: HTML/CSS/JavaScript

### 4. Knowledge Network

**目的**: 知識の有機的可視化

**機能**:

- Force-directed graph
- 3D depth simulation
- インタラクティブ展開
- 自動回転

**技術**: HTML Canvas API

### 5. Obsidian Vault

**目的**: 日付ベースメモ管理

**機能**:

- 自動デイリーノート
- テンプレート
- 全文検索
- タグサポート

**技術**: Python + Markdown

---

## 🗂️ ディレクトリ構造

```
app/
├── 00-10_*.bat          # 番号付きランチャー
├── QUICK_MENU.bat       # クイックメニュー
├── README.md            # 統合ドキュメント
│
└── VECTIS_SYSTEM_FILES/
    ├── apps/            # アプリケーション
    ├── modules/         # Pythonモジュール
    ├── config/          # 設定ファイル
    ├── docs/            # ドキュメント
    └── obsidian_vault/  # メモ保存先
```

---

## ⚙️ 設定ファイル

### llm_config.json

**場所**: `VECTIS_SYSTEM_FILES/config/llm_config.json`

**構造**:

```json
{
  "default_provider": "ollama",
  "providers": {
    "ollama": { "enabled": true, "model": "llama3.2" },
    "gemini": { "enabled": false }
  },
  "features": {
    "keyboard_layout": "qwerty",
    "toeic_priority": "low"
  }
}
```

---

## 🚀 起動方法

### クイックメニュー

```batch
QUICK_MENU.bat
```

### 直接起動

```batch
00_MAGI_HUD.bat              # MAGI HUD
09_Control_Center.bat         # 設定
10_Knowledge_Network.bat      # 可視化
```

---

## 🔧 技術スタック

| レイヤー | 技術 |
|---------|------|
| Backend | Python 3.11+ |
| Frontend | HTML/CSS/JavaScript |
| Desktop UI | Tkinter |
| LLM | Gemini API, Ollama, Groq API |
| Key Remap | AutoHotkey v2 |
| Storage | JSON, Markdown |

**主要ライブラリ**:

- `google-generativeai` - Gemini
- `groq` - Groq API
- `requests` - HTTP
- `tkinter` - GUI
- `json` - 設定管理

---

## 📊 データフロー

### LLM呼び出し

```
User Input
    ↓
UnifiedLLM.generate()
    ↓
[Provider Selection]
    ├─ Gemini → API Call
    ├─ Ollama → Local HTTP
    └─ Groq → API Call
    ↓
[Fallback on Error]
    ↓
Response
```

### 大西配列

```
User Action (MAGI HUD Click)
    ↓
KeyboardLayoutManager.toggle()
    ↓
llm_config.json Update
    ↓
Visual Update (Button + Map)

※ 実際のキーリマッピングはAutoHotkeyが別途実行
```

---

## 🎯 主要機能一覧

| 機能 | 実装 | 場所 |
|------|------|------|
| LLM統合 | ✅ | `modules/unified_llm.py` |
| 大西配列 | ✅ | `modules/keyboard_layout.py` |
| MAGI HUD | ✅ | `apps/desktop_hud/hud.py` |
| Control Center | ✅ | `apps/knowledge_cards/control_center.html` |
| Knowledge Network | ✅ | `apps/knowledge_cards/knowledge_network.html` |
| Obsidian Vault | ✅ | `modules/obsidian_vault.py` |
| クイックメニュー | ✅ | `QUICK_MENU.bat` |

---

## 📈 パフォーマンス

### LLM応答時間

| Provider | 平均応答時間 | オフライン |
|----------|------------|-----------|
| Gemini | ~2秒 | ❌ |
| Ollama (llama3.2) | ~3秒 | ✅ |
| Groq | ~1秒 | ❌ |

### メモリ使用量

- MAGI HUD: ~50MB
- Ollama: 4-8GB (モデル依存)
- Control Center: ~20MB (ブラウザ)

---

## 🔐 セキュリティ

### APIキー管理

- 環境変数経由で読み込み
- 設定ファイルに直接記載しない
- `.env`ファイル使用推奨

### ローカルデータ

- すべてローカル保存
- 外部送信なし (Ollama使用時)
- プライバシー保護

---

## 🐛 既知の制限

1. **Windows専用** - macOS/Linux未対応
2. **AutoHotkey依存** - 大西配列にはAHK v2必須
3. **Python 3.11+** - 3.10以下は非対応
4. **Ollama要件** - ローカルLLMに8GB RAM推奨

---

## 🔄 更新履歴

### v2.1.0 (2026-01-11)

- ✅ LLM統合システム実装
- ✅ 大西o24配列サポート
- ✅ Knowledge Network追加
- ✅ Control Center追加
- ✅ Obsidian Vault統合

### v2.0.0 (Previous)

- YouTube自動要約
- Job HQ RL学習
- ES Dojo

---

## 📞 サポート

### ステータス確認

```powershell
VECTIS_SYSTEM_FILES\scripts\check_llm_status.py
```

### ドキュメント

- 📘 詳細仕様書: `README_SPEC_DETAILED.md`
- 📗 統合ガイド: `README.md`

---

**VECTIS OS v2.1.0** - シンプルに、パワフルに ✨
