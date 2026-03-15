import os
import datetime
import random
import ctypes
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
WALLPAPER_PATH = os.path.abspath("vectis_wallpaper_generated.png")
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

# ID of the Spreadsheet created by the GAS NLM Aggregator
# USER MUST UPDATE THIS ID
NLM_SHEET_ID = 'YOUR_NLM_SHEET_ID_HERE' 

# Use a Japanese compatible font. Meiryo is standard on Windows.
FONT_PATH = "C:\\Windows\\Fonts\\meiryo.ttc" 
FONT_PATH_BOLD = "C:\\Windows\\Fonts\\meiryob.ttc"
# Consolas for code/diagram labels if available, else Meiryo
FONT_CODE = "C:\\Windows\\Fonts\\consola.ttf" 

def get_services():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Check if scopes match (simplistic check: if we added scopes, we need new token)
    # Ideally should decode token scope, but for now force re-auth if token is old or we suspect scope change
    # For this implementation, let's just re-auth if invalid. 
    # NOTE: User might need to delete token.pickle manually if scope changed.
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            
    calendar_service = build('calendar', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return calendar_service, sheets_service

def fetch_events(service, max_results=15):
    now = datetime.datetime.utcnow().isoformat() + 'Z' 
    print(f'Getting the upcoming {max_results} events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=max_results, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def fetch_nlm_stats(service):
    """Fetches the latest entry from the NLM Log Sheet."""
    if NLM_SHEET_ID == 'YOUR_NLM_SHEET_ID_HERE':
        return {"last_update": "NOT CONNECTED", "latest_summary": "Link Sheet ID in main.py"}

    try:
        # Assuming Data is in 'NLM_Logs'!A2:C
        # We just want the last row. To do that efficiently without knowing row count,
        # we can fetch a range or just metadata. Let's fetch the whole column A (Timestamp) and B (Name).
        # Better: use append logic or get last row. 
        # Simple approach: Read all data (assuming not huge yet) or use a logic to find last.
        # Let's read A:C
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=NLM_SHEET_ID,
                                    range='NLM_Logs!A2:C').execute()
        values = result.get('values', [])
        
        if not values:
            return {"last_update": "NO DATA", "latest_summary": "Waiting for NLM..."}
            
        last_row = values[-1]
        timestamp = last_row[0] if len(last_row) > 0 else "N/A"
        filename = last_row[1] if len(last_row) > 1 else "Unknown"
        summary = last_row[2] if len(last_row) > 2 else "..."
        
        # Simple formatting of timestamp if possible (assuming GAS used standard format)
        return {
            "last_update": timestamp,
            "latest_summary": f"Ingested: {filename}"
        }
    except Exception as e:
        print(f"Error fetching NLM stats: {e}")
        return {"last_update": "ERROR", "latest_summary": "Check API/ID"}

def draw_architecture(draw, width, height, fonts, nlm_stats):
    """Draws the VECTIS System Architecture on the left side."""
    f_bold, f_med, f_small, f_tiny, f_code = fonts
    
    # Diagram Config
    diagram_center_x = 600
    diagram_center_y = 500
    box_width = 220
    box_height = 100
    color_accent = (0, 255, 150)
    color_box = (40, 40, 50)
    color_text = (200, 200, 200)

    def draw_box(x, y, title, subtitle, color=color_box, border=None):
        rect = [(x - box_width//2, y - box_height//2), (x + box_width//2, y + box_height//2)]
        draw.rectangle(rect, fill=color, outline=border, width=2 if border else 0)
        draw.text((x - box_width//2 + 10, y - 20), title, fill=(255, 255, 255), font=f_small)
        draw.text((x - box_width//2 + 10, y + 10), subtitle, fill=(150, 150, 150), font=f_tiny)
        return rect

    # 1. USER (Top)
    user_rect = draw_box(diagram_center_x, diagram_center_y - 250, "USER (You)", "Objective / Will", border=color_accent)

    # 2. VECTIS OS (Center)
    os_rect = draw_box(diagram_center_x, diagram_center_y, "VECTIS OS", "Integrated Thinking", color=(50, 50, 70), border=(0, 150, 255))
    
    # 3. SECOND BRAIN (NotebookLM) - Emphasized (Left)
    # Dynamic Border Color based on connection
    nlm_border = (50, 255, 50) if nlm_stats['last_update'] != "NOT CONNECTED" else (100, 100, 100)
    nb_rect = draw_box(diagram_center_x - 300, diagram_center_y, "NotebookLM", "Second Brain", color=(30, 60, 30), border=nlm_border)
    
    # 4. EXTERNAL WORLD (Right)
    world_rect = draw_box(diagram_center_x + 300, diagram_center_y, "REAL WORLD", "Daily Tasks / Field", color=(60, 30, 30))

    # 5. OUTPUT/LOG (Bottom)
    log_rect = draw_box(diagram_center_x, diagram_center_y + 250, "INTEL LOG", "Strategic Archive")

    # Connecting Lines
    def connect(rect1, rect2, label=None, color=(100, 100, 100)):
        # Simple center-to-center line for now
        c1 = ((rect1[0][0]+rect1[1][0])//2, (rect1[0][1]+rect1[1][1])//2)
        c2 = ((rect2[0][0]+rect2[1][0])//2, (rect2[0][1]+rect2[1][1])//2)
        draw.line([c1, c2], fill=color, width=2)
        if label:
            mx, my = (c1[0]+c2[0])//2, (c1[1]+c2[1])//2
            draw.text((mx-30, my-10), label, fill=color, font=f_tiny)

    connect(user_rect, os_rect, "Direct command")
    connect(os_rect, nb_rect, "RAG / Context", color=(50, 255, 50))
    connect(os_rect, world_rect, "Execution")
    connect(os_rect, log_rect, "Record")
    
    # Second Brain Deep Dive Details (DYNAMIC)
    draw.text((diagram_center_x - 450, diagram_center_y + 80), ">> SECOND BRAIN STATUS", fill=(50, 255, 50), font=f_code)
    draw.text((diagram_center_x - 450, diagram_center_y + 100), f"   - Last Knowledge: {nlm_stats['last_update']}", fill=(150, 255, 150), font=f_tiny)
    
    # Truncate summary if too long
    summary = nlm_stats['latest_summary']
    if len(summary) > 30: summary = summary[:27] + "..."
    draw.text((diagram_center_x - 450, diagram_center_y + 120), f"   - Recent: {summary}", fill=(150, 255, 150), font=f_tiny)

    draw.text((50, 800), "ARCHITECTURE: SELF-EXPANSION MODEL v2.0", fill=(100, 100, 100), font=f_code)

def create_wallpaper(events, nlm_stats):
    # Base Image
    width = 1920
    height = 1080
    bg_color = (15, 15, 18) # Deep Dark
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_large = ImageFont.truetype(FONT_PATH_BOLD, 80)
        font_med = ImageFont.truetype(FONT_PATH, 32)
        font_small = ImageFont.truetype(FONT_PATH, 22)
        font_tiny = ImageFont.truetype(FONT_PATH, 16)
        if os.path.exists(FONT_CODE):
            font_code = ImageFont.truetype(FONT_CODE, 18)
        else:
            font_code = font_tiny
    except IOError:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()
        font_code = ImageFont.load_default()
    
    fonts = (font_large, font_med, font_small, font_tiny, font_code)

    # --- LEFT SIDE: ARCHITECTURE ---
    draw_architecture(draw, width, height, fonts, nlm_stats)

    # --- RIGHT SIDE: ROUTINE ---
    margin_x = 1350
    margin_y = 100
    
    # Header Information (Top Left)
    today = datetime.datetime.now()
    date_str = today.strftime("%Y.%m.%d")
    day_str = today.strftime("%A").upper()
    time_now = today.strftime("%H:%M")
    
    draw.text((50, 40), f"{date_str} [{day_str}]", fill=(0, 255, 150), font=font_med)
    draw.text((50, 80), f"VECTIS OS // {time_now}", fill=(255, 255, 255), font=font_large)

    # Routine Panel
    draw.rectangle([(margin_x - 20, 0), (width, height)], fill=(25, 25, 30))
    draw.text((margin_x, margin_y), "TODAY'S ROUTINE", fill=(0, 255, 150), font=font_med)
    draw.line([(margin_x, margin_y + 45), (width - 50, margin_y + 45)], fill=(0, 255, 150), width=2)

    current_y = margin_y + 70
    
    if not events:
         draw.text((margin_x, current_y), "NO ACTIVE TASKS", fill=(100, 100, 100), font=font_small)
    else:
        for i, event in enumerate(events):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event['summary']
            
            try:
                dt = datetime.datetime.fromisoformat(start)
                time_str = dt.strftime("%H:%M")
                is_passed = dt < datetime.datetime.now(dt.tzinfo)
            except ValueError:
                time_str = "ALL DAY"
                is_passed = False

            if "#重要" in summary or "面接" in summary:
                bar_color = (255, 50, 50) 
                text_color = (255, 255, 255)
            elif is_passed:
                 bar_color = (60, 60, 60)
                 text_color = (100, 100, 100)
            else:
                bar_color = (0, 150, 255)
                text_color = (220, 220, 220)

            # Draw time slot
            draw.text((margin_x, current_y), time_str, fill=bar_color, font=font_small)
            draw.text((margin_x + 80, current_y), summary, fill=text_color, font=font_small)
            draw.line([(margin_x + 65, current_y + 10), (margin_x + 65, current_y + 35)], fill=(50, 50, 50), width=1)
            
            current_y += 50
            if current_y > height - 100:
                break

    # Bottom Status
    draw.text((width - 300, height - 30), f"LAST SYNC: {datetime.datetime.now().strftime('%H:%M:%S')}", fill=(100, 100, 100), font=font_tiny)

    img.save(WALLPAPER_PATH)
    return WALLPAPER_PATH

def set_wallpaper_windows(image_path):
    print(f"Setting wallpaper to: {image_path}")
    SPI_SETDESKWALLPAPER = 20
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

def main():
    try:
        # Re-auth might be triggered here to add Sheets scope
        calendar_service, sheets_service = get_services()
        
        events = fetch_events(calendar_service)
        nlm_stats = fetch_nlm_stats(sheets_service)
        
        image_path = create_wallpaper(events, nlm_stats)
        set_wallpaper_windows(image_path)
        print("Wallpaper updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

