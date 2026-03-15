import { useState, useEffect, useCallback } from 'react';
import {
  Youtube,
  Sparkles,
  Copy,
  Download,
  History,
  X,
  AlertCircle,
  CheckCircle,
  Loader2,
  Clock,
  Trash2,
  FileText,
  Link as LinkIcon,
  Book
} from 'lucide-react';
import { GoogleGenerativeAI } from '@google/generative-ai';
import './App.css';

// Types
interface SummaryHistory {
  id: string;
  url: string;
  videoId: string;
  title: string;
  summary: string;
  timestamp: Date;
}

// Utility to extract YouTube video ID
const extractVideoId = (url: string): string | null => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)/,
    /^([a-zA-Z0-9_-]{11})$/
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
};

// Load API key from file or localStorage
const loadApiKey = async (): Promise<string | null> => {
  // First check localStorage
  const storedKey = localStorage.getItem('gemini_api_key');
  if (storedKey) return storedKey;

  // Try to fetch from gemini_key.txt
  try {
    const response = await fetch('/gemini_key.txt');
    if (response.ok) {
      const key = await response.text();
      const trimmedKey = key.trim();
      if (trimmedKey) {
        localStorage.setItem('gemini_api_key', trimmedKey);
        return trimmedKey;
      }
    }
  } catch (e) {
    console.log('Could not load API key from file');
  }

  return null;
};

// YouTube Transcript API (simulated)
const fetchTranscript = async (videoId: string): Promise<string> => {
  const response = await fetch(
    `https://www.youtube.com/watch?v=${videoId}`
  );

  if (!response.ok) {
    throw new Error('動画の情報を取得できませんでした');
  }

  // Extract video title from HTML
  const html = await response.text();
  const titleMatch = html.match(/<title>([^<]+)<\/title>/);
  const title = titleMatch ? titleMatch[1].replace(' - YouTube', '') : 'Unknown';

  return `VIDEO_TITLE: ${title}\nVIDEO_ID: ${videoId}`;
};

