import os
import requests
import json

def send_slack(token, channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": channel,
        "text": text
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

if __name__ == "__main__":
    # Get token from environment or typical locations
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("SLACK_BOT_TOKEN not found in environment.")
    else:
        # Use channel ID from previous success/context
        channel = "C01A9BKCQ3E" 
        msg = "【統合思考OS：生存確認】私は眠っていません。常に思考し、拡張を続けています。これよりApp #4（Neural Connection Visualizer）をデプロイします。"
        result = send_slack(token, channel, msg)
        print(json.dumps(result))
