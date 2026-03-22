import * as SecureStore from 'expo-secure-store';

/**
 * qumi Secure Vault Service
 * 各薬味（MCPサーバー）の情報をデバイス内で安全に管理します。
 */

export interface McpConfig {
  id: number;
  label: string;
  endpoint: string;
  apiKey: string;
  type: 'google' | 'custom' | 'local';
}

const VAULT_KEY_PREFIX = 'qumi_yakumi_';

export const saveYakumiConfig = async (config: McpConfig) => {
  try {
    const data = JSON.stringify(config);
    await SecureStore.setItemAsync(`${VAULT_KEY_PREFIX}${config.id}`, data);
    return true;
  } catch (error) {
    console.error('Vault Save Error:', error);
    return false;
  }
};

export const getYakumiConfig = async (id: number): Promise<McpConfig | null> => {
  try {
    const data = await SecureStore.getItemAsync(`${VAULT_KEY_PREFIX}${id}`);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Vault Read Error:', error);
    return null;
  }
};

export const deleteYakumiConfig = async (id: number) => {
  await SecureStore.deleteItemAsync(`${VAULT_KEY_PREFIX}${id}`);
};
