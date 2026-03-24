# 📟 VECTIS MAGI HUD

**「期限を右下に出してくれる奴」こと、VECTIS MAGI SYSTEMの説明書です。**
スーパーコンピュータMAGIを模したインターフェースで、締切管理と情報処理を一元化します。

## 🚀 起動方法

`01_Main_HUD.bat` をダブルクリックしてください。

---

## 👁️ MAGI SYSTEM OVERVIEW

### 1. LIMIT COUNTDOWN (締切管理)

- 右下に **「PROJECT: KODANSHA [LIMIT]」** までの残り時間をデジタル表示します。
- 限界時間が近づくにつれ、緊迫感のある表示となります。

### 2. THE THREE MAGI (入力モード)

入力欄下のボタンでモードを切り替えます。それぞれがMAGIの3つの人格に対応しています。

- **MELCHIOR-1 (MEMO)** [AMBER]
  - 科学者としてのメルキオール。思考、メモ、アイデアの記録用。
  - デフォルトモードです。`quick_memos.txt` に記録されます。

- **BALTHASAR-2 (SEARCH)** [BLUE]
  - 母としてのバルタザール。外部世界（Web）へのアクセス。
  - 入力したワードでGoogle検索を実行します。

- **CASPER-3 (TODO)** [PINK]
  - 女としてのカスパー。現実的なタスク管理。
  - `user_todo.txt` にタスクを追加します。

- **MAGI-SYS (INBOX)** [GREEN]
  - システムの中枢。未処理情報の投げ込み口。
  - AIによる自動仕分け用ボックス `sorter_inbox.txt` に転送されます。

### 3. SPECIAL COMMANDS

- **`yt add [URL]`**: YouTubeの監視対象を追加。
- **`yt key [KEYWORD]`**: 自動収集キーワードを追加。

---
*Created by VECTIS Organization*
