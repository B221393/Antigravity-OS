import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, ScrollView, TouchableOpacity,
  SafeAreaView, StatusBar, Dimensions, Modal, TextInput,
  Alert, ActivityIndicator, KeyboardAvoidingView, Platform,
  Keyboard,
} from 'react-native';
import {
  Bot, Book, Camera, Map, Mail, Calendar,
  Settings, Zap, Shield, Cpu, Share2, Music,
  X, Save, Lock, Link, Link2Off, ChevronRight,
  Send, MessageSquare, ChevronDown, Sparkles,
} from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  FadeIn, FadeOut, SlideInUp, SlideOutDown,
  useSharedValue, useAnimatedStyle, withSpring, withTiming,
} from 'react-native-reanimated';
import { saveYakumiConfig, getYakumiConfig } from './src/services/vault';
import { testConnection } from './src/services/mcpClient';
import { routeCommand, executeCommand, AgentResult } from './src/services/agentLogic';
import { PulseGlow, NotificationBadge, ProcessingOverlay, ChatBubbleAnimated } from './src/components/ActionFeedback';

const { width, height } = Dimensions.get('window');
const COLUMN_WIDTH = (width - 48) / 3;

// ─── チャットメッセージ型 ─────────────────────────
interface ChatMessage {
  id: string;
  type: 'user' | 'system' | 'result';
  text: string;
  slotLabel?: string;
  slotId?: number;
  slotColor?: string;
  timestamp: Date;
  executionTime?: number;
  success?: boolean;
}

