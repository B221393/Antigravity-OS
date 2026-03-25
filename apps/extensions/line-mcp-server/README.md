# line-mcp-server

LINE Messaging API を操作するための MCP サーバーです。  
ローカル利用を想定した `stdio` トランスポートで動作します。

## 機能

- `line_health_check`  
  `LINE_CHANNEL_ACCESS_TOKEN` の有無と、`/v2/bot/info` への疎通を確認します。

- `line_push_message`  
  `userId` / `groupId` / `roomId` に対してテキストメッセージを push 送信します。

- `line_get_profile`  
  指定 `userId` のプロフィールを取得します。

## 必要環境

- Node.js 20+
- LINE Messaging API の Channel Access Token

## セットアップ

```bash
cd apps/extensions/line-mcp-server
npm install
npm run build
```

## 起動

```bash
set LINE_CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN
node dist/index.js
```

PowerShell の場合:

```powershell
$env:LINE_CHANNEL_ACCESS_TOKEN="YOUR_LINE_CHANNEL_ACCESS_TOKEN"
node dist/index.js
```

## MCPクライアント設定例

```json
{
  "mcpServers": {
    "line": {
      "command": "node",
      "args": [
        "C:\\Users\\Yuto\\desktop\\app\\apps\\extensions\\line-mcp-server\\dist\\index.js"
      ],
      "env": {
        "LINE_CHANNEL_ACCESS_TOKEN": "YOUR_LINE_CHANNEL_ACCESS_TOKEN"
      }
    }
  }
}
```
