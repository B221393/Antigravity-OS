import warnings
import os
import sys
import mss
import pyautogui
import base64
import time
from datetime import datetime
from PIL import Image

# Setup path for modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.gemini_client import GenerativeModel

class VisionAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Initialize using unified client
        self.model = GenerativeModel('gemini-2.0-flash')


    def capture_screen(self, output_path="screenshot.png"):
        with mss.mss() as sct:
            filename = sct.shot(output=output_path)
            return filename

    def identify_ui(self, instruction, screenshot_path):
        """
        Use Gemini to find coordinates for a specific element. Returns JSON.
        """
        import json
        if self.model:
            # Load the image
            img = Image.open(screenshot_path)
        
        prompt = f"""
        TASK: Identify the precise coordinates of the UI element: '{instruction}'.
        The current screen resolution is {pyautogui.size()[0]}x{pyautogui.size()[1]}.
        
        [AI AGENT GUIDELINES (Jarvis/Operator style)]
        1. Scan the image for icons, buttons, or text that corresponds to the goal.
        2. Provide exact center coordinates (x, y) for clicking.
        3. If there are multiple candidates, prioritize taskbar icons or prominent buttons.
        4. IGNORE reflections or text within the terminal if an actual icon exists.
        
        RETURN FORMAT (ONLY RAW JSON):
        {{
            "x": integer_x,
            "y": integer_y,
            "label": "Name of the element",
            "thought": "Internal reasoning for selecting this point",
            "action": "CLICK" | "RIGHT_CLICK" | "DOUBLE_CLICK"
        }}
        """
        
        try:
            response = self.model.generate_content([prompt, img])
            res_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(res_text)
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def image_to_knowledge(self, image_input):
        """
        Analyze an image and return structured knowledge (Minecraft Sorter style).
        """
        import json
        if not self.model:
            return {"status": "ERROR", "message": "Model not initialized"}
        
        # Determine if input is path or PIL Image
        if isinstance(image_input, str):
            img = Image.open(image_input)
        else:
            img = image_input

        prompt = """
        Analyze this image and extract its core information as a VECTIS System record.
        
        1. CATEGORY: Detect if this is most likely:
           - 'JOB_HUNTING': Company materials, ES, industry research.
           - 'DIARY': Personal photos, food, travel, daily thoughts.
           - 'KNOWLEDGE': Technical snippets, book pages, research papers, news.
        
        2. CONTENT: Perform OCR to extract important text. Summarize it clearly.
        
        3. RARITY: Estimate rarity based on importance (Common, Rare, Epic).
        
        Return ONLY a JSON object with:
        {
            "title": "Short descriptive title",
            "category": "JOB_HUNTING" | "DIARY" | "KNOWLEDGE",
            "content": "Detailed summary of extracted text/information",
            "keywords": ["list", "of", "keywords"],
            "rarity": "Common" | "Rare" | "Epic",
            "reason": "Brief reason for this categorization"
        }
        """
        
        try:
            response = self.model.generate_content([prompt, img])
            res_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(res_text)
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

class ActionAgent:

    def __init__(self):
        # Fail-safe: move mouse to top-left corner to abort
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5 

    def click(self, x, y):
        print(f"Clicking at ({x}, {y})")
        pyautogui.click(x, y)

    def type_text(self, text):
        print(f"Typing: {text}")
        pyautogui.write(text, interval=0.1)

    def press_key(self, key):
        print(f"Pressing key: {key}")
        pyautogui.press(key)

    def fast_open(self, url):
        import webbrowser
        print(f"FAST_BROWSE: {url}")
        webbrowser.open(url)

    def navigate_to(self, target_name):
        """Standardized navigation without Vision logic when possible."""
        sites = {
            "google": "https://www.google.com",
            "search": "https://www.google.com/search?q="
        }
        url = sites.get(target_name.lower())
        if url:
            self.fast_open(url)
            return True
        return False

if __name__ == "__main__":

    # This test requires a valid API Key
    # vision = VisionAgent("YOUR_API_KEY")
    # action = ActionAgent()
    print("Vision & Action Agent initialized.")