// ─── メインアプリ ─────────────────────────────────
export default function App() {
  // 既存state
  const [selectedYakumi, setSelectedYakumi] = useState<any>(null);
  const [endpoint, setEndpoint] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [registry, setRegistry] = useState<Record<number, boolean>>({});
  const [testing, setTesting] = useState(false);
  const [lastCheck, setLastCheck] = useState<Record<number, boolean>>({});

  // 新規: チャットUI state
  const [chatVisible, setChatVisible] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      type: 'system',
      text: 'qumi 起動完了。コマンドを入力してください。\n例: 「牛乳を買うメモを追加して」',
      timestamp: new Date(),
    },
  ]);
  const [processingSlot, setProcessingSlot] = useState<number | null>(null);
  const [completedSlots, setCompletedSlots] = useState<Record<number, boolean>>({});

  const scrollRef = useRef<ScrollView>(null);
  const chatScrollRef = useRef<ScrollView>(null);

  // ─── 薬味定義 ──────────────────────────────────
  const yakumis = [
    { id: 1, icon: Bot, label: 'AI MEMO', color: '#FF3B30' },
    { id: 2, icon: Book, label: 'KNOWLEDGE', color: '#FF9500' },
    { id: 3, icon: Zap, label: 'IOWN', color: '#FFCC00' },
    { id: 4, icon: Shield, label: 'SECURITY', color: '#4CD964' },
    { id: 5, icon: Map, label: 'G-MAPS', color: '#5AC8FA' },
    { id: 6, icon: Camera, label: 'VISION', color: '#007AFF' },
    { id: 7, icon: Cpu, label: 'AGENT', color: '#5856D6' },
    { id: 8, icon: Calendar, label: 'SCHEDULE', color: '#AF52DE' },
    { id: 9, icon: Mail, label: 'G-MAIL', color: '#FF2D55' },
    { id: 10, icon: Music, label: 'SOUND', color: '#8E8E93' },
    { id: 11, icon: Share2, label: 'NETWORK', color: '#00FF99' },
    { id: 12, icon: Settings, label: 'CONFIG', color: '#FFFFFF' },
  ];

  // ─── 初期化 ────────────────────────────────────
  useEffect(() => {
    const initRegistry = async () => {
      const reg: any = {};
      for (const y of yakumis) {
        const config = await getYakumiConfig(y.id);
        reg[y.id] = !!config;
      }
      setRegistry(reg);
    };
    initRegistry();
  }, []);

  // ─── 完了バッジの自動消去 ──────────────────────
  useEffect(() => {
    const entries = Object.entries(completedSlots).filter(([, v]) => v);
    if (entries.length > 0) {
      const timer = setTimeout(() => {
        setCompletedSlots({});
      }, 3500);
      return () => clearTimeout(timer);
    }
  }, [completedSlots]);

  // ─── 既存: スロット設定画面 ────────────────────
  const handleOpenSlot = async (yakumi: any) => {
    const config = await getYakumiConfig(yakumi.id);
    setSelectedYakumi(yakumi);
    setEndpoint(config?.endpoint || '');
    setApiKey(config?.apiKey || '');
  };

  const handleTestAndSave = async () => {
    if (!selectedYakumi) return;
    setTesting(true);

    if (!endpoint) {
      setTesting(false);
      Alert.alert('Error', 'Endpoint URLを入力してください。');
      return;
    }

    const isAlive = await testConnection(endpoint, apiKey);

    const success = await saveYakumiConfig({
      id: selectedYakumi.id,
      label: selectedYakumi.label,
      endpoint,
      apiKey,
      type: 'custom',
    });

    setTesting(false);
    if (success) {
      setRegistry({ ...registry, [selectedYakumi.id]: true });
      setLastCheck({ ...lastCheck, [selectedYakumi.id]: isAlive });

      if (isAlive) {
        Alert.alert('Connected!', `${selectedYakumi.label} との連携に成功しました。`);
        setSelectedYakumi(null);
      } else {
        Alert.alert('Saved (Offline)', '設定は保存されましたが、サーバーからの応答がありません。');
      }
    }
  };

  // ─── 新規: コマンド実行ハンドラー ─────────────
  const handleSendCommand = async () => {
    const input = commandInput.trim();
    if (!input) return;

    Keyboard.dismiss();

    // ユーザーメッセージ追加
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      text: input,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setCommandInput('');

    // ルーティング解析
    const route = routeCommand(input);

    if (route) {
      const yakumi = yakumis.find(y => y.id === route.slotId);

      // ルーティング通知
      const routeMsg: ChatMessage = {
        id: `route-${Date.now()}`,
        type: 'system',
        text: `🌶️ ${route.slotLabel} にルーティング中...`,
        slotLabel: route.slotLabel,
        slotId: route.slotId,
        slotColor: yakumi?.color,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, routeMsg]);

      // パルス発光開始
      setProcessingSlot(route.slotId);

      // コマンド実行
      const result = await executeCommand(input);

      // パルス発光停止
      setProcessingSlot(null);

      // 完了バッジ表示
      setCompletedSlots(prev => ({ ...prev, [route.slotId]: true }));

      // 結果メッセージ
      const resultMsg: ChatMessage = {
        id: `result-${Date.now()}`,
        type: 'result',
        text: result.success
          ? `✅ ${result.slotLabel} 完了 (${result.executionTime}ms)\n${JSON.stringify(result.data, null, 2)}`
          : `❌ ${result.slotLabel} エラー: ${result.error}`,
        slotLabel: result.slotLabel,
        slotId: result.slotId,
        slotColor: yakumi?.color,
        timestamp: new Date(),
        executionTime: result.executionTime,
        success: result.success,
      };
      setMessages(prev => [...prev, resultMsg]);
    } else {
      // ルーティング失敗
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'system',
        text: '⚠️ コマンドを解析できませんでした。\n「メモを追加」「G-MAPSで検索」などの形式で試してください。',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    }

    // スクロール
    setTimeout(() => {
      chatScrollRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  // ─── ヘルパー: スロットの色を取得 ─────────────
  const getSlotColor = (slotId?: number) => {
    if (!slotId) return '#444';
    return yakumis.find(y => y.id === slotId)?.color || '#444';
  };

  // ─── レンダリング ──────────────────────────────
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* ═══ ヘッダー ═══ */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>qumi</Text>
          <Text style={styles.headerSubtitle}>Personal MCP Registry</Text>
        </View>
        <View style={styles.headerRight}>
          <View style={styles.liveCounter}>
            <Link size={12} color="#00FF99" style={{ marginRight: 4 }} />
            <Text style={styles.liveText}>
              {Object.values(lastCheck).filter(v => v).length} ACTIVE
            </Text>
          </View>
        </View>
      </View>

      {/* ═══ 薬味グリッド ═══ */}
      <ScrollView contentContainerStyle={styles.grid} ref={scrollRef}>
        <View style={styles.yakumiWrapper}>
          {yakumis.map((yakumi) => (
            <TouchableOpacity
              key={yakumi.id}
              style={styles.slotContainer}
              onPress={() => handleOpenSlot(yakumi)}
              activeOpacity={0.7}
            >
              <PulseGlow
                isActive={processingSlot === yakumi.id}
                color={yakumi.color}
              >
                <LinearGradient
                  colors={[yakumi.color + '33', yakumi.color + '05']}
                  style={[
                    styles.slotIcon,
                    registry[yakumi.id] && { borderColor: yakumi.color, borderWidth: 2 },
                    lastCheck[yakumi.id] && styles.activePulse,
                  ]}
                >
                  <yakumi.icon size={28} color={registry[yakumi.id] ? yakumi.color : '#222'} />
                  {registry[yakumi.id] && (
                    <View style={[styles.statusIndicator, { backgroundColor: lastCheck[yakumi.id] ? '#00FF99' : '#444' }]} />
                  )}
                </LinearGradient>
                <NotificationBadge
                  visible={!!completedSlots[yakumi.id]}
                  color={yakumi.color}
                />
              </PulseGlow>
              <Text style={[styles.slotLabel, registry[yakumi.id] && { color: '#FFF' }]}>{yakumi.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* ═══ 処理中インジケーター ═══ */}
      {processingSlot && (
        <ProcessingOverlay
          visible={true}
          slotLabel={yakumis.find(y => y.id === processingSlot)?.label || ''}
          color={yakumis.find(y => y.id === processingSlot)?.color || '#FFF'}
        />
      )}

      {/* ═══ コマンド入力バー（常時表示） ═══ */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        <View style={styles.commandBar}>
          {/* チャット展開ボタン */}
          <TouchableOpacity
            style={styles.chatToggle}
            onPress={() => setChatVisible(!chatVisible)}
          >
            <MessageSquare size={18} color={chatVisible ? '#00FF99' : '#444'} />
          </TouchableOpacity>

          {/* 入力フィールド */}
          <View style={styles.inputContainer}>
            <Sparkles size={14} color="#333" style={{ marginRight: 8 }} />
            <TextInput
              style={styles.commandInput}
              placeholder="コマンドを入力... 「牛乳を買うメモを追加して」"
              placeholderTextColor="#222"
              value={commandInput}
              onChangeText={setCommandInput}
              onSubmitEditing={handleSendCommand}
              returnKeyType="send"
              autoCorrect={false}
            />
          </View>

          {/* 送信ボタン */}
          <TouchableOpacity
            style={[
              styles.sendButton,
              commandInput.trim() ? styles.sendButtonActive : null,
            ]}
            onPress={handleSendCommand}
            disabled={!commandInput.trim() || !!processingSlot}
          >
            {processingSlot ? (
              <ActivityIndicator size="small" color="#00FF99" />
            ) : (
              <Send size={18} color={commandInput.trim() ? '#000' : '#333'} />
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      {/* ═══ チャットパネル（展開時） ═══ */}
      <Modal visible={chatVisible} animationType="slide" transparent>
        <View style={styles.chatOverlay}>
          <View style={styles.chatPanel}>
            {/* チャットヘッダー */}
            <View style={styles.chatHeader}>
              <View style={styles.chatHeaderLeft}>
                <Sparkles size={18} color="#00FF99" />
                <Text style={styles.chatHeaderTitle}>Agent Log</Text>
              </View>
              <TouchableOpacity onPress={() => setChatVisible(false)}>
                <ChevronDown size={24} color="#666" />
              </TouchableOpacity>
            </View>

            {/* メッセージリスト */}
            <ScrollView
              ref={chatScrollRef}
              style={styles.chatMessages}
              contentContainerStyle={styles.chatMessagesContent}
              onContentSizeChange={() => chatScrollRef.current?.scrollToEnd({ animated: true })}
            >
              {messages.map((msg, index) => (
                <ChatBubbleAnimated key={msg.id} index={index}>
                  {msg.type === 'user' ? (
                    <View style={styles.userBubble}>
                      <Text style={styles.userBubbleText}>{msg.text}</Text>
                      <Text style={styles.bubbleTime}>
                        {msg.timestamp.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
                      </Text>
                    </View>
                  ) : msg.type === 'result' ? (
                    <View style={[styles.resultBubble, { borderLeftColor: msg.slotColor || '#444' }]}>
                      <View style={styles.resultHeader}>
                        <View style={[styles.resultDot, { backgroundColor: msg.slotColor }]} />
                        <Text style={[styles.resultSlotLabel, { color: msg.slotColor }]}>
                          {msg.slotLabel}
                        </Text>
                        {msg.executionTime && (
                          <Text style={styles.resultTime}>{msg.executionTime}ms</Text>
                        )}
                      </View>
                      <Text style={styles.resultText}>{msg.text}</Text>
                      <Text style={styles.bubbleTime}>
                        {msg.timestamp.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
                      </Text>
                    </View>
                  ) : (
                    <View style={styles.systemBubble}>
                      <Text style={styles.systemText}>{msg.text}</Text>
                    </View>
                  )}
                </ChatBubbleAnimated>
              ))}
            </ScrollView>

            {/* チャット内コマンド入力 */}
            <View style={styles.chatInputBar}>
              <TextInput
                style={styles.chatInput}
                placeholder="何をしましょうか？"
                placeholderTextColor="#222"
                value={commandInput}
                onChangeText={setCommandInput}
                onSubmitEditing={handleSendCommand}
                returnKeyType="send"
              />
              <TouchableOpacity
                style={[
                  styles.chatSendButton,
                  commandInput.trim() ? styles.chatSendButtonActive : null,
                ]}
                onPress={handleSendCommand}
                disabled={!commandInput.trim() || !!processingSlot}
              >
                {processingSlot ? (
                  <ActivityIndicator size="small" color="#00FF99" />
                ) : (
                  <Send size={16} color={commandInput.trim() ? '#000' : '#333'} />
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* ═══ 連携設定モーダル（既存） ═══ */}
      <Modal visible={!!selectedYakumi} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <View style={styles.modalTitleRow}>
                {selectedYakumi && <selectedYakumi.icon size={24} color={selectedYakumi?.color} />}
                <Text style={[styles.modalTitle, { color: selectedYakumi?.color, marginLeft: 12 }]}>
                  {selectedYakumi?.label} 連携設定
                </Text>
              </View>
              <TouchableOpacity onPress={() => setSelectedYakumi(null)}>
                <X color="#666" size={24} />
              </TouchableOpacity>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>ENDPOINT (HTTPS/WSS)</Text>
              <TextInput
                style={styles.input}
                placeholder="https://idx-mcp-server..."
                placeholderTextColor="#333"
                value={endpoint}
                onChangeText={setEndpoint}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>AUTHORIZATION TOKEN</Text>
              <TextInput
                style={styles.input}
                secureTextEntry
                placeholder="Bearer / API Key"
                placeholderTextColor="#333"
                value={apiKey}
                onChangeText={setApiKey}
              />
            </View>

            <TouchableOpacity
              style={[styles.saveButton, { backgroundColor: selectedYakumi?.color }]}
              onPress={handleTestAndSave}
              disabled={testing}
            >
              {testing ? (
                <ActivityIndicator color="#000" />
              ) : (
                <>
                  <Link size={20} color="#000" />
                  <Text style={styles.saveButtonText}>TEST & INTEGRATE</Text>
                </>
              )}
            </TouchableOpacity>

            <View style={styles.securityBox}>
              <Lock size={14} color="#00FF99" />
              <Text style={styles.securityText}>
                このデバイスの Secure Vault にのみ保存されます。
              </Text>
            </View>
          </View>
        </View>
      </Modal>

      {/* ═══ フッター ═══ */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>Integrating 12 Flavors of Cloud & Local Agents</Text>
      </View>
    </SafeAreaView>
  );
}

// ─── スタイルシート ───────────────────────────────
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },

  // ─ ヘッダー ─
  header: {
    padding: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#111',
  },
  headerTitle: {
    color: '#FFF',
    fontSize: 36,
    fontWeight: '900',
    letterSpacing: -2,
  },
  headerSubtitle: {
    color: '#444',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  headerRight: {
    alignItems: 'flex-end',
    gap: 8,
  },
  liveCounter: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#001105',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#003311',
  },
  liveText: {
    color: '#00FF99',
    fontSize: 10,
    fontWeight: '900',
  },

  // ─ グリッド ─
  grid: {
    padding: 12,
  },
  yakumiWrapper: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  slotContainer: {
    width: COLUMN_WIDTH,
    height: 130,
    margin: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  slotIcon: {
    width: 75,
    height: 75,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#080808',
    borderWidth: 1,
    borderColor: '#111',
    marginBottom: 10,
    position: 'relative',
  },
  statusIndicator: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    width: 14,
    height: 14,
    borderRadius: 7,
    borderWidth: 3,
    borderColor: '#000',
  },
  activePulse: {
    shadowColor: '#FFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
  },
  slotLabel: {
    color: '#333',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1,
    textAlign: 'center',
  },

  // ─ コマンドバー（常時表示） ─
  commandBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#111',
    backgroundColor: '#050505',
    gap: 8,
  },
  chatToggle: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#0A0A0A',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#1A1A1A',
  },
  inputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0A0A0A',
    borderRadius: 12,
    paddingHorizontal: 14,
    height: 44,
    borderWidth: 1,
    borderColor: '#1A1A1A',
  },
  commandInput: {
    flex: 1,
    color: '#FFF',
    fontSize: 14,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#111',
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonActive: {
    backgroundColor: '#00FF99',
  },

  // ─ チャットパネル ─
  chatOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  chatPanel: {
    height: height * 0.7,
    backgroundColor: '#050505',
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    borderTopWidth: 1,
    borderTopColor: '#1A1A1A',
    overflow: 'hidden',
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#111',
  },
  chatHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  chatHeaderTitle: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '800',
    letterSpacing: 1,
  },
  chatMessages: {
    flex: 1,
  },
  chatMessagesContent: {
    padding: 16,
    paddingBottom: 8,
  },

  // ─ メッセージバブル ─
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#1A1A1A',
    borderRadius: 16,
    borderBottomRightRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 10,
    maxWidth: '80%',
    borderWidth: 1,
    borderColor: '#222',
  },
  userBubbleText: {
    color: '#FFF',
    fontSize: 14,
    lineHeight: 20,
  },
  systemBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#080808',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 10,
    maxWidth: '85%',
    borderWidth: 1,
    borderColor: '#111',
  },
  systemText: {
    color: '#666',
    fontSize: 13,
    lineHeight: 20,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  resultBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#080808',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 10,
    maxWidth: '85%',
    borderLeftWidth: 3,
    borderWidth: 1,
    borderColor: '#111',
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 6,
  },
  resultDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  resultSlotLabel: {
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 1,
  },
  resultTime: {
    color: '#333',
    fontSize: 10,
    fontWeight: '700',
    marginLeft: 'auto',
  },
  resultText: {
    color: '#888',
    fontSize: 12,
    lineHeight: 18,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  bubbleTime: {
    color: '#222',
    fontSize: 9,
    fontWeight: '700',
    marginTop: 6,
    textAlign: 'right',
  },

  // ─ チャット入力 ─
  chatInputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#111',
    gap: 8,
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#0A0A0A',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 44,
    color: '#FFF',
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#1A1A1A',
  },
  chatSendButton: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#111',
    alignItems: 'center',
    justifyContent: 'center',
  },
  chatSendButtonActive: {
    backgroundColor: '#00FF99',
  },

  // ─ 設定モーダル（既存） ─
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.95)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#0A0A0A',
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    padding: 32,
    borderTopWidth: 1,
    borderTopColor: '#222',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 40,
  },
  modalTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '900',
    letterSpacing: 1,
  },
  inputGroup: {
    marginBottom: 28,
  },
  inputLabel: {
    color: '#444',
    fontSize: 10,
    fontWeight: '900',
    marginBottom: 12,
    letterSpacing: 2,
  },
  input: {
    backgroundColor: '#050505',
    borderBottomWidth: 2,
    borderBottomColor: '#222',
    padding: 16,
    color: '#FFF',
    fontSize: 16,
    fontFamily: 'monospace',
  },
  saveButton: {
    padding: 20,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 10,
  },
  saveButtonText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 15,
    marginLeft: 12,
    letterSpacing: 1,
  },
  securityBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 32,
    opacity: 0.5,
  },
  securityText: {
    color: '#00FF99',
    fontSize: 10,
    fontWeight: '700',
    marginLeft: 8,
  },

  // ─ フッター ─
  footer: {
    padding: 8,
    alignItems: 'center',
  },
  footerText: {
    color: '#111',
    fontSize: 9,
    fontWeight: '800',
    letterSpacing: 2,
  },
});
