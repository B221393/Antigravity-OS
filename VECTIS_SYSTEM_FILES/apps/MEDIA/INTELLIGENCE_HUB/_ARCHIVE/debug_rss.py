
import urllib.request
import urllib.error

ids = {
    "Newspicks Candidate 1": "UCfTnJmRQP79C4y_BMF_XrlA",
}

for name, cid in ids.items():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    print(f"\nTesting {name}: {cid}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            print(f"Success! Status: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Failed with code: {e.code}")
    except Exception as e:
        print(f"Failed with error: {e}")
