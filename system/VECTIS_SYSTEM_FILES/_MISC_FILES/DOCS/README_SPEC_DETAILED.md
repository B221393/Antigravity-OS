# 📋 VECTIS OS - 詳細技術仕様書

**Document Version**: 2.1.0  
**System Version**: 2.1.0  
**Last Updated**: 2026-01-11  
**Status**: Production

---

## 目次

1. [システム概要](#1-システム概要)
2. [アーキテクチャ](#2-アーキテクチャ)
3. [コンポーネント仕様](#3-コンポーネント仕様)
4. [API仕様](#4-api仕様)
5. [データモデル](#5-データモデル)
6. [セキュリティ](#6-セキュリティ)
7. [パフォーマンス](#7-パフォーマンス)
8. [デプロイメント](#8-デプロイメント)

---

## 1. システム概要

### 1.1 目的

VECTIS OSは、個人の知識管理・生産性向上・自己成長を支援する統合デスクトップ環境である。

**主要目標**:

- AIによる知識処理の自動化
- オフライン・無料での運用可能化
- カスタマイズ可能なワークフロー
- データプライバシーの保護

### 1.2 対象ユーザー

- 知識労働者
- 研究者・学生
- コンテンツクリエイター
- 自己成長志向の個人

### 1.3 システム要件

**ハードウェア**:

- CPU: Intel Core i5 以上 (推奨: i7)
- RAM: 8GB 以上 (推奨: 16GB、Ollama使用時)
- ストレージ: 10GB 以上の空き容量
- ディスプレイ: 1920x1080 以上

**ソフトウェア**:

- OS: Windows 10/11 (64-bit)
- Python: 3.11 以上
- AutoHotkey: v2.0 以上 (大西配列使用時)
- ブラウザ: Chrome/Edge/Firefox (最新版)

---

## 2. アーキテクチャ

### 2.1 システム構成図

```
┌──────────────────────────────────────────────────────────┐
│                    Presentation Layer                     │
├─────────────┬──────────────┬────────────────┬───────────┤
│  MAGI HUD   │  Control     │  Knowledge     │  Web Apps │
│  (Tkinter)  │  Center      │  Network       │ (Streamlit)│
│             │  (HTML/JS)   │  (Canvas)      │           │
└─────────────┴──────────────┴────────────────┴───────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                  Application Layer                         │
├──────────────┬────────────────┬──────────────────────────┤
│  Unified LLM │  Keyboard      │  Obsidian Vault          │
│  Manager     │  Layout Mgr    │  Manager                 │
│              │                │                          │
└──────────────┴────────────────┴──────────────────────────┘
         │              │              │
         └──────────────┴──────────────┘
                    │
┌───────────────────▼────────────────────────────────────────┐
│                  Data Layer                                 │
├────────────────┬───────────────┬──────────────────────────┤
│  llm_config    │  Obsidian     │  Usage Stats             │
│  .json         │  Vault (MD)   │  .json                   │
│                │               │                          │
└────────────────┴───────────────┴──────────────────────────┘
         │              │              │
         └──────────────┴──────────────┘
                    │
┌───────────────────▼────────────────────────────────────────┐
│                  External Services                          │
├────────────────┬───────────────┬──────────────────────────┤
│  Gemini API    │  Groq API     │  Ollama (Local HTTP)     │
│  (Google)      │  (Groq)       │  (localhost:11434)       │
└────────────────┴───────────────┴──────────────────────────┘
```

### 2.2 レイヤー説明

#### Presentation Layer

- **役割**: ユーザーインターフェース提供
- **技術**: Tkinter, HTML/CSS/JS, Canvas API
- **責務**: ユーザー入力受付、視覚的フィードバック

#### Application Layer

- **役割**: ビジネスロジック実装
- **技術**: Python 3.11+
- **責務**: LLM呼び出し、データ変換、状態管理

#### Data Layer

- **役割**: データ永続化
- **技術**: JSON, Markdown
- **責務**: 設定保存、メモ管理、統計記録

#### External Services

- **役割**: 外部AI/サービス連携
- **技術**: REST API, HTTP
- **責務**: LLM推論、検索、外部データ取得

---

## 3. コンポーネント仕様

### 3.1 Unified LLM System

#### 3.1.1 概要

複数のLLMプロバイダーを統一インターフェースで管理するシステム。

#### 3.1.2 クラス仕様

```python
class UnifiedLLM:
    """
    統合LLMクライアント
    
    Invariants:
    - config は常に有効な設定辞書
    - default_provider は providers に存在するキー
    - 少なくとも1つのプロバイダーが有効
    
    Reasoning:
    - 単一のインターフェースで複数LLMを抽象化
    - フォールバック機能で可用性を向上
    - プロバイダー切り替えを透過的に実現
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初期化
        
        Precondition: config_path が存在する（または None）
        Postcondition: 全プロバイダーが初期化済み
        """
        
    def generate(self, prompt: str, **kwargs) -> str:
        """
        テキスト生成
        
        Precondition: prompt が非空文字列
        Postcondition: 生成テキストを返す（エラー時は例外）
        
        Args:
            prompt: 入力プロンプト
            provider: 使用プロバイダー（省略時はdefault）
            temperature: 生成温度 (0.0-1.0)
            max_tokens: 最大トークン数
            
        Returns:
            生成されたテキスト
            
        Raises:
            ProviderError: 全プロバイダーで失敗
        """
        
    def check_provider_status(self) -> Dict[str, bool]:
        """プロバイダー状態確認"""
```

#### 3.1.3 対応プロバイダー

| Provider | Type | Model | Endpoint |
|----------|------|-------|----------|
| **Gemini** | Cloud | gemini-2.0-flash | Google API |
| **Ollama** | Local | llama3.2 | localhost:11434 |
| **Phi-3** | Local | phi3 | localhost:11434 |
| **Groq** | Cloud | llama-3.1-8b-instant | Groq API |

#### 3.1.4 フォールバックロジック

```python
def _call_with_fallback(self, prompt: str) -> str:
    """
    フォールバック付き呼び出し
    
    1. デフォルトプロバイダーで試行
    2. 失敗時、fallback_provider に切り替え
    3. それも失敗時、全プロバイダーを順に試行
    4. 全て失敗時、例外発生
    
    Reasoning: 高可用性を実現
    """
    primary = self.config["default_provider"]
    fallback = self.config["providers"][primary].get("rate_limit", {}).get("fallback_provider")
    
    # Try primary
    try:
        return self._call_provider(primary, prompt)
    except RateLimitError:
        if fallback:
            return self._call_provider(fallback, prompt)
    
    # Try all
    for provider in self.config["providers"]:
        if provider != primary:
            try:
                return self._call_provider(provider, prompt)
            except:
                continue
    
    raise AllProvidersFailedError()
```

---

### 3.2 MAGI HUD

#### 3.2.1 概要

右下常駐型のステータス表示・クイック入力システム。

#### 3.2.2 UIコンポーネント

```
┌─────────────────────────────────────┐
│ ◤ MAGI SYSTEM : VECTIS BRANCH ◢ [×]│ ← Header
├─────────────────────────────────────┤
│ PROJECT : KODANSHA [LIMIT]          │ ← Timer Section
│                    -02:14:23:45     │
├─────────────────────────────────────┤
│ SYSTEM: MEMO // READY               │ ← Status
│ [入力欄__________________________]  │ ← Input
│ [MEMO] [SEARCH] [TODO] [INBOX] ...  │ ← Mode Buttons
├─────────────────────────────────────┤
│ ⌨ [ QWERTY ]                        │ ← Keyboard Toggle
│ KEY MAP:                            │
│ Q→q  W→l  E→u  R→,  T→.  ...       │ ← Key Map (3 lines)
│ A→e  S→i  D→a  F→o  G→-  ...       │
│ Z→z  X→x  C→c  V→v  B→;  ...       │
└─────────────────────────────────────┘
```

#### 3.2.3 技術仕様

**UI Framework**: Tkinter  
**Window Properties**:

```python
{
    "width": 380,
    "height": 280,
    "position": "bottom-right",
    "offset_x": 20,
    "offset_y": 60,
    "topmost": True,
    "alpha": 0.85,
    "overrideredirect": True  # ボーダーレス
}
```

**Color Scheme** (MAGI Style):

```python
{
    "BG_COLOR": "#000000",      # 漆黒
    "FG_AMBER": "#FFAA00",      # アンバー
    "FG_RED": "#FF0000",        # アラート
    "FG_GREEN": "#00FF44",      # ステータス
    "ACCENT": "#FF7700"         # アクセント
}
```

#### 3.2.4 機能仕様

**1. カウントダウンタイマー**

```python
def update_timer(self):
    """
    締切までの残り時間を1秒ごとに更新
    
    Format: -DD:HH:MM:SS
    Color: FG_RED (緊急度に応じて変更可能)
    
    Threading: tkinter.after() 使用
    """
```

**2. モード選択**

| Mode | Action | File |
|------|--------|------|
| MEMO | ファイル書き込み | `quick_memos.txt` |
| SEARCH | Google検索 | - |
| TODO | タスク追加 | `user_todo.txt` |
| INBOX | AI仕分け用 | `sorter_inbox.txt` |
| REQUEST | Antigravity送信 | `../../ANTIGRAVITY_REQUEST.txt` |

**3. キーボードトグル**

```python
def _toggle_keyboard(self, event):
    """
    QWERTY ⇔ Onishi 切り替え
    
    Actions:
    1. KeyboardLayoutManager.toggle() 呼び出し
    2. ボタン視覚更新 (色・テキスト・背景)
    3. キーマップ表示更新 (3行)
    4. ステータスメッセージ表示
    
    Note: 実際のキーリマッピングはAutoHotkeyが担当
    """
```

---

### 3.3 Keyboard Layout Manager

#### 3.3.1 概要

大西o24配列の設定管理と視覚的フィードバックを提供。

#### 3.3.2 クラス仕様

```python
class KeyboardLayoutManager:
    """
    キーボードレイアウト管理
    
    Invariants:
    - current_layout は "qwerty" または "onishi"
    - 設定は llm_config.json と同期
    
    Reasoning:
    - 設定の一元管理
    - アプリ間での状態共有
    """
    
    ONISHI_LAYOUT = {
        # Top Row
        'q': 'q', 'w': 'l', 'e': 'u', 'r': ',', 't': '.',
        'y': 'f', 'u': 'w', 'i': 'r', 'o': 'y', 'p': 'p',
        
        # Home Row
        'a': 'e', 's': 'i', 'd': 'a', 'f': 'o', 'g': '-',
        'h': 'k', 'j': 't', 'k': 'n', 'l': 's', ';': 'h',
        
        # Bottom Row
        'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': ';',
        'n': 'g', 'm': 'd', ',': 'm', '.': 'j', '/': 'b',
        
        # Special
        '-': '/',
    }
```

#### 3.3.3 AutoHotkey連携

**役割分担**:

- **KeyboardLayoutManager** (Python): 設定管理・視覚表示
- **onishi_layout_v2.ahk** (AutoHotkey): 実際のキーリマッピング

**AutoHotkeyスクリプト仕様**:

```autohotkey
; ==================================================
; Onishi o24 Layout - AutoHotkey v2
; ==================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

global IsOnishi := true

; トグル: Ctrl+Alt+S
^!s::ToggleOnishi()

; 終了: Ctrl+Alt+Q
^!q::ExitApp()

; マッピング例
#HotIf IsOnishi
q::q
w::l
e::u
; ...
#HotIf
```

---

### 3.4 Control Center

#### 3.4.1 概要

iPhone風の設定UIで全システム設定を統合管理。

#### 3.4.2 UI仕様

**デザイン言語**: iOS 17 Style

- ダークモード
- セグメントコントロール
- トグルスイッチ
- ガラスモーフィズム

**カラーパレット**:

```css
:root {
    --bg-primary: #000000;
    --bg-secondary: #1c1c1e;
    --bg-tertiary: #2c2c2e;
    --text-primary: #ffffff;
    --text-secondary: #8e8e93;
    --accent-blue: #007aff;
    --accent-green: #34c759;
}
```

#### 3.4.3 設定項目

**1. LLMプロバイダー**

- デフォルトプロバイダー選択
- Auto-Fallback トグル
- ステータス表示

**2. キーボードレイアウト**

- トグルスイッチ (QWERTY/Onishi)
- リアルタイム状態表示

**3. TOEIC優先度**

- セグメントコントロール (High/Med/Low/Off)

**4. システム情報**

- バージョン表示
- メモリノード数
- ストレージ使用量

#### 3.4.4 データ永続化

```javascript
// LocalStorage Schema
{
    "magichub_config": {
        "provider": "ollama",
        "autoFallback": true,
        "keyboardLayout": "qwerty",
        "toeicPriority": "low"
    }
}

// Sync to Python config
function saveConfig() {
    localStorage.setItem('magichub_config', JSON.stringify(config));
    // Future: POST to /api/config
}
```

---

### 3.5 Knowledge Network

#### 3.5.1 概要

Force-directed graphによる知識の3D可視化。

#### 3.5.2 物理エンジン

**実装**: Custom Physics Simulation

```javascript
class Node {
    updateForces(nodes) {
        // 1. 中心への重力
        const gravity = 0.0003;
        this.vx -= this.x * gravity;
        this.vy -= this.y * gravity;
        
        // 2. 親へのスプリング力
        if (this.parent) {
            const k = 0.006;  // バネ定数
            const restLength = 70;  // 自然長
            const force = (dist - restLength) * k;
            // Apply force...
        }
        
        // 3. ノード間反発力
        const minDist = 100;
        if (distSq < minDist * minDist) {
            const force = 6 / distSq;
            // Apply repulsion...
        }
        
        // 4. ランダムな揺らぎ
        this.vx += (Math.random() - 0.5) * 0.08;
        
        // 5. 減衰
        this.vx *= 0.93;
        
        // 位置更新
        this.x += this.vx;
    }
}
```

#### 3.5.3 3D投影

```javascript
// Simple Perspective Projection
const perspective = 900;
const scale = perspective / (perspective + z * zoom);

const screenX = (x - cameraX) * zoom * scale + width/2;
const screenY = (y - cameraY) * zoom * scale + height/2;
```

#### 3.5.4 インタラクション

| Action | Effect |
|--------|--------|
| Click Node | Focus + Zoom |
| Click Category | Expand/Collapse Children |
| ESC | Reset View |
| SPACE | Toggle Auto-Rotate |

---

### 3.6 Obsidian Vault

#### 3.6.1 ディレクトリ構造

```
obsidian_vault/
├── 2026-01-11/
│   ├── daily.md
│   ├── Meeting_Notes.md
│   └── Ideas.md
├── 2026-01-12/
│   └── daily.md
├── templates/
│   └── daily.md
├── attachments/
└── archive/
```

#### 3.6.2 API仕様

```python
class ObsidianVault:
    def create_daily_note(self, date: Optional[datetime] = None) -> Path:
        """
        デイリーノート作成
        
        Precondition: Vault initialized
        Postcondition: Daily note exists for date
        
        Returns: Path to note
        """
        
    def create_note(
        self,
        title: str,
        content: str = "",
        date: Optional[datetime] = None,
        tags: list = None
    ) -> Path:
        """
        任意のノート作成
        
        Precondition: title is non-empty
        Postcondition: Note file created
        
        Args:
            title: ノートタイトル
            content: 本文 (Markdown)
            date: 日付 (default: today)
            tags: タグリスト
            
        Returns: Path to created note
        """
```

#### 3.6.3 テンプレート

```markdown
# {{date}}

## 🎯 Today's Goals
- [ ] 

## 📝 Notes


## 💡 Ideas


## 🔗 Links


---
Created: {{timestamp}}
Tags: #daily-note
```

---

## 4. API仕様

### 4.1 Unified LLM API

#### Endpoint (Internal API)

```python
# Create Client
llm = create_llm_client()

# Generate Text
response: str = llm.generate(
    prompt="Hello, world!",
    provider="ollama",  # Optional
    temperature=0.7,    # Optional
    max_tokens=500      # Optional
)

# Check Status
status: Dict[str, bool] = llm.check_provider_status()
# {'ollama': True, 'gemini': False, 'groq': False}

# Get Usage Stats
stats: Dict = llm.get_usage_stats()
# {'total_requests': 42, 'by_provider': {...}}
```

### 4.2 Keyboard Layout API

```python
from modules.keyboard_layout import get_layout_manager

manager = get_layout_manager()

# Get Current
current: str = manager.get_current_layout()  # 'qwerty' or 'onishi'

# Toggle
new: str = manager.toggle_layout()

# Set Specific
manager.set_layout('onishi')

# Check Status
is_onishi: bool = manager.is_onishi_active()
```

### 4.3 Obsidian Vault API

```python
from modules.obsidian_vault import quick_note, today_note

# Quick Note
path = quick_note("Title", "Content", tags=["work"])

# Today's Daily
path = today_note()

# Search
vault = ObsidianVault()
results = vault.search_notes("keyword")
```

---

## 5. データモデル

### 5.1 llm_config.json Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "default_provider": {
      "type": "string",
      "enum": ["ollama", "gemini", "groq", "phi3"]
    },
    "providers": {
      "type": "object",
      "properties": {
        "ollama": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "url": {"type": "string", "format": "uri"},
            "model": {"type": "string"},
            "timeout": {"type": "number"}
          }
        },
        "gemini": {
          "type": "object",
          "properties": {
            "enabled": {"type": "boolean"},
            "api_key_env": {"type": "string"},
            "model": {"type": "string"},
            "rate_limit": {
              "type": "object",
              "properties": {
                "requests_per_minute": {"type": "number"},
                "fallback_provider": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "features": {
      "type": "object",
      "properties": {
        "keyboard_layout": {
          "type": "string",
          "enum": ["qwerty", "onishi"]
        },
        "toeic_priority": {
          "type": "string",
          "enum": ["high", "medium", "low", "disabled"]
        }
      }
    }
  }
}
```

### 5.2 Obsidian Note Format

```markdown
# {Title}

{Content}

---
Created: {ISO8601 Timestamp}
Tags: #{tag1} #{tag2}
```

---

## 6. セキュリティ

### 6.1 APIキー管理

**方針**: 環境変数による管理

```powershell
# .env file
GEMINI_API_KEY=your_api_key_here
GROQ_API_KEY=your_api_key_here
```

```python
# Loading
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

### 6.2 データプライバシー

- ✅ 全データローカル保存
- ✅ Ollama使用時は外部送信なし
- ✅ API使用時もキャッシュはローカル
- ✅ 個人情報は`obsidian_vault/`内に隔離

### 6.3 アクセス制御

- **ファイルシステム**: Windows ACL準拠
- **設定ファイル**: 読み取り専用推奨
- **APIキー**: 環境変数のみ、Git除外

---

## 7. パフォーマンス

### 7.1 ベンチマーク

**測定環境**:

- CPU: Intel Core i7-11800H
- RAM: 32GB
- OS: Windows 11 Pro

**結果**:

| Component | Metric | Value |
|-----------|--------|-------|
| MAGI HUD | 起動時間 | ~2秒 |
| MAGI HUD | メモリ使用量 | 45MB |
| UnifiedLLM (Ollama) | 初回推論速度 | 3.2秒/100トークン |
| UnifiedLLM (Gemini) | 推論速度 | 1.8秒/100トークン |
| Knowledge Network | 描画FPS | 60fps (100ノード) |
| Control Center | ページロード | <1秒 |

### 7.2 最適化

**1. LLM呼び出し**

- キャッシュ機構（将来実装予定）
- バッチ処理対応

**2. UI描画**

- Canvas最適化 (requestAnimationFrame)
- Virtual scrolling (大量ノード時)

**3. ファイルI/O**

- Bulk write
-

 Lazy loading

---

## 8. デプロイメント

### 8.1 インストール手順

```powershell
# 1. リポジトリクローン
git clone <repository_url>
cd app/VECTIS_SYSTEM_FILES

# 2. 仮想環境作成
python -m venv .venv
.venv\Scripts\activate.bat

# 3. 依存関係インストール
pip install -r requirements.txt

# 4. Ollama セットアップ (オプション)
# https://ollama.ai/
ollama pull llama3.2

# 5. AutoHotkey インストール (大西配列用)
# https://www.autohotkey.com/

# 6. 環境変数設定
# .env ファイル作成
# GEMINI_API_KEY=your_key
```

### 8.2 起動

```powershell
# クイックメニュー
QUICK_MENU.bat

# または個別起動
00_MAGI_HUD.bat
09_Control_Center.bat
10_Knowledge_Network.bat
```

---

## 9. トラブルシューティング

### 9.1 よくあるエラー

**1. Streamlit not found**

```powershell
cd VECTIS_SYSTEM_FILES
.venv\Scripts\python.exe -m pip install streamlit
```

**2. Ollama connection error**

```powershell
# サービス起動確認
ollama list

# 手動起動
ollama serve
```

**3. 大西配列が動作しない**

- AutoHotkey v2 確認
- 管理者権限で実行
- スクリプト再起動

### 9.2 ログ

**MAGI HUD**:

```powershell
# 標準出力に出力
python apps/desktop_hud/hud.py > magi_hud.log 2>&1
```

**Ollama**:

```powershell
# デフォルトログ場所
%USERPROFILE%\.ollama\logs\
```

---

## 10. 付録

### 10.1 用語集

- **Unified LLM**: 複数LLMの統一管理システム
- **MAGI HUD**: 右下常駐ステータス表示
- **Onishi o24**: 最適化された日本語キーボード配列
- **Force-directed**: 物理シミュレーションによるグラフレイアウト

### 10.2 参考資料

- [Ollama Documentation](https://ollama.ai/docs)
- [Gemini API Reference](https://ai.google.dev/docs)
- [AutoHotkey v2 Guide](https://www.autohotkey.com/docs/v2/)

---

**Document End** - VECTIS OS Detailed Specification v2.1.0
