import os
import urllib.request
import zipfile
import shutil

# Config
DOWNLOAD_URL = "https://download.kiwix.org/release/kiwix-tools/kiwix-tools_windows-x86_64.zip"
TARGET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
TEMP_ZIP = "kiwix_tools.zip"

def setup():
    print(f"Downloading Kiwix Tools from {DOWNLOAD_URL}...")
    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, TEMP_ZIP)
        print("Download complete.")
    except Exception as e:
        print(f"Download failed: {e}")
        return

    print("Extracting...")
    try:
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            # Extract to temp folder first
            zip_ref.extractall("temp_extract")
            
        # Find the inner folder (often named kiwix-tools_windows-x86_64-x.y.z)
        extracted_root = "temp_extract"
        inner_folder = os.listdir(extracted_root)[0]
        inner_path = os.path.join(extracted_root, inner_folder)
        
        # Move executables to bin
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)
            
        for item in os.listdir(inner_path):
            s = os.path.join(inner_path, item)
            d = os.path.join(TARGET_DIR, item)
            if os.path.isfile(s): # Move files (exe)
                shutil.copy2(s, d)
                
        print(f"Instalation successful! Binaries are in {TARGET_DIR}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")
    finally:
        # Cleanup
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)
        if os.path.exists("temp_extract"):
            shutil.rmtree("temp_extract")

if __name__ == "__main__":
    setup()
