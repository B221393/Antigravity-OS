import os
import time
import json
import pickle
import io
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- Settings ---
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '12xQcqpv_FPkH3H4e1QCsH5ed5-UnBC0D'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.pickle')

def get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_PATH):
                print(f"Error: {CREDS_PATH} not found.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def watch_drive():
    service = get_service()
    if not service: return
    print(f"[{time.strftime('%H:%M:%S')}] Monitoring started (Folder: {FOLDER_ID})")

    while True:
        try:
            # mimeTypeも取得するように変更
            query = f"'{FOLDER_ID}' in parents and name = 'command.json' and trashed = false"
            results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
            files = results.get('files', [])

            for file in files:
                file_id = file['id']
                mime_type = file.get('mimeType', '')
                
                print(f"[{time.strftime('%H:%M:%S')}] Found: {file['name']} (Type: {mime_type})")

                # Googleドキュメント形式（バイナリでない）の場合はスキップして削除
                if "application/vnd.google-apps" in mime_type:
                    print(f"!!! Warning: Invalid file format (Google Doc). Deleting...")
                    service.files().delete(fileId=file_id).execute()
                    continue

                try:
                    # ダウンロード実行
                    request = service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    
                    content = fh.getvalue().decode('utf-8').strip()
                    if not content:
                        print("!!! Warning: Empty file.")
                    else:
                        data = json.loads(content)
                        print(f">>> Prompt: {data.get('prompt', 'N/A')}")
                    
                except Exception as e:
                    print(f"!!! Error processing file content: {e}")
                
                # 成功・失敗に関わらず、見つけた command.json は削除してループを止める
                service.files().delete(fileId=file_id).execute()
                print("--- Cleaned up command file ---")

        except Exception as e:
            print(f"Monitor Loop Error: {e}")
            time.sleep(10)

        time.sleep(5)

if __name__ == "__main__":
    try:
        watch_drive()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
