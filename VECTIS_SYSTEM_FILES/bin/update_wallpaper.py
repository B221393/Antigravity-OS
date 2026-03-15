"""
VECTIS Schedule Wallpaper Auto-Updater
スケジュールを読み込んで壁紙を自動生成・設定する
"""

from PIL import Image, ImageDraw, ImageFont
import ctypes
import os
from datetime import datetime
from pathlib import Path

# パス設定
SCHEDULE_FILE = Path(r"c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\CAREER\SCHEDULE.md")
WALLPAPER_OUTPUT = Path(r"c:\Users\Yuto\Desktop\SHUKATSU_WALLPAPER.png")
FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"  # MSゴシック

def parse_schedule(schedule_file: Path) -> list[dict]:
    """スケジュールファイルからイベントを抽出"""
    events = []
    if not schedule_file.exists():
        return events
    
    content = schedule_file.read_text(encoding='utf-8')
    
    # 直近の予定セクションを探す
    in_schedule_section = False
    for line in content.split('\n'):
        if '直近の予定' in line:
            in_schedule_section = True
            continue
        if in_schedule_section and line.startswith('---'):
            break
        if in_schedule_section and '|' in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            # ヘッダー行をスキップ
            if len(parts) >= 4 and parts[0] not in ['日付', ':---']:
                if parts[0].startswith(':'):
                    continue
                date = parts[0].replace('**', '')
                weekday = parts[1]
                event_name = parts[2]
                status = parts[3]
                if date and event_name:
                    events.append({
                        'date': date,
                        'weekday': weekday,
                        'event': event_name,
                        'status': '✅' if '完了' in status or '✅' in status else '📋'
                    })
    return events

def create_wallpaper(events: list[dict], width=1920, height=1080):
    """スケジュールを含む壁紙を生成"""
    # 背景: ダークグラデーション
    img = Image.new('RGB', (width, height), (10, 15, 30))
    draw = ImageDraw.Draw(img)
    
    # グリッドパターン（薄いシアン）
    for x in range(0, width, 50):
        draw.line([(x, 0), (x, height)], fill=(0, 50, 70), width=1)
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill=(0, 50, 70), width=1)
    
    # フォント設定
    try:
        font_title = ImageFont.truetype(FONT_PATH, 28)
        font_event = ImageFont.truetype(FONT_PATH, 20)
        font_small = ImageFont.truetype(FONT_PATH, 16)
    except:
        font_title = ImageFont.load_default()
        font_event = font_title
        font_small = font_title
    
    # パネル位置（右上）
    panel_x = width - 450
    panel_y = 50
    panel_width = 400
    panel_height = 250
    
    # パネル背景（半透明風）
    for i in range(panel_height):
        alpha = int(180 - i * 0.3)
        draw.rectangle(
            [(panel_x, panel_y + i), (panel_x + panel_width, panel_y + i + 1)],
            fill=(20, 30, 50)
        )
    
    # 枠線
    draw.rectangle(
        [(panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height)],
        outline=(0, 200, 255),
        width=2
    )
    
    # タイトル
    title = f"SHUKATSU SCHEDULE {datetime.now().year}"
    draw.text((panel_x + 20, panel_y + 15), title, fill=(0, 220, 255), font=font_title)
    
    # イベント一覧
    y_offset = panel_y + 60
    for event in events[:5]:  # 最大5件
        status_color = (100, 255, 100) if event['status'] == '✅' else (255, 200, 100)
        text = f"{event['status']} {event['date']}({event['weekday']}) {event['event']}"
        draw.text((panel_x + 20, y_offset), text, fill=(220, 220, 220), font=font_event)
        y_offset += 35
    
    # 更新時刻
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    draw.text((panel_x + 20, panel_y + panel_height - 30), f"Updated: {update_time}", fill=(100, 100, 100), font=font_small)
    
    return img

def set_wallpaper(image_path: Path):
    """Windowsの壁紙を設定"""
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(image_path), 3)

def main():
    print("スケジュール読み込み中...")
    events = parse_schedule(SCHEDULE_FILE)
    
    if not events:
        print("スケジュールが見つかりません")
        events = [{'date': '予定なし', 'event': 'スケジュールを追加してください', 'status': '📋'}]
    
    print(f"{len(events)}件のイベントを検出")
    
    print("壁紙生成中...")
    wallpaper = create_wallpaper(events)
    wallpaper.save(WALLPAPER_OUTPUT)
    print(f"保存: {WALLPAPER_OUTPUT}")
    
    print("壁紙設定中...")
    set_wallpaper(WALLPAPER_OUTPUT)
    print("壁紙を設定しました！")

if __name__ == "__main__":
    main()