function App() {
  const [url, setUrl] = useState('');
  const [videoId, setVideoId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [videoTitle, setVideoTitle] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState<SummaryHistory[]>([]);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [showApiInput, setShowApiInput] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [pediaMode, setPediaMode] = useState(true); // Default to Pedia Mode

  // Load history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('youtube_summary_history');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setHistory(parsed.map((h: SummaryHistory) => ({
          ...h,
          timestamp: new Date(h.timestamp)
        })));
      } catch (e) {
        console.error('Failed to load history');
      }
    }
  }, []);

  // Load API key
  useEffect(() => {
    loadApiKey().then(key => {
      setApiKey(key);
      if (!key) {
        setShowApiInput(true);
      }
    });
  }, []);

  // Save history to localStorage
  const saveHistory = useCallback((newHistory: SummaryHistory[]) => {
    localStorage.setItem('youtube_summary_history', JSON.stringify(newHistory));
    setHistory(newHistory);
  }, []);

  // Handle URL input change
  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUrl(value);
    setError(null);

    const extracted = extractVideoId(value);
    setVideoId(extracted);
  };

  // Handle API key save
  const handleApiKeySave = () => {
    if (apiKeyInput.trim()) {
      localStorage.setItem('gemini_api_key', apiKeyInput.trim());
      setApiKey(apiKeyInput.trim());
      setShowApiInput(false);
    }
  };

  // Summarize video
  const handleSummarize = async () => {
    if (!videoId) {
      setError('有効なYouTube URLを入力してください');
      return;
    }

    if (!apiKey) {
      setShowApiInput(true);
      setError('Gemini APIキーを設定してください');
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);

    try {
      // Initialize Gemini
      const genAI = new GoogleGenerativeAI(apiKey);
      const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

      // Create prompt for summarization
      const prompt = `
あなたは優秀な動画要約アシスタントです。以下のYouTube動画を分析し、日本語で詳細な要約を作成してください。
出力は「自分ペディア」に追加するためのMarkdown形式で作成してください。

YouTube動画URL: https://www.youtube.com/watch?v=${videoId}

## 要約の形式

### 📌 概要
（動画の主題を2-3文で簡潔に説明）

### 🎯 主要ポイント
- ポイント1
- ポイント2
- ポイント3
（重要なポイントを箇条書きで）

### 📝 詳細内容
（動画の詳細な内容を段落で説明。重要な引用や数字があれば含める）

### 💡 キーテイクアウェイ
（視聴者が覚えておくべき重要な学び3-5つ）

### 🏷️ カテゴリ・タグ
（動画のカテゴリや関連キーワード）

---
動画の内容を正確に要約し、視聴者が動画を見なくても主要な情報を理解できるようにしてください。
`;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      setSummary(text);
      setVideoTitle(`YouTube動画 (${videoId})`);

      // Save to history
      const newEntry: SummaryHistory = {
        id: Date.now().toString(),
        url: url,
        videoId: videoId,
        title: `YouTube動画 (${videoId})`,
        summary: text,
        timestamp: new Date()
      };

      saveHistory([newEntry, ...history.slice(0, 49)]); // Keep last 50

      // Auto-save to Pedia file if mode is active (Simulated via download for now, as browser can't write directly to disk without permission)
      if (pediaMode) {
        // In a real app, this would append to a file via File System Access API or backend
        console.log("Pedia Mode: Content ready to be appended.");
      }

    } catch (err) {
      console.error('Summarization error:', err);
      setError(
        err instanceof Error
          ? `要約に失敗しました: ${err.message}`
          : '要約に失敗しました。もう一度お試しください。'
      );
    } finally {
      setLoading(false);
    }
  };

  // Copy summary to clipboard
  const handleCopy = async () => {
    if (summary) {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Download as text file (Pedia Style Append)
  const handleDownload = () => {
    if (summary) {
      const dateStr = new Date().toISOString().split('T')[0];
      const pediaHeader = `\n## [${dateStr}] ${videoTitle}\n- Source: ${url}\n\n`;
      const content = pediaHeader + summary + "\n\n---";
      
      const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
      const urlObj = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlObj;
      a.download = `Self_Pedia_Append_${videoId}.md`; // Suggesting append
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(urlObj);
    }
  };

  // Load from history
  const handleHistoryClick = (item: SummaryHistory) => {
    setUrl(item.url);
    setVideoId(item.videoId);
    setSummary(item.summary);
    setVideoTitle(item.title);
    setHistoryOpen(false);
  };

  // Delete from history
  const handleHistoryDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    saveHistory(history.filter(h => h.id !== id));
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">
              <Youtube />
            </div>
            <div>
              <div className="logo-text">YouTube 自分ペディア</div>
              <div className="logo-subtitle">Knowledge Base Generator</div>
            </div>
          </div>

          <div className="header-actions">
             <div className="pedia-toggle" onClick={() => setPediaMode(!pediaMode)}>
                <Book size={18} color={pediaMode ? 'var(--accent-blue)' : 'var(--text-muted)'} />
                <span style={{fontSize: '0.8rem', color: pediaMode ? 'var(--text-main)' : 'var(--text-muted)'}}>
                  {pediaMode ? '自分ペディアモード ON' : '追記モード OFF'}
                </span>
             </div>
            <button className="history-toggle" onClick={() => setHistoryOpen(true)}>
              <History size={20} />
              履歴
              {history.length > 0 && (
                <span className="history-badge">{history.length}</span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* API Key Input */}
        {showApiInput && (
          <div className="input-section">
            <h2 className="input-title">
              <Sparkles size={24} />
              Gemini APIキーを設定
            </h2>
            <div className="input-wrapper">
              <input
                type="password"
                className="url-input"
                placeholder="Gemini APIキーを入力..."
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
              />
              <button
                className="summarize-btn"
                onClick={handleApiKeySave}
                disabled={!apiKeyInput.trim()}
              >
                <CheckCircle size={20} />
                保存
              </button>
            </div>
            <p style={{ marginTop: '12px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              ※ APIキーは<a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener" style={{ color: 'var(--accent-blue)' }}>Google AI Studio</a>で取得できます
            </p>
          </div>
        )}

        {/* URL Input Section */}
        <div className="input-section">
          <h2 className="input-title">
            <LinkIcon size={24} />
            YouTube動画を知識に追加
          </h2>
          <div className="input-wrapper">
            <input
              type="text"
              className="url-input"
              placeholder="YouTube URLを貼り付け... (例: https://youtube.com/watch?v=xxxxx)"
              value={url}
              onChange={handleUrlChange}
              onKeyDown={(e) => e.key === 'Enter' && handleSummarize()}
            />
            <button
              className={`summarize-btn ${loading ? 'loading' : ''}`}
              onClick={handleSummarize}
              disabled={loading || !videoId}
            >
              {loading ? (
                <>
                  <Loader2 size={20} />
                  分析中...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  ペディアに追加
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-state">
            <AlertCircle size={24} />
            <span className="error-text">{error}</span>
          </div>
        )}

        {/* Video Preview */}
        {videoId && !loading && (
          <div className="video-preview">
            <div className="video-container">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
            <div className="video-info">
              <div className="video-title">
                <Youtube size={18} />
                {videoTitle || 'YouTube動画'}
              </div>
              <div className="video-url">{url}</div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="summary-section">
            <div className="loading-state">
              <div className="loading-spinner" />
              <div className="loading-text">AIが知識を抽出しています...</div>
              <div className="loading-dots">
                <div className="loading-dot" />
                <div className="loading-dot" />
                <div className="loading-dot" />
              </div>
            </div>
          </div>
        )}

        {/* Summary Display */}
        {summary && !loading && (
          <div className="summary-section">
            <div className="summary-header">
              <h3 className="summary-title">
                <Book size={22} />
                {pediaMode ? '自分ペディア用エントリー' : '要約結果'}
              </h3>
              <div className="summary-actions">
                <button
                  className={`action-btn ${copied ? 'copied' : ''}`}
                  onClick={handleCopy}
                >
                  {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
                  {copied ? 'コピー完了!' : 'コピー'}
                </button>
                <button className="action-btn" onClick={handleDownload}>
                  <Download size={18} />
                  {pediaMode ? '追記用保存' : '保存'}
                </button>
              </div>
            </div>
            <div className="summary-content">
              {summary.split('\n').map((line, i) => {
                if (line.startsWith('### ')) {
                  return <h3 key={i}>{line.replace('### ', '')}</h3>;
                } else if (line.startsWith('## ')) {
                  return <h2 key={i}>{line.replace('## ', '')}</h2>;
                } else if (line.startsWith('# ')) {
                  return <h1 key={i}>{line.replace('# ', '')}</h1>;
                } else if (line.startsWith('- ')) {
                  return <li key={i}>{line.replace('- ', '')}</li>;
                } else if (line.trim() === '') {
                  return <br key={i} />;
                } else if (line.startsWith('---')) {
                  return <hr key={i} style={{ borderColor: 'var(--border-color)', margin: '20px 0' }} />;
                } else {
                  return <p key={i}>{line}</p>;
                }
              })}
            </div>
          </div>
        )}
      </main>

      {/* History Panel Overlay */}
      <div
        className={`history-overlay ${historyOpen ? 'visible' : ''}`}
        onClick={() => setHistoryOpen(false)}
      />

      {/* History Panel */}
      <aside className={`history-panel ${historyOpen ? 'open' : ''}`}>
        <div className="history-header">
          <h3 className="history-title">
            <Clock size={20} />
            知識履歴
          </h3>
          <button className="close-btn" onClick={() => setHistoryOpen(false)}>
            <X size={24} />
          </button>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <div className="history-empty">
              <History size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
              <p>まだ履歴がありません</p>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className="history-item"
                onClick={() => handleHistoryClick(item)}
              >
                <div className="history-item-title">{item.title}</div>
                <div className="history-item-date">
                  <Clock size={14} />
                  {new Date(item.timestamp).toLocaleDateString('ja-JP', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
                <button
                  className="history-item-delete"
                  onClick={(e) => handleHistoryDelete(item.id, e)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Footer */}
      <footer className="footer">
        YouTube 自分ペディア Generator © 2026 - VECTIS OS Suite
      </footer>
    </div>
  );
}

export default App;