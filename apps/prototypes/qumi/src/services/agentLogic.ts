import { callMcpServer } from './mcpClient';

/**
 * qumi Agent Logic - インテリジェント・ルーター
 * 
 * 自然言語の入力を解析し、適切なMCPスロット（薬味）とメソッドを
 * 自動選択して実行する軽量AIルーター。
 * 
 * 設計思想: 
 *   LLMに依存せず、キーワードマッチングとパターン解析で
 *   高速かつ確実なルーティングを実現する。
 */

// ─── スロット定義 ─────────────────────────────────
export interface SlotRoute {
  slotId: number;
  slotLabel: string;
  method: string;
  params: Record<string, any>;
  confidence: number; // 0-1: マッチの確信度
}

// ─── ルーティングルール定義 ─────────────────────────
interface RoutingRule {
  slotId: number;
  slotLabel: string;
  keywords: string[];
  patterns: RegExp[];
  method: string;
  paramExtractor: (input: string) => Record<string, any>;
}

const ROUTING_RULES: RoutingRule[] = [
  // 🌶️ 1. AI MEMO
  {
    slotId: 1,
    slotLabel: 'AI MEMO',
    keywords: ['メモ', 'memo', '記録', '追加', 'ノート', '覚え', 'note', 'remember', '書いて', '書き留め'],
    patterns: [
      /(.+)を?(メモ|記録|追加|覚え|書いて|ノート)/i,
      /(メモ|memo|note).*(追加|作成|書い)/i,
      /add.*(memo|note)/i,
      /remember\s+(.+)/i,
    ],
    method: 'add_memo',
    paramExtractor: (input: string) => {
      // 「〇〇をメモして」→ title: 〇〇
      const match = input.match(/(.+?)を?(メモ|記録|追加|覚え|書いて|ノート|note|memo)/i);
      const content = match ? match[1].trim() : input;
      return {
        title: content.substring(0, 50),
        content: content,
      };
    },
  },
  // 📚 2. KNOWLEDGE
  {
    slotId: 2,
    slotLabel: 'KNOWLEDGE',
    keywords: ['調べ', '検索', 'search', '知り', '教え', 'what', 'how', 'なに', '知識', 'knowledge'],
    patterns: [
      /(.+)を?(調べ|検索|教え|知り)/i,
      /(search|find|look up)\s+(.+)/i,
      /(what|how|why)\s+(.+)/i,
    ],
    method: 'search_knowledge',
    paramExtractor: (input: string) => {
      const match = input.match(/(.+?)を?(調べ|検索|教え|知り)/i);
      return { query: match ? match[1].trim() : input };
    },
  },
  // ⚡ 3. IOWN (高速処理)
  {
    slotId: 3,
    slotLabel: 'IOWN',
    keywords: ['計算', '分析', 'analyze', 'calculate', 'compute', '処理', 'process'],
    patterns: [
      /(計算|分析|処理).*(.+)/i,
      /(analyze|calculate|compute|process)\s+(.+)/i,
    ],
    method: 'process_data',
    paramExtractor: (input: string) => ({ data: input }),
  },
  // 🛡️ 4. SECURITY
  {
    slotId: 4,
    slotLabel: 'SECURITY',
    keywords: ['セキュリティ', 'パスワード', '暗号', 'security', 'password', 'encrypt', '安全'],
    patterns: [
      /(パスワード|暗号|セキュリティ|security|password)/i,
    ],
    method: 'security_check',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // 📍 5. G-MAPS
  {
    slotId: 5,
    slotLabel: 'G-MAPS',
    keywords: ['地図', 'マップ', 'map', '場所', '住所', 'ルート', '道', '行き方', 'G-MAPS', 'gmap', '近く', 'navigate'],
    patterns: [
      /(.+)を?(地図|マップ|場所|map)/i,
      /(G-MAPS|gmap|map).*(で|を使って|using).*(.+)/i,
      /(.+)(への|まで|の)(行き方|ルート|道順|道)/i,
      /(.+)(の?(近く|周辺|付近))/i,
    ],
    method: 'search_location',
    paramExtractor: (input: string) => {
      const match = input.match(/(.+?)を?(地図|マップ|場所|map|検索)/i)
        || input.match(/(.+?)(への|まで|の)(行き方|ルート)/i);
      return { query: match ? match[1].trim() : input };
    },
  },
  // 📸 6. VISION
  {
    slotId: 6,
    slotLabel: 'VISION',
    keywords: ['写真', 'カメラ', '撮影', 'photo', 'camera', '画像', 'image', 'scan', 'スキャン'],
    patterns: [
      /(写真|カメラ|撮影|photo|camera|画像|scan|スキャン)/i,
    ],
    method: 'capture_vision',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // 🤖 7. AGENT
  {
    slotId: 7,
    slotLabel: 'AGENT',
    keywords: ['エージェント', 'agent', '自動', 'auto', '実行', 'run', 'タスク', 'task'],
    patterns: [
      /(エージェント|agent|自動|auto).*(実行|run|start)/i,
      /(タスク|task).*(実行|作成|追加)/i,
    ],
    method: 'run_agent_task',
    paramExtractor: (input: string) => ({ task: input }),
  },
  // 📅 8. SCHEDULE
  {
    slotId: 8,
    slotLabel: 'SCHEDULE',
    keywords: ['予定', 'スケジュール', 'schedule', 'カレンダー', 'calendar', '予約', '会議', 'meeting'],
    patterns: [
      /(予定|スケジュール|schedule|calendar).*(追加|確認|表示)/i,
      /(予約|会議|meeting).*(追加|入れ|設定)/i,
    ],
    method: 'manage_schedule',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // 📧 9. G-MAIL
  {
    slotId: 9,
    slotLabel: 'G-MAIL',
    keywords: ['メール', 'mail', 'email', '送信', 'send', '受信', 'inbox', 'gmail'],
    patterns: [
      /(メール|mail|email).*(送|確認|読|チェック)/i,
      /(送信|send)\s+(.+)/i,
    ],
    method: 'manage_mail',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // 🎵 10. SOUND
  {
    slotId: 10,
    slotLabel: 'SOUND',
    keywords: ['音楽', '再生', 'play', 'music', '曲', 'song', 'sound', '音'],
    patterns: [
      /(音楽|曲|music|song).*(再生|play|流|かけ)/i,
      /(再生|play)\s+(.+)/i,
    ],
    method: 'control_sound',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // 🌐 11. NETWORK
  {
    slotId: 11,
    slotLabel: 'NETWORK',
    keywords: ['ネットワーク', 'network', '接続', 'connect', '共有', 'share', 'sync', '同期'],
    patterns: [
      /(ネットワーク|network|接続|connect|共有|share|同期|sync)/i,
    ],
    method: 'network_action',
    paramExtractor: (input: string) => ({ action: input }),
  },
  // ⚙️ 12. CONFIG
  {
    slotId: 12,
    slotLabel: 'CONFIG',
    keywords: ['設定', '変更', 'config', 'setting', 'change', 'update', '構成'],
    patterns: [
      /(設定|config|setting).*(変更|更新|表示|開)/i,
    ],
    method: 'manage_config',
    paramExtractor: (input: string) => ({ action: input }),
  },
];

// ─── メイン・ルーティング関数 ─────────────────────
export const routeCommand = (input: string): SlotRoute | null => {
  const normalized = input.toLowerCase().trim();

  if (!normalized || normalized.length === 0) {
    return null;
  }

  let bestMatch: SlotRoute | null = null;
  let highestScore = 0;

  for (const rule of ROUTING_RULES) {
    let score = 0;

    // 1. キーワードマッチング (各キーワード: +0.3)
    const keywordHits = rule.keywords.filter(kw => normalized.includes(kw.toLowerCase()));
    score += keywordHits.length * 0.3;

    // 2. パターンマッチング (各パターン: +0.5) — より強い信号
    const patternHits = rule.patterns.filter(p => p.test(normalized));
    score += patternHits.length * 0.5;

    // スコアが閾値を超え、かつ最高スコアなら採用
    if (score > 0.2 && score > highestScore) {
      highestScore = score;
      bestMatch = {
        slotId: rule.slotId,
        slotLabel: rule.slotLabel,
        method: rule.method,
        params: rule.paramExtractor(input),
        confidence: Math.min(score, 1.0),
      };
    }
  }

  return bestMatch;
};

// ─── コマンド実行関数 ─────────────────────────────
export interface AgentResult {
  success: boolean;
  slotLabel: string;
  slotId: number;
  method: string;
  data?: any;
  error?: string;
  executionTime: number;
}

export const executeCommand = async (input: string): Promise<AgentResult> => {
  const startTime = Date.now();
  const route = routeCommand(input);

  if (!route) {
    return {
      success: false,
      slotLabel: 'SYSTEM',
      slotId: 0,
      method: 'unknown',
      error: 'コマンドを解析できませんでした。もう少し具体的に入力してください。',
      executionTime: Date.now() - startTime,
    };
  }

  // MCPサーバーへ送信
  const response = await callMcpServer(route.slotId, route.method, route.params);

  return {
    success: response.success,
    slotLabel: route.slotLabel,
    slotId: route.slotId,
    method: route.method,
    data: response.data,
    error: response.error,
    executionTime: Date.now() - startTime,
  };
};
