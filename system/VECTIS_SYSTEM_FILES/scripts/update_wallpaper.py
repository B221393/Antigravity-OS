import os
import ctypes
import datetime
from PIL import Image, ImageDraw, ImageFont

def get_task_content():
    # Priority paths
    paths = [
        r"C:\Users\Yuto\Desktop\app\documents\notes\tasks.md",
        r"C:\Users\Yuto\.gemini\antigravity\brain\66ed5608-f571-403e-b7ab-0e03de082ae5\task.md"
    ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                continue
    return None

def create_wallpaper(tasks_text):
    # Screen resolution (Hardcoded for now or get from system)
    width = 1920
    height = 1080
    
    # MAGI Colors
    BG_COLOR = (0, 0, 0)
    FG_AMBER = (255, 170, 0)
    FG_GREEN = (0, 255, 68)
    FG_DIM = (100, 100, 100)
    
    img = Image.new('RGB', (width, height), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    try:
        font_main = ImageFont.truetype("C:\\Windows\\Fonts\\msgothic.ttc", 20)
        font_header = ImageFont.truetype("C:\\Windows\\Fonts\\msgothic.ttc", 30)
        font_small = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 14)
    except:
        font_main = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw Header
    draw.text((50, 50), "VECTIS SYSTEM REPORT :: STATUS COMPLETED", font=font_header, fill=FG_AMBER)
    draw.line((50, 90, width-50, 90), fill=FG_AMBER, width=2)
    
    # Parse Tasks
    y = 120
    if tasks_text:
        lines = tasks_text.split('\n')
        # Filter for completed tasks [x]
        completed_tasks = [l for l in lines if "- [x]" in l]
        # Filter for schedule (section 5)
        schedule_lines = []
        in_schedule = False
        for l in lines:
            if "## 5. スケジュール" in l:
                in_schedule = True
                continue
            if in_schedule and l.startswith("##"):
                in_schedule = False
            if in_schedule and l.strip():
                schedule_lines.append(l.strip())
        
        # Draw Completed Tasks
        draw.text((50, y), "[ COMPLETED MISSIONS ]", font=font_main, fill=FG_GREEN)
        y += 30
        for task in completed_tasks[-15:]: # Show last 15
            clean_task = task.replace("- [x]", "").strip()
            # Remove HTML comments
            import re
            clean_task = re.sub(r'<!--.*?-->', '', clean_task)
            draw.text((70, y), f"✓ {clean_task}", font=font_main, fill=FG_DIM)
            y += 25
            
        y += 40
        # Draw Schedule
        draw.text((50, y), "[ UPCOMING SCHEDULE ]", font=font_main, fill=FG_AMBER)
        y += 30
        for s in schedule_lines:
            draw.text((70, y), s, font=font_main, fill=(200, 200, 200))
            y += 25
            
    else:
        draw.text((50, y), "NO TASK DATA FOUND", font=font_header, fill=FG_DIM)

    # Add timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((width - 250, height - 30), f"UPDATED: {timestamp}", font=font_small, fill=FG_DIM)

    # Save
    wallpaper_path = os.path.join(os.path.dirname(__file__), "wallpaper_gen.png")
    img.save(wallpaper_path)
    return wallpaper_path

def set_wallpaper(path):
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)

if __name__ == "__main__":
    content = get_task_content()
    wp_path = create_wallpaper(content)
    # Convert to absolute path for Windows API
    abs_path = os.path.abspath(wp_path)
    set_wallpaper(abs_path)
    print(f"Wallpaper updated: {abs_path}")
