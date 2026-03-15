import os
import sys
import json
import time
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Path setup for Gemini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../../..")))

try:
    from modules.gemini_client import ask_gemini
except ImportError:
    def ask_gemini(prompt): return "Error: Gemini module not found."

class VideoProject:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.projects_dir = os.path.join(self.base_dir, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        
    def create_project_folder(self, title):
        project_dir = os.path.join(self.projects_dir, title)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "audio"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "images"), exist_ok=True)
        return project_dir

    def create_new_project_manual(self):
        print("\n🎬 新規動画プロジェクト作成 (手動入力)")
        title = input("プロジェクト名を入力: ").strip()
        if not title: return
        
        project_dir = self.create_project_folder(title)
        print("台本作成モードに入ります。「終了」と入力するまで続けてください。\n")
        
        script_data = []
        line_num = 1
        while True:
            text = input(f"[{line_num:03}] 台本: ").strip()
            if text == "終了": break
            if not text: continue
            script_data.append({"id": line_num, "text": text, "audio_file": f"{line_num:03}_voice.wav"})
            line_num += 1
            
        self.save_project(project_dir, script_data)

    def create_new_project_ai(self):
        print("\n🤖 AI 台本生成 (Zundamon Style)")
        title = input("プロジェクト名を入力: ").strip()
        if not title: return
        project_dir = self.create_project_folder(title)
        
        topic = input("動画のテーマ・内容を入力してください: ").strip()
        if not topic: return
        
        prompt = f"""
        You are a popular Video Script Writer for 'Zundamon' (Voicevox character).
        Character: Zundamon (Ends sentences with 'なのだ', 'のだ', slightly sassy but cute).
        Topic: {topic}
        
        Write a short script (5-10 lines).
        Output strictly in JSON format:
        [
          {{"text": "Line 1 text"}},
          {{"text": "Line 2 text"}}
        ]
        """
        
        print("\n🧠 AIが台本を執筆中... (数秒お待ちください)")
        try:
            response = ask_gemini(prompt)
            # Basic cleanup to ensure JSON parsing
            json_str = response.strip().replace("```json", "").replace("```", "")
            ai_lines = json.loads(json_str)
            
            script_data = []
            for i, line in enumerate(ai_lines):
                script_data.append({
                    "id": i+1, 
                    "text": line['text'], 
                    "audio_file": f"{i+1:03}_voice.wav"
                })
            
            self.save_project(project_dir, script_data)
            print(f"\n✅ AI台本が完成しました！ ({len(script_data)}行)")
            
        except Exception as e:
            print(f"❌ AI生成エラー: {e}")

    def save_project(self, project_dir, script_data):
        script_path = os.path.join(project_dir, "script.json")
        with open(script_path, "w", encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
            
        txt_path = os.path.join(project_dir, "voicevox_text.txt")
        with open(txt_path, "w", encoding='utf-8') as f:
            for item in script_data:
                f.write(f"{item['text']}\n")
        
        print(f"✅ プロジェクト保存完了: {project_dir}")

    def generate_slides(self):
        self.list_projects()
        p_name = input("スライド生成するプロジェクト名を入力: ").strip()
        project_dir = os.path.join(self.projects_dir, p_name)
        
        if not os.path.exists(project_dir):
            print("❌ プロジェクトが見つかりません")
            return

        script_path = os.path.join(project_dir, "script.json")
        if not os.path.exists(script_path):
            print("❌ script.json が見つかりません")
            return
            
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
            
        print("\n🖼️ スライド画像を生成中...")
        try:
            # Font settings (Default to simple Arial or similar if Meiryo not found, but try standard Win font)
            font_path = "C:\\Windows\\Fonts\\meiryo.ttc"
            font_size = 60
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            for item in script_data:
                # 1920x1080 Background
                bg_color = (random.randint(20, 50), random.randint(20, 50), random.randint(40, 80)) # Dark Blue-ish
                img = Image.new('RGB', (1920, 1080), color=bg_color)
                draw = ImageDraw.Draw(img)
                
                # Draw Text (Centered rough est)
                text = item['text']
                # Simple word wrap logic could go here, but for now simple center
                draw.text((960, 540), text, font=font, fill=(255, 255, 255), anchor="mm")
                
                # Zundamon Icon Placeholder (Green Circle)
                draw.ellipse((50, 800, 250, 1000), fill=(100, 200, 100))
                draw.text((150, 900), "ずんだ", font=font, fill=(0,0,0), anchor="mm")
                
                save_path = os.path.join(project_dir, "images", f"{item['id']:03}.png")
                img.save(save_path)
                print(f"  Saved: {save_path}")
                
            print("\n✅ 全スライド生成完了！動画編集ソフトにドラッグ＆ドロップで使えます。")
            
        except Exception as e:
            print(f"❌ 画像生成エラー: {e}")

    def list_projects(self):
        projects = [d for d in os.listdir(self.projects_dir) if os.path.isdir(os.path.join(self.projects_dir, d))]
        if not projects:
            print("プロジェクトはありません。")
            return
        print("\n📂 既存のプロジェクト:")
        for idx, p in enumerate(projects):
            print(f"  - {p}")

def main():
    studio = VideoProject()
    while True:
        print("\n╔════════════════════════════════════╗")
        print("║      🎥 VECTIS VIDEO STUDIO        ║")
        print("╚════════════════════════════════════╝")
        print(" [1] 🎬 新規台本作成 (手動)")
        print(" [2] 🤖 AI 台本生成 (ずんだもん)")
        print(" [3] 🖼️ 自動スライド生成 (映像素材)")
        print(" [4] プロジェクト一覧")
        print(" [Q] 終了")
        
        choice = input("\nSelect > ").strip().lower()
        if choice == 'q': break
        elif choice == '1': studio.create_new_project_manual()
        elif choice == '2': studio.create_new_project_ai()
        elif choice == '3': studio.generate_slides()
        elif choice == '4': studio.list_projects()

if __name__ == "__main__":
    main()
