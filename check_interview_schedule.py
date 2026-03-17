import imaplib, email, os, datetime
from email.header import decode_header

EMAIL_ACCOUNT = os.getenv('MY_EMAIL_ADD', 'yutotuy0209@gmail.com')
EMAIL_PASSWORD = os.getenv('MY_EMAIL_PWD', 'akde cobk mjpu drik').replace(' ', '')

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select('inbox')

    # 過去14日分を検索（より確実に）
    date = (datetime.date.today() - datetime.timedelta(days=14)).strftime('%d-%b-%Y')
    status, messages = mail.search(None, f'(SINCE "{date}")')

    found = False
    for num in messages[0].split():
        res, msg_data = mail.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes): subject = subject.decode(encoding or 'utf-8', errors='ignore')
                
                body = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            try:
                                body += part.get_payload(decode=True).decode(errors='ignore')
                            except: pass
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                
                # 「パーソル」「AVC」「3/16」「16日」などのキーワードでフィルタ
                keywords = ['パーソル', 'AVC', 'Persol']
                date_keywords = ['3/16', '3月16日', '16日']
                
                if any(k in subject or k in body for k in keywords) and any(d in subject or d in body for d in date_keywords):
                    found = True
                    print(f'--- MATCH FOUND ---')
                    print(f'Subject: {subject}')
                    print(f'From: {msg.get("From")}')
                    print(f'Body Snippet: {body[:500]}...')
                    print(f'-------------------\n')
    
    if not found:
        print("指定された条件に一致するメールは見つかりませんでした。")

except Exception as e:
    print(f"Error: {e}")
finally:
    try: mail.logout()
    except: pass
