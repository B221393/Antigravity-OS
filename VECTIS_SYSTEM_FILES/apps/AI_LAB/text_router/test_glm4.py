
import urllib.request
import json
import os
from datetime import datetime

def analyze_with_ollama(text):
    print(f"Testing GLM-4 with text: {text}")
    try:
        url = "http://localhost:11434/api/generate"
        today_str = datetime.now().strftime("%Y-%m-%d (%A)")
        
        prompt = f"""
        You are a smart personal assistant. Analyze the text and classify it into 'schedule', 'todo', or 'other'.
        Current Date: {today_str}
        
        Text: "{text}"
        
        If it involves a specific date/time or deadline, it is a 'schedule'.
        If it is a task without a specific date, it is a 'todo'.
        Otherwise 'other'.

        Extract:
        - title (summary of action)
        - date (YYYY-MM-DD format if applicable, calculate from relative terms like 'tomorrow', 'next week'. Return null if none)
        - category (Choose one: 'Job', 'Deadline', 'Study', 'Personal')
        - memo (details)

        Return JSON ONLY. No markdown.
        Format:
        {{
            "type": "schedule" | "todo" | "other",
            "title": "string",
            "date": "YYYY-MM-DD" | null,
            "category": "string",
            "memo": "string"
        }}
        """
        
        data = {
            "model": "glm4",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        print("Sending request to Ollama (glm4)...")
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get('response', '{}')
            
            # GLM-4 parsing logic from app
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(response_text)
            print("\n✅ Success! GLM-4 Output:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            return parsed

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    # Test case: ambiguous schedule/task
    analyze_with_ollama("来週の火曜日に面接があるので準備する")
