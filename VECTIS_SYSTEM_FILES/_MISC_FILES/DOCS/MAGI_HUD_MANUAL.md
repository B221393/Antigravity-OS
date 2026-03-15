# 📟 VECTIS MAGI HUD

**「期限を右下に出してくれる奴」こと、VECTIS MAGI SYSTEMの説明書です。**
スーパーコンピュータMAGIのような漆黒×アンバーのインターフェースで、締切管理と情報処理を一元化します。

## 🚀 起動方法

この階層（一番上）にある `LAUNCH_MAGI_HUD.bat` をダブルクリックしてください。

---

## 👁️ MAGI SYSTEM OVERVIEW

### 1. LIMIT COUNTDOWN (締切管理)

- 右下に **「PROJECT: KODANSHA [LIMIT]」** までの残り時間をデジタル表示します。
- 限界時間が近づくにつれ、緊迫感のある表示となります。

### 2. MODE SELECTOR (入力モード)

入力欄下のボタンでモードを切り替えます。

- **MEMO** [AMBER]
  - 思考、メモ、アイデアの記録用。
  - デフォルトモードです。`VECTIS_SYSTEM_FILES/apps/desktop_hud/quick_memos.txt` に記録されます。

- **SEARCH** [BLUE]
  - 外部世界（Web）へのアクセス。
  - 入力したワードでGoogle検索を実行します。

- **TODO** [PINK]
  - 現実的なタスク管理。
  - `VECTIS_SYSTEM_FILES/apps/desktop_hud/user_todo.txt` にタスクを追加します。

- **INBOX** [GREEN]
  - 未処理情報の投げ込み口。
  - AIによる自動仕分け用ボックス `sorter_inbox.txt` に転送されます。

### 3. SPECIAL COMMANDS

- **`yt add [URL]`**: YouTubeの監視対象を追加。
- **`yt key [KEYWORD]`**: 自動収集キーワードを追加。

---
*Created by VECTIS Organization*
