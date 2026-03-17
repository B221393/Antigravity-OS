import datetime
import os
import pickle
from googleapiclient.discovery import build

def get_calendar_events():
    creds = None
    token_path = 'python_scripts/token.pickle'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    else:
        print('token.pickle が見つかりません。')
        return

    if not creds or not creds.valid:
        print('有効な認証情報がありません。')
        return

    try:
        service = build('calendar', 'v3', credentials=creds)

        # 今週・来週の範囲（今日から14日間）
        now = datetime.datetime.utcnow().isoformat() + 'Z'  
        time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=14)).isoformat() + 'Z'

        print('■ Googleカレンダーの予定 (直近14日間)\n')
        events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=time_max,
                                              maxResults=50, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('Googleカレンダーに直近14日間の予定は見つかりませんでした。')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if 'T' in start:
                dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                dt_jst = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                start_str = dt_jst.strftime('%Y/%m/%d %H:%M')
            else:
                start_str = start
            print(f'- {start_str} : {event["summary"]}')

    except Exception as e:
        print(f'カレンダー取得エラー: {e}')

get_calendar_events()
