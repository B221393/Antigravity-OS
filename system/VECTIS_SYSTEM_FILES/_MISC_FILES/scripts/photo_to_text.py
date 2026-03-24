import os
import sys
import time

# Add modules path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, BASE_DIR)

from modules.gemini_client import GenerativeModel

def extract_text_from_image(image_path):
    print(f"👀 Analyzing: {os.path.basename(image_path)}...")
    
    try:
        model = GenerativeModel('gemini-2.0-flash-exp')
        
        # Determine mime type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/jpeg"
        if ext == ".png": mime_type = "image/png"
        if ext == ".webp": mime_type = "image/webp"
        
        # Read image data
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        prompt = """
        この画像に含まれるテキストを**完全に書き起こして**ください。
        
        【指示】
        - 構造（見出し、箇条書き）を維持すること。
        - 手書き文字も可能な限り読み取ること。
        - 余計な解説は不要。テキストのみを出力すること。
        """
        
        response = model.generate_content([prompt, {"mime_type": mime_type, "data": image_data}])
        return response.text
        
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("画像をドラッグ＆ドロップしてください。")
        input("Press Enter to exit...")
        sys.exit()
        
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print("ファイルが見つかりません。")
        sys.exit()

    # --- Organization Logic ---
    import shutil
    from datetime import datetime
    
    # Define Storage Paths
    DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data", "OCR"))
    IMG_DIR = os.path.join(DATA_DIR, "IMAGES")
    TXT_DIR = os.path.join(DATA_DIR, "TEXTS")
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(TXT_DIR, exist_ok=True)
    
    # Generate Timestamped Filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = os.path.basename(image_path)
    base_name, ext = os.path.splitext(original_name)
    
    new_image_name = f"{timestamp}_{base_name}{ext}"
    new_text_name = f"{timestamp}_{base_name}.txt"
    
    dest_image_path = os.path.join(IMG_DIR, new_image_name)
    dest_text_path = os.path.join(TXT_DIR, new_text_name)
    
    # Copy Image to Storage
    print(f"📦 画像を保管庫に移動中: {dest_image_path}")
    shutil.copy2(image_path, dest_image_path)
    
    # Analyze (Use the copy)
    result = extract_text_from_image(dest_image_path)
    
    print("\n" + "="*50)
    print("📝 抽出結果:")
    print("="*50 + "\n")
    print(result)
    print("\n" + "="*50)
    
    # Copy to clipboard
    try:
        import pyperclip
        pyperclip.copy(result)
        print("📋 クリップボードにコピーしました！")
    except:
        pass
        
    # Save to file
    with open(dest_text_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"💾 テキストを保存しました: {dest_text_path}")
    
    # Open the folder for the user
    try:
        os.startfile(TXT_DIR)
    except:
        pass
        
    input("\n終了するにはEnterキーを押してください...")
