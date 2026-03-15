import sys
import os

# Try to import playwright, if fails, return instructions
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAIL = True
except ImportError:
    PLAYWRIGHT_AVAIL = False

class PlaywrightScraper:
    def __init__(self, headless=True):
        self.headless = headless

    def fetch_page_text(self, url, wait_ms=3000):
        if not PLAYWRIGHT_AVAIL:
            return "[SYSTEM] Playwright is not installed. Run 'setup_playwright.bat' to enable advanced scraping."

        try:
            with sync_playwright() as p:
                # Launch browser
                # Note: Chromium logic
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                print(f"Navigating to {url}...")
                try:
                    page.goto(url, timeout=60000, wait_until='domcontentloaded')
                except Exception as e:
                    print(f"[WARN] Navigation timeout/error: {e}")
                
                # Dynamic wait
                page.wait_for_timeout(wait_ms)
                
                # Special handling for X (Twitter) scroll
                if "x.com" in url or "twitter.com" in url:
                    page.mouse.wheel(0, 5000)
                    page.wait_for_timeout(2000)
                
                # Robust extraction with retries
                content = ""
                title = ""
                for attempt in range(3):
                    try:
                        title = page.title()
                        content = page.evaluate("document.body.innerText")
                        break
                    except Exception as e:
                        print(f"[WARN] Content extraction failed (attempt {attempt+1}): {e}")
                        page.wait_for_timeout(1000)

                browser.close()
                return f"Title: {title}\n\n{content}"
                
        except Exception as e:
            return f"[ERROR] Playwright Fetch Failed: {e}"

    def capture_screenshot(self, url, output_path, wait_ms=3000):
        if not PLAYWRIGHT_AVAIL:
            return False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()
                
                print(f"📸 Snapshotting: {url}...")
                page.goto(url, timeout=60000)
                page.wait_for_timeout(wait_ms)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                page.screenshot(path=output_path)
                browser.close()
                return True
                
        except Exception as e:
            print(f"[ERROR] Screenshot Failed: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright_scraper.py <url>")
    else:
        scraper = PlaywrightScraper()
        print(scraper.fetch_page_text(sys.argv[1]))
