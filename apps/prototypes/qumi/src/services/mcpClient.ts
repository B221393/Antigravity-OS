import { McpConfig, getYakumiConfig } from './vault';

/**
 * qumi MCP Client Service
 * 登録された設定を使用して、外部MCPサーバーと通信します。
 */

export interface McpResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export const callMcpServer = async (id: number, method: string, params: any = {}): Promise<McpResponse> => {
  const config = await getYakumiConfig(id);
  
  if (!config || !config.endpoint) {
    return { success: false, error: 'Config not found' };
  }

  try {
    const response = await fetch(config.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Qumi-Device-ID': 'local-vault-device', // デバイス識別子
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method,
        params,
        id: Date.now(),
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const result = await response.json();
    return { success: true, data: result };
  } catch (error: any) {
    console.error(`MCP Call Error [${config.label}]:`, error);
    return { success: false, error: error.message };
  }
};

/**
 * 接続確認テスト
 */
export const testConnection = async (endpoint: string, apiKey: string): Promise<boolean> => {
  try {
    const response = await fetch(endpoint, {
      method: 'OPTIONS', // またはサーバーが提供する health check
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });
    return response.status === 200;
  } catch (error) {
    // 実際にはサーバーの実装に合わせて調整が必要ですが、
    // fetchが通るか（エンドポイントが生きているか）を確認します
    return false;
  }
};
