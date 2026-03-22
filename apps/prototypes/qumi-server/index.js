const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

// インメモリ・データベース（ここにローカル保存される）
let memos = [
  { id: 1, title: "初期メモ", content: "ローカルMCPサーバーが起動しました。", date: new Date().toISOString() }
];

/**
 * MCP Tool Definition: add_memo
 * 軽量AIでも理解できるよう、引数はシンプルに。
 */
const add_memo = (title, content) => {
  const newMemo = {
    id: Date.now(),
    title,
    content,
    date: new Date().toISOString()
  };
  memos.push(newMemo);
  console.log(`[MCP] Memo Added: ${title}`);
  return newMemo;
};

/**
 * MCP Tool Definition: get_memos
 */
const get_memos = () => {
  return memos;
};

// API エンドポイント (qumi アプリからの接続用)
app.get('/memos', (req, res) => {
  res.json(get_memos());
});

app.post('/mcp', (req, res) => {
  const { method, params } = req.body;
  
  console.log(`[MCP Request] Method: ${method}`);

  if (method === 'add_memo') {
    const result = add_memo(params.title, params.content);
    return res.json({ success: true, result });
  }

  if (method === 'get_memos') {
    const result = get_memos();
    return res.json({ success: true, result });
  }

  res.status(404).json({ error: 'Method not found' });
});

app.listen(port, () => {
  console.log(`
  🌶️ qumi Local MCP Server
  ------------------------
  Endpoint: http://localhost:${port}/mcp
  Status:   RUNNING
  
  AIからの命令をローカルで受け付ける準備が整いました。
  `);
});
