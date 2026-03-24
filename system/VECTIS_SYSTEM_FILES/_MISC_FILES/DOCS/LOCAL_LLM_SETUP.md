# VECTIS OS - ローカルLLM導入ガイド

## 📋 概要

VECTIS OSをAPIキー不要・無料で動作させるための設定ガイドです。

### 実装済み機能

- ✅ **統合LLMプロバイダー** - Gemini/Ollama/Phi-3/Groq対応
- ✅ **自動フォールバック** - API制限時にローカルへ自動切り替え
- ✅ **大西配列サポート** - キーボードレイアウト切替
- ✅ **設定ファイル管理** - `config/llm_config.json`

---

## 🚀 セットアップ手順

### オプション1: Ollama (推奨)

**最も簡単で高速なオプション**

1. **Ollamaインストール**

   ```powershell
   # https://ollama.com/download からインストーラーをダウンロード
   # または
   winget install Ollama.Ollama
   ```

2. **モデルダウンロード**

   ```powershell
   # Llama 3.2 (推奨 - 軽量で高性能)
   ollama pull llama3.2
   
   # または Phi-3 (Microsoft製 - より軽量)
   ollama pull phi3
   
   # または Gemma 2 (Google製)
   ollama pull gemma2
   ```

3. **Ollama起動**

   ```powershell
   ollama serve
   ```

   ✅ Ollamaは自動でバックグラウンド起動します

4. **設定変更**
   `config/llm_config.json` を編集:

   ```json
   {
     "default_provider": "ollama"
   }
   ```

### オプション2: Microsoft Phi-3 via Ollama

**軽量で高品質なモデル**

1. Ollamaインストール (上記参照)

2. Phi-3ダウンロード

   ```powershell
   ollama pull phi3
   ```

3. 設定変更
   `config/llm_config.json`:

   ```json
   {
     "default_provider": "phi3",
     "providers": {
       "phi3": {
         "enabled": true,
         "url": "http://localhost:11434/api/generate",
         "model": "phi3",
         "timeout": 30
       }
     }
   }
   ```

### オプション3: ハイブリッド構成 (推奨)

**Gemini APIとローカルを併用**

- 通常時: Gemini API使用 (無料枠)
- レート制限時: 自動的にOllamaへフォールバック

設定 (`config/llm_config.json`):

```json
{
  "default_provider": "gemini",
  "providers": {
    "gemini": {
      "enabled": true,
      "rate_limit": {
        "fallback_provider": "ollama"
      }
    },
    "ollama": {
      "enabled": true,
      "model": "llama3.2"
    }
  },
  "features": {
    "auto_fallback": true
  }
}
```

---

## 🧪 動作テスト

```powershell
# 統合LLMテスト
python modules/unified_llm.py

# プロバイダー状態確認
python scripts/check_llm_status.py
```

---

## ⌨️ 大西配列切り替え

### 有効化

```python
from modules.keyboard_layout import toggle_keyboard_layout

# 切り替え
toggle_keyboard_layout()  # QWERTY ⇔ 大西配列
```

### 設定ファイルで変更

`config/llm_config.json`:

```json
{
  "features": {
    "keyboard_layout": "onishi"  // または "qwerty"
  }
}
```

---

## 📊 TOEIC機能優先度設定

TOEIC関連機能の優先度を下げる場合:

`config/llm_config.json`:

```json
{
  "features": {
    "toeic_priority": "low"  // "high", "medium", "low", "disabled"
  }
}
```

効果:

- `low`: スタートメニュー表示順位を下げる
- `disabled`: 完全に非表示

---

## 🔧 トラブルシューティング

### Ollamaに接続できない

**症状**: `Ollama not running at http://localhost:11434`

**解決策**:

```powershell
# Ollama起動確認
ollama list

# サービス再起動
Stop-Service Ollama
Start-Service Ollama

# または手動起動
ollama serve
```

### モデルが遅い

**解決策**:

- より軽量なモデルに変更: `phi3` または `llama3.2:1b`
- GPU利用確認: NVIDIAドライバー最新版インストール

```powershell
# 軽量モデル
ollama pull llama3.2:1b
```

### メモリ不足

**解決策**:

```json
// config/llm_config.json
{
  "providers": {
    "ollama": {
      "model": "phi3:mini"  // 最小モデル
    }
  }
}
```

---

## 📈 推奨構成

### 🖥️ デスクトップPC (RAM 16GB+)

```json
{
  "default_provider": "ollama",
  "providers": {
    "ollama": {
      "model": "llama3.2"  // または "gemma2"
    }
  }
}
```

### 💻 ノートPC (RAM 8GB)

```json
{
  "default_provider": "gemini",
  "providers": {
    "gemini": {
      "rate_limit": {
        "fallback_provider": "ollama"
      }
    },
    "ollama": {
      "model": "phi3"  // 軽量モデル
    }
  }
}
```

### 🌐 オフライン環境

```json
{
  "default_provider": "ollama",
  "providers": {
    "ollama": {
      "model": "llama3.2"
    },
    "gemini": {
      "enabled": false
    }
  }
}
```

---

## 🎯 次のステップ

1. ✅ Ollamaインストール
2. ✅ モデルダウンロード
3. ✅ 設定ファイル編集
4. ✅ 動作テスト実行
5. ✅ VECTIS OSアプリで確認

---

## 💡 Tips

### プロバイダー別の特徴

| Provider | 速度 | 品質 | コスト | オフライン |
|----------|------|------|--------|------------|
| Gemini   | ⚡⚡⚡ | ★★★★★ | 無料枠あり | ❌ |
| Ollama (llama3.2) | ⚡⚡ | ★★★★ | 無料 | ✅ |
| Ollama (phi3) | ⚡⚡⚡ | ★★★ | 無料 | ✅ |
| Groq     | ⚡⚡⚡⚡ | ★★★★ | 無料枠あり | ❌ |

### 使い分け

- **開発中**: Gemini (高品質)
- **本番運用**: Ollama (安定性)
- **デモ**: Groq (超高速)

---

## 📞 サポート

問題が発生した場合:

1. `python modules/unified_llm.py` で状態確認
2. ログファイル確認: `logs/vectis.log`
3. 設定リセット: `config/llm_config.json` を削除して再起動
