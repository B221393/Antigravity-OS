import imaplib
import email
from email.header import decode_header
import datetime
import os
import sys

# ---------------------------------------------------------
# 【設定】環境変数からメールアドレスとアプリパスワードを取得します
# ※セキュリティのため、パスワードは直接コードに書かず環境変数(.env等)から読み込みます
# ---------------------------------------------------------
EMAIL_ACCOUNT = os.getenv("MY_EMAIL_ADD", "yutotuy0209@gmail.com")
EMAIL_PASSWORD = os.getenv("MY_EMAIL_PWD", "akde cobk mjpu drik").replace(" ", "")

# Gmailの場合は imap.gmail.com、Outlookの場合は outlook.office365.com
IMAP_SERVER = "imap.gmail.com" 

def clean_text(text):
    if not text: return ""
    return text.replace('\r', '').replace('\n', ' ').strip()

def fetch_todays_emails():
    try:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] メールサーバーに接続しています...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        
        # 受信トレイを選択
        mail.select('inbox')
        
        # 今日の日付でフィルタリング (例: "04-Mar-2026")
        today = datetime.datetime.now().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{today}")')
        
        if status != "OK":
            print("メールの検索に失敗しました。")
            return

        email_ids = messages[0].split()
        if not email_ids:
            print("本日の新しいメールはありません。")
            return
            
        print(f"本日のメールを {len(email_ids)} 件見つけました。解析を開始します...\n")
        
        output_file = "Todays_Tasks_from_Email.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# 本日（{today}）のメール・タスク一覧\n\n")
            
            # 最新のメールから順に取得（後ろからループ）
            for i in reversed(email_ids):
                res, msg_data = mail.fetch(i, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 件名のデコード
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                            
                        # 送信者のデコード
                        from_ = msg.get("From")
                        
                        # 本文の取得
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        pass
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                            except:
                                pass
                        
                        # 最初の300文字だけ抽出（タスク抽出用）
                        snippet = clean_text(body)[:300] + "..." if body else "本文なし"
                        
                        f.write(f"## 件名: {subject}\n")
                        f.write(f"**送信元:** {from_}\n")
                        f.write(f"**内容スニペット:**\n{snippet}\n\n")
                        f.write("---\n")
                        
        print(f"[完了] メールの抽出が完了しました！\n結果を '{output_file}' に保存しました。")
        print("Antigravity（AI）にこのファイルを読み込ませて、タスクを整理してもらいましょう！")
                        
    except imaplib.IMAP4.error as e:
        print(f"ログインエラー: メールアドレスまたはアプリパスワードが間違っているか、IMAP設定が無効になっています。\n詳細: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    if EMAIL_ACCOUNT == "your_email@gmail.com":
        print("⚠️ エラー: メールアドレスとパスワードが設定されていません！")
        print("実行する前に環境変数（MY_EMAIL_ADD と MY_EMAIL_PWD）を設定するか、コード内を直接書き換えてください。（※直接書き換える場合は外部への公開に注意してください）")
        sys.exit(1)
        
    fetch_todays_emails()
