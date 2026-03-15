"""
📅 予定 (Calendar) + 🍅 ポモドーロ - 今後1ヶ月の予定管理アプリ
Port: 8515
就活イベント、締切、面接などを一覧管理
空き時間をポモドーロセッションで自動埋め機能付き
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
import sys
import uuid

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Config
DATA_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(DATA_DIR, "events.json")

# 🍅 ポモドーロ設定 (ぷよぷよの「設定値」= 変数の活用)
POMODORO_CONFIG = {
    "work_minutes": 25,      # 作業時間
    "short_break": 5,        # 短い休憩
    "long_break": 15,        # 長い休憩（4回ごと）
    "sessions_before_long": 4,
}

# Page Config
st.set_page_config(page_title="📅 カレンダー | 自分ステーション", page_icon="📅", layout="wide")
apply_vectis_style()

# Custom Styles
st.markdown("""
<style>
    .event-card {
        background: rgba(20, 20, 20, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #FF9900;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .event-card:hover {
        border-color: #FF9900;
        transform: translateX(5px);
    }
    .event-card.job {
        border-left-color: #00FFCC;
    }
    .event-card.deadline {
        border-left-color: #FF4444;
    }
    .event-card.personal {
        border-left-color: #9966FF;
    }
    .event-card.pomodoro {
        border-left-color: #FF6347;
        background: rgba(255, 99, 71, 0.1);
    }
    .event-tag.pomodoro {
        background: rgba(255, 99, 71, 0.2);
        color: #FF6347;
        border-color: #FF6347;
    }
    .pomodoro-timer {
        background: linear-gradient(135deg, rgba(255, 99, 71, 0.2), rgba(255, 69, 0, 0.1));
        border: 1px solid rgba(255, 99, 71, 0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 12px 0;
    }
    .timer-display {
        font-family: 'Share Tech Mono', monospace;
        font-size: 2.5em;
        color: #FF6347;
        font-weight: bold;
    }
    .event-date {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.9em;
        color: #00FFCC;
        opacity: 0.8;
    }
    .event-title {
        font-size: 1.1em;
        font-weight: 700;
        margin: 8px 0;
        color: white;
    }
    .event-tag {
        display: inline-block;
        font-size: 0.7em;
        padding: 3px 10px;
        border-radius: 20px;
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.3);
        color: #00FFCC;
        margin-right: 8px;
    }
    .event-tag.job { background: rgba(0, 255, 204, 0.2); }
    .event-tag.deadline { background: rgba(255, 68, 68, 0.2); color: #FF4444; border-color: #FF4444; }
    .week-header {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.2em;
        color: #FF9900;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 153, 0, 0.3);
    }
    .today-badge {
        background: linear-gradient(45deg, #00FFCC, #0099FF);
        color: black;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7em;
        font-weight: bold;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# === Data Functions ===
def load_events():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_events(events):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

def get_events_for_month():
    """Get events for the next 30 days"""
    events = load_events()
    today = datetime.now().date()
    end_date = today + timedelta(days=30)
    
    filtered = []
    for e in events:
        try:
            event_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
            if today <= event_date <= end_date:
                e["_date_obj"] = event_date
                filtered.append(e)
        except:
            pass
    
    return sorted(filtered, key=lambda x: x["_date_obj"])

# === 🍅 ポモドーロ関数 (ぷよぷよプログラミング公式用語との対応) ===
def find_free_slots(target_date, events):
    """
    1日の空き時間を検出
    ぷよぷよで言う「Stage.checkFall」 (盤面の空き状況を確認するロジック) に相当
    """
    day_start = datetime.combine(target_date, datetime.strptime("09:00", "%H:%M").time())
    day_end = datetime.combine(target_date, datetime.strptime("22:00", "%H:%M").time())
    
    day_events = []
    for e in events:
        if e.get("time"):
            try:
                event_time = datetime.strptime(e["time"], "%H:%M").time()
                event_start = datetime.combine(target_date, event_time)
                event_end = event_start + timedelta(hours=1)
                day_events.append((event_start, event_end))
            except ValueError:
                pass
    
    day_events.sort(key=lambda x: x[0])
    free_slots = []
    current_time = day_start
    
    # 盤面（スケジュール）を走査して空き（Gap）を見つけるループ
    for event_start, event_end in day_events:
        if current_time < event_start:
            gap_minutes = (event_start - current_time).total_seconds() / 60
            # 条件分岐: ぷよが置けるか判定 (Stage.checkEraseのような判定ロジック)
            if gap_minutes >= POMODORO_CONFIG["work_minutes"]:
                free_slots.append({"start": current_time, "end": event_start, "duration_min": int(gap_minutes)})
        current_time = max(current_time, event_end)
    
    if current_time < day_end:
        gap_minutes = (day_end - current_time).total_seconds() / 60
        if gap_minutes >= POMODORO_CONFIG["work_minutes"]:
            free_slots.append({"start": current_time, "end": day_end, "duration_min": int(gap_minutes)})
    return free_slots

def auto_fill_pomodoro(target_date):
    """
    空き時間にポモドーロを自動挿入
    ぷよぷよで言う「Player.createNewPuyo」 (新しいぷよを盤面に生成して配置) に相当
    """
    events = load_events()
    day_events = [e for e in events if e.get("date") == target_date.strftime("%Y-%m-%d")]
    free_slots = find_free_slots(target_date, day_events)
    
    added_count = 0
    session_num = 1
    work_time = POMODORO_CONFIG["work_minutes"]
    break_time = POMODORO_CONFIG["short_break"]
    cycle_time = work_time + break_time
    
    for slot in free_slots:
        possible_sessions = slot["duration_min"] // cycle_time
        current_start = slot["start"]
        
        for i in range(int(possible_sessions)):
            new_event = {
                "id": str(uuid.uuid4()),
                "title": f"🍅 ポモドーロ #{session_num}",
                "date": target_date.strftime("%Y-%m-%d"),
                "time": current_start.strftime("%H:%M"),
                "category": "🍅 ポモドーロ",
                "memo": f"{work_time}分集中 → {break_time}分休憩",
                "created": datetime.now().isoformat(),
                "auto_generated": True
            }
            # 配列に追加: Stage.board[y][x] = puyo のようにデータをセット
            events.append(new_event)
            added_count += 1
            session_num += 1
            current_start += timedelta(minutes=cycle_time)
    
    if added_count > 0:
        save_events(events)
    return added_count

def clear_auto_pomodoro(target_date=None):
    """
    自動生成ポモドーロを削除
    ぷよぷよで言う「Stage.erasing」 (消去アニメーション後のデータ削除) に相当
    """
    events = load_events()
    if target_date:
        date_str = target_date.strftime("%Y-%m-%d")
        events = [e for e in events if not (e.get("auto_generated") and e.get("date") == date_str)]
    else:
        events = [e for e in events if not e.get("auto_generated")]
    save_events(events)

def sync_from_google():
    """Googleカレンダーから予定を同期"""
    try:
        # Import dynamically to avoid issues if file is missing/broken
        try:
            from google_calendar_client import GoogleCalendarClient
        except ImportError:
            st.error("GoogleCalendarClientが見つかりません (google_calendar_client.py)")
            return 0
            
        auth_client = GoogleCalendarClient()
        g_events = auth_client.get_upcoming_events(max_results=50)
        
        if not g_events:
            return 0
            
        local_events = load_events()
        # Create a set of existing IDs (if we decide to track GCal IDs) or simple dedupe key
        existing_keys = set()
        for e in local_events:
            # Key: date + title
            key = f"{e['date']}_{e['title']}"
            existing_keys.add(key)
            
        added_count = 0
        for ge in g_events:
            start = ge['start'].get('dateTime', ge['start'].get('date'))
            title = ge.get('summary', 'No Title')
            
            # Parse date
            date_str = start[:10] # YYYY-MM-DD
            time_str = ""
            if 'T' in start:
                time_str = start[11:16] # HH:MM
            
            key = f"{date_str}_{title}"
            
            if key not in existing_keys:
                new_event = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "date": date_str,
                    "time": time_str,
                    "category": "☁️ Google", # Special category for synced events
                    "memo": ge.get('description', '') + f"\n(Location: {ge.get('location', '')})",
                    "created": datetime.now().isoformat(),
                    "source": "google_calendar",
                    "gcal_id": ge['id']
                }
                local_events.append(new_event)
                existing_keys.add(key)
                added_count += 1
        
        save_events(local_events)
        return added_count

    except Exception as e:
        st.error(f"同期エラー: {e}")
        return -1

# === Sidebar ===
with st.sidebar:
    render_global_road()
    st.markdown("---")
    st.markdown("##### ➕ 新しい予定")
    
    with st.form("add_event"):
        title = st.text_input("タイトル", placeholder="面接、締切、など...")
        date = st.date_input("日付", value=datetime.now().date())
        time_str = st.text_input("時間 (任意)", placeholder="14:00")
        category = st.selectbox("カテゴリ", ["💼 就活", "🔴 締切", "📝 その他"])
        memo = st.text_area("メモ", placeholder="場所、準備物など...", height=80)
        
        if st.form_submit_button("✅ 追加"):
            events = load_events()
            new_event = {
                "id": str(datetime.now().timestamp()),
                "title": title,
                "date": date.strftime("%Y-%m-%d"),
                "time": time_str,
                "category": category,
                "memo": memo,
                "created": datetime.now().isoformat()
            }
            events.append(new_event)
            save_events(events)
            st.success("追加しました！")
            st.rerun()
    
    # === 🍅 ポモドーロセクション ===
    st.markdown("---")
    st.markdown("##### 🍅 ポモドーロ")
    st.markdown('<div class="pomodoro-timer"><div class="timer-display">25:00</div></div>', unsafe_allow_html=True)
    
    pomo_date = st.date_input("対象日", value=datetime.now().date(), key="pomo_date")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🍅 空き時間を埋める", use_container_width=True):
            count = auto_fill_pomodoro(pomo_date)
            if count > 0:
                st.success(f"✅ {count}個のポモドーロを追加!")
                st.rerun()
            else:
                st.info("空き時間がありません")
    
    with col_p2:
        if st.button("🗑️ 自動分を削除", use_container_width=True):
            clear_auto_pomodoro(pomo_date)
            st.success("削除しました")
            st.rerun()

    st.markdown("---")
    st.markdown("##### ☁️ Google連携")
    if st.button("🔄 Googleカレンダーから同期", use_container_width=True):
        count = sync_from_google()
        if count > 0:
            st.success(f"✅ {count}件の予定を同期しました！")
            st.rerun()
        elif count == 0:
            st.info("新しい予定はありませんでした。")
        else:
            pass # Error displayed in func

# === Main Content ===
st.markdown(get_station_header(
    title="📅 カレンダー + 🍅 ポモドーロ",
    subtitle="今後1ヶ月の予定・締切を管理 | 空き時間自動埋め機能",
    channel_id="TOOL.03"
), unsafe_allow_html=True)

# Quick Stats
today = datetime.now().date()
events = get_events_for_month()
job_events = [e for e in events if "就活" in e.get("category", "")]
deadline_events = [e for e in events if "締切" in e.get("category", "")]
pomodoro_events = [e for e in events if "ポモドーロ" in e.get("category", "")]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📆 総予定数", len(events))
with col2:
    st.metric("💼 就活", len(job_events))
with col3:
    st.metric("🔴 締切", len(deadline_events))
with col4:
    st.metric("🍅 ポモドーロ", len(pomodoro_events))

st.markdown("---")

# Group by week
if not events:
    st.info("👉 サイドバーから予定を追加してください")
else:
    current_week = None
    
    for e in events:
        event_date = e["_date_obj"]
        week_start = event_date - timedelta(days=event_date.weekday())
        week_label = f"{week_start.strftime('%m/%d')} の週"
        
        if week_label != current_week:
            current_week = week_label
            st.markdown(f'<div class="week-header">📆 {week_label}</div>', unsafe_allow_html=True)
        
        # Determine card class
        card_class = "event-card"
        tag_class = "event-tag"
        if "就活" in e.get("category", ""):
            card_class += " job"
            tag_class += " job"
        elif "締切" in e.get("category", ""):
            card_class += " deadline"
            tag_class += " deadline"
        elif "ポモドーロ" in e.get("category", ""):
            card_class += " pomodoro"
            tag_class += " pomodoro"
        else:
            card_class += " personal"
        
        # Today badge
        today_badge = ""
        if event_date == today:
            today_badge = '<span class="today-badge">TODAY</span>'
        
        # Format date display
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        date_display = f"{event_date.strftime('%m/%d')} ({weekdays[event_date.weekday()]})"
        if e.get("time"):
            date_display += f" {e['time']}"
        
        col_main, col_action = st.columns([5, 1])
        
        with col_main:
            st.markdown(f"""
            <div class="{card_class}">
                <div class="event-date">{date_display}{today_badge}</div>
                <div class="event-title">{e['title']}</div>
                <span class="{tag_class}">{e['category']}</span>
                {f'<div style="margin-top:8px; font-size:0.85em; opacity:0.7;">{e.get("memo", "")}</div>' if e.get("memo") else ''}
            </div>
            """, unsafe_allow_html=True)
        
        with col_action:
            if st.button("🗑️", key=f"del_{e['id']}", help="削除"):
                all_events = load_events()
                all_events = [x for x in all_events if x.get("id") != e["id"]]
                save_events(all_events)
                st.rerun()

# === Import from Job Hunting Cards ===
st.markdown("---")
with st.expander("🔄 就活カードから予定をインポート"):
    st.info("知識カード(.kcard)から締切情報を自動抽出できます（開発中）")
    # Future: scan .kcard files for date-like content

st.markdown("---")
render_station_footer()
