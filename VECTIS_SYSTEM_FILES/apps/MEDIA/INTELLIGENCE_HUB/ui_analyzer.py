
import os
import sys
import json
import base64
from datetime import datetime
from PIL import Image

# Setup path for modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

from modules.gemini_client import GenerativeModel
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def analyze_page_ui(url, output_dir=None):
    """
    Captures a specific URL and performs AI Vision Analysis on the UI.
    Returns a dictionary with the analysis results.
    """
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "data", "screenshots")
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_filename = f"UI_SCAN_{timestamp}.png"
    screenshot_path = os.path.join(output_dir, screenshot_filename)
    
    print(f"   🖼️ Analyzing UI (Vision + HTML Structure): {url}")
    
    # Playwright Execution
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=30000)
            
            # Screenshot
            page.screenshot(path=screenshot_path)
            
            # HTML Structure Analysis (Text based)
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove noise
            for script in soup(["script", "style", "svg", "path", "noscript"]):
                script.decompose()
            
            text_structure = soup.get_text(separator=' | ', strip=True)[:15000] # Limit size
            
            browser.close()
    except Exception as e:
        print(f"   ❌ Playwright Error: {e}")
        return {"status": "error", "message": str(e)}

    # AI Analysis
    try:
        model = GenerativeModel('gemini-2.0-flash')
        img = Image.open(screenshot_path)
        
        prompt = f"""
        You are a world-class UI/UX Designer and Frontend Engineer (Top 1% Talent).
        
        Analyze this recruitment website based on two inputs:
        1. The Screenshot (Visual Design)
        2. The HTML Text Structure (Information Architecture) below:
        
        [HTML Text Structure Start]
        {text_structure}
        [HTML Text Structure End]
        
        Your goal is to perform a strict, professional critique.
        Do NOT be nice. Be critical and objective.
        
        Evaluate NOT ONLY the visuals but also the 'Information Architecture' and 'Copywriting'.
        Does the text make sense? Is the hierarchy clear from the text alone?
        
        Output strictly in JSON format:
        {{
          "ui_score": 1-10 (be strict, 5 is average),
          "critique_summary": "One sentence summary of the design & content quality",
          "good_points": ["Specific point 1", "Specific point 2"],
          "bad_points": ["Specific point 1", "Specific point 2"],
          "code_quality_insight": "Insight about the semantic structure or text hierarchy",
          "design_study": {{
            "theme": "The main design concept",
            "professional_insight": "Deep insight (e.g. Cognitive Load, Semantics, Color Theory)",
            "improvement_idea": "Concrete suggestion to fix the biggest flaw"
          }}
        }}
        """
        
        response = model.generate_content([prompt, img])
        res_text = response.text.strip().replace("```json", "").replace("```", "")
        
        analysis = json.loads(res_text)
        analysis['screenshot_path'] = screenshot_path
        return analysis
            
    except Exception as e:
        print(f"   [UI Analysis Error] {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test run
    test_url = "https://www.google.com"
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print(f"Testing UI Analyzer on: {test_url}")
    result = analyze_page_ui(test_url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
