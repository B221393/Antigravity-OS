# 🎯 VECTIS 新規アプリ - クイックスタートガイド

## 📦 3つの新しいアプリが追加されました

### 1️⃣ ES Assistant Quick Launch 📝

**何ができる？**

- エントリーシート（ES）を素早く作成・管理
- コマンドラインから簡単操作
- 既存のStreamlit GUI版とも連携

**起動方法**

```batch
# メインフォルダから
010_START_ES_ASSISTANT.bat

# または直接
cd VECTIS_SYSTEM_FILES\apps\es_assistant
es_quick_launch.bat
```

**メニュー**

```
[1] 📄 新しいESを作成
[2] 📋 Draftsフォルダを開く
[3] 🎯 Targeted ESを開く
[4] 📊 ES一覧を表示
[5] 🚀 ES Assistant GUI起動
[6] 🔍 最新のESを編集
[7] 📂 フォルダ整理
[0] ❌ 終了
```

---

### 2️⃣ Chat Analyzer 💬

**何ができる？**

- チャット会話を貼り付けて自動解析
- 自分と相手の発言を色分け表示
- 統計情報とJSON保存機能

**起動方法**

```batch
# メインフォルダから
012_START_CHAT_ANALYZER.bat
```

**使い方**

1. LINEやDiscordなどの会話をコピー
2. アプリに貼り付け
3. 自分と相手の名前を設定
4. 「解析開始」ボタンをクリック
5. 右側に色分けされた結果が表示される
6. 「保存」ボタンで記録

**対応フォーマット**

- `自分: メッセージ` （コロン形式）
- `[自分] メッセージ` （ブラケット形式）
- `自分 > メッセージ` （矢印形式）
- `12:30 自分: メッセージ` （タイムスタンプ付き）

---

### 3️⃣ Text Router 🔀

**何ができる？**

- テキストを入力するだけで適切なアプリを自動判定
- マインクラフト風の仕分け装置デザイン
- 10種類のカテゴリに自動振り分け

**起動方法**

```batch
# メインフォルダから
013_START_TEXT_ROUTER.bat
```

**使い方**

1. やりたいことを自由にテキストで入力

   ```
   例: 「明日の面接の準備をしたい」
   → 就活・ES関連に自動判定
   
   例: 「友達とのLINEを整理したい」
   → チャット会話に自動判定
   
   例: 「藤井聡太の棋譜を見たい」
   → 将棋に自動判定
   ```

2. 「仕分け開始」ボタンをクリック
3. 適切なアプリが提案される
4. 「はい」で該当アプリが自動起動！

**対応カテゴリ**

- 💼 就活・ES関連
- 💬 チャット会話
- ♟️ 将棋
- 📺 YouTube
- 📅 スケジュール
- 📔 日記・メモ
- 🔍 検索・リサーチ
- 💻 プログラミング
- 🇬🇧 英語・TOEIC
- 🌐 その他・汎用

---

## 🔄 アプリ連携の例

### パターン1: ES作成の完全フロー

```
1. Text Router起動
2. 「講談社のESを書きたい」と入力
3. → ES Quick Launchが起動
4. メニューから [1] 新しいESを作成
5. 企業名: 講談社
6. Notepadで編集開始！
```

### パターン2: 友達との会話を振り返り

```
1. LINEの会話履歴をコピー
2. Chat Analyzer起動
3. 貼り付けて解析
4. 自分と友達の発言が綺麗に整理される
5. 保存して後で見返せる
```

### パターン3: やりたいことが曖昧な時

```
1. Text Router起動
2. 思いついたテキストを入力
   「TOEICの勉強したいけど何から始めよう」
3. → 自動的にTOEIC Masteryが提案される
4. 学習アプリが起動！
```

---

## 📁 保存場所

### ES Assistant

```
VECTIS_SYSTEM_FILES/apps/es_assistant/
├── drafts/              # あなたのES下書き
├── drafts_targeted/     # 企業別ターゲットES
├── templates/           # テンプレート
└── archive/             # 古いESのアーカイブ
```

### Chat Analyzer

```
VECTIS_SYSTEM_FILES/apps/chat_analyzer/
└── saved_conversations/  # 保存した会話ログ（JSON形式）
```

### Text Router

```
VECTIS_SYSTEM_FILES/apps/text_router/
└── routing_log.json      # どのアプリに振り分けたかの履歴
```

---

## 💡 Tips

### ES Quick Launch

- **タイムスタンプ自動付与**: 新規作成時に `draft_20260116_企業名.md` として保存
- **最新編集機能**: `[6]` で最後に作成したESをすぐ開ける
- **フォルダ自動整理**: `[7]` で必要なフォルダを一括作成

### Chat Analyzer

- **ダブルクリック読込**: 保存済みリストをダブルクリックで再読込
- **統計表示**: メッセージ数と文字数をリアルタイム表示
- **Diary連携**: diary アプリのchat_logsフォルダとも連携

### Text Router

- **学習不要**: すぐに使えるキーワードマッチング
- **優先度システム**: 複数マッチした場合は優先度で判定
- **アプリ一覧**: 右側に全アプリが表示され、直接起動も可能

---

## ❓ トラブルシューティング

### アプリが起動しない

```
→ pythonw が PATH に入っているか確認
→ Streamlit アプリは `streamlit run` で起動
```

### 日本語が文字化けする

```
→ 各batファイルは chcp 65001 で UTF-8 に設定済み
→ Notepad を VS Code や他のエディタに変更も可能
```

### 保存した会話が見つからない

```
→ saved_conversations/ フォルダを確認
→ JSON形式で保存されています
```

---

## 🎨 カスタマイズ

### Text Router にアプリを追加

`text_router/app.py` の `load_routes()` を編集:

```python
"新カテゴリ": {
    "keywords": ["キーワード1", "キーワード2"],
    "app_path": os.path.join(base_path, "your_app", "app.py"),
    "app_type": "streamlit",  # または "bat", "python"
    "icon": "🌟",
    "priority": 8
}
```

### Chat Analyzer のカラーテーマ変更

`chat_analyzer/app.py` の色設定を編集:

```python
bg="#0a0e27",      # 背景色
fg="#00ffff",      # テキスト色
```

---

## 📚 もっと詳しく知りたい？

詳細なドキュメント:

```
VECTIS_SYSTEM_FILES/apps/APP_INTEGRATION_REPORT.md
```

---

**🎉 これで準備完了！早速使ってみましょう！**

作成日: 2026-01-16  
Version: 1.0
