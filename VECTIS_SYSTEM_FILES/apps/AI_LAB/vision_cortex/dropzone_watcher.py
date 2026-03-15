import time
import os
import shutil
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Assuming ocr_service is in the same directory or importable
# For now, we'll placeholder the import and integration
try:
    from .ocr_service import image_to_markdown
except ImportError:
    # Handle case where script is run directly vs module
    import sys
    sys.path.append(str(Path(__file__).parent))
    from ocr_service import image_to_markdown

DROPZONE_DIR = Path.home() / "Desktop" / "OCR_DROPZONE"
PROCESSED_DIR = DROPZONE_DIR / "processed"

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if filepath.suffix.lower() not in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']:
            return

        # Wait a brief moment for file write to complete
        time.sleep(1)
        self.process_image(filepath)

    def process_image(self, filepath):
        print(f"Detected new image: {filepath.name}")
        try:
            # Generate Markdown
            markdown_content = image_to_markdown(filepath)
            
            # Save Markdown side-by-side (or in the same folder)
            md_filename = filepath.stem + ".md"
            md_path = filepath.parent / md_filename
            
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            print(f"Generated Markdown: {md_filename}")

            # Optional: Move image to processed folder to keep dropzone clean
            # shutil.move(str(filepath), str(PROCESSED_DIR / filepath.name))

        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")

def start_watching():
    if not DROPZONE_DIR.exists():
        DROPZONE_DIR.mkdir(parents=True)
    
    if not PROCESSED_DIR.exists():
        PROCESSED_DIR.mkdir(parents=True)

    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(DROPZONE_DIR), recursive=False)
    observer.start()
    print(f"OCR Dropzone Watcher started at: {DROPZONE_DIR}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
