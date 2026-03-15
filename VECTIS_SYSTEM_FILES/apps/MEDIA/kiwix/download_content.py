import os
import urllib.request
import re

# Config
BASE_URL = "https://download.kiwix.org/zim/wiktionary/"
TARGET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library")

def get_latest_zim_url():
    print(f"Scanning {BASE_URL} for Japanese Wiktionary...")
    try:
        with urllib.request.urlopen(BASE_URL) as response:
            html = response.read().decode('utf-8')
            
        # Regex to find wiktionary_ja_all_nopic_YYYY-MM.zim
        # Example: wiktionary_ja_all_nopic_2023-10.zim
        pattern = r'href="(wiktionary_ja_all_nopic_\d{4}-\d{2}\.zim)"'
        matches = re.findall(pattern, html)
        
        if not matches:
            print("No matches found.")
            return None
            
        # Sort to get latest
        matches.sort()
        latest_file = matches[-1]
        
        return BASE_URL + latest_file, latest_file
        
    except Exception as e:
        print(f"Error scanning index: {e}")
        return None

def download_zim():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    result = get_latest_zim_url()
    if not result:
        print("Could not find a ZIM file to download.")
        return
        
    url, filename = result
    dest_path = os.path.join(TARGET_DIR, filename)
    
    if os.path.exists(dest_path):
        print(f"File {filename} already exists. Skipping download.")
        return

    print(f"Downloading {filename}...")
    print(f"Source: {url}")
    print("This may take a few minutes (approx 500MB-1GB)...")
    
    try:
        # Download with simple progress hook
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = downloaded * 100 / total_size
                if block_num % 1000 == 0:
                    print(f"\rProgress: {percent:.1f}% ({downloaded//1024//1024}MB / {total_size//1024//1024}MB)", end="")
        
        urllib.request.urlretrieve(url, dest_path, reporthook=progress)
        print("\nDownload complete!")
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        # Clean up partial
        if os.path.exists(dest_path):
            os.remove(dest_path)

if __name__ == "__main__":
    download_zim()
