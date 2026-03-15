
import urllib.request
import re

video_id = "qyegi8_FD-w"
url = f"https://www.youtube.com/watch?v={video_id}"

print(f"Fetching video page: {url}")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # Look for channelId
        # "channelId":"UC..."
        match = re.search(r'"channelId":"(UC[\w-]+)"', html)
        if match:
            print(f"FOUND Channel ID: {match.group(1)}")
        else:
            # Try itemprop
            match = re.search(r'<meta itemprop="channelId" content="(UC[\w-]+)">', html)
            if match:
                print(f"FOUND Channel ID (meta): {match.group(1)}")
            else:
                print("ID not found in video page.")
                
except Exception as e:
    print(f"Error: {e}")
