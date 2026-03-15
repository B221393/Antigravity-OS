# VECTIS OS - 統合LLMシステム

## クイックスタート

### 状態確認

```powershell
python scripts/check_llm_status.py
```

### 基本的な使い方

```python
from modules.unified_llm import create_llm_client

# LLMクライアント作成
llm = create_llm_client()

# テキスト生成
response = llm.generate("こんにちは")
print(response)
```

## 設定

### デフォルトプロバイダー変更

`config/llm_config.json`:

```json
{
  "default_provider": "ollama"
}
```

### キーボードレイアウト切り替え

```python
from modules.keyboard_layout import toggle_keyboard_layout

toggle_keyboard_layout()  # QWERTY <-> 大西配列
```

### TOEIC優先度変更

`config/llm_config.json`:

```json
{
  "features": {
    "toeic_priority": "low"  // high, medium, low, disabled
  }
}
```

## ドキュメント

- 📖 [ローカルLLMセットアップガイド](docs/LOCAL_LLM_SETUP.md)
- 📊 [システム強化レポート](docs/SYSTEM_UPGRADE_REPORT.md)

## 機能

- ✅ 複数LLMプロバイダー対応 (Gemini, Ollama, Phi-3, Groq)
- ✅ 自動フォールバック (API制限時にローカルへ)
- ✅ 完全オフライン動作可能
- ✅ レート制限なし (ローカルモデル使用時)
- ✅ 大西配列キーボードサポート
- ✅ First-Class Reasoning パターン適用

## 現在の状態

実行中のプロバイダー:

- 🟢 **Ollama** (llama3.2) - デフォルト
- 🔴 **Gemini** - APIキー未設定
- 🔴 **Groq** - APIキー未設定

設定:

- ⌨️ キーボード: **QWERTY**
- 📚 TOEIC優先度: **LOW**
- 🔄 自動フォールバック: **有効**
