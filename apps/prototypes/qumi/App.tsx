import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions, Modal, TextInput, Alert, ActivityIndicator } from 'react-native';
import { 
  Bot, Book, Camera, Map, Mail, Calendar, 
  Settings, Zap, Shield, Cpu, Share2, Music, X, Save, Lock, Link, Link2Off, ChevronRight
} from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { saveYakumiConfig, getYakumiConfig } from './src/services/vault';
import { testConnection } from './src/services/mcpClient';

const { width } = Dimensions.get('window');
const COLUMN_WIDTH = (width - 48) / 3;

export default function App() {
  const [selectedYakumi, setSelectedYakumi] = useState<any>(null);
  const [endpoint, setEndpoint] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [registry, setRegistry] = useState<Record<number, boolean>>({});
  const [testing, setTesting] = useState(false);
  const [lastCheck, setLastCheck] = useState<Record<number, boolean>>({});

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

  const handleOpenSlot = async (yakumi: any) => {
    const config = await getYakumiConfig(yakumi.id);
    setSelectedYakumi(yakumi);
    setEndpoint(config?.endpoint || '');
    setApiKey(config?.apiKey || '');
  };

  const handleTestAndSave = async () => {
    if (!selectedYakumi) return;
    setTesting(true);
    
    // エンドポイントが空の場合は保存のみ
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
      type: 'custom'
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>qumi</Text>
          <Text style={styles.headerSubtitle}>Personal MCP Registry</Text>
        </View>
        <View style={styles.liveCounter}>
          <Link size={12} color="#00FF99" style={{ marginRight: 4 }} />
          <Text style={styles.liveText}>
            {Object.values(lastCheck).filter(v => v).length} ACTIVE
          </Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.grid}>
        <View style={styles.yakumiWrapper}>
          {yakumis.map((yakumi) => (
            <TouchableOpacity 
              key={yakumi.id} 
              style={styles.slotContainer}
              onPress={() => handleOpenSlot(yakumi)}
            >
              <LinearGradient
                colors={[yakumi.color + '33', yakumi.color + '05']}
                style={[
                  styles.slotIcon, 
                  registry[yakumi.id] && { borderColor: yakumi.color, borderWidth: 2 },
                  lastCheck[yakumi.id] && styles.activePulse
                ]}
              >
                <yakumi.icon size={28} color={registry[yakumi.id] ? yakumi.color : '#222'} />
                {registry[yakumi.id] && (
                  <View style={[styles.statusIndicator, { backgroundColor: lastCheck[yakumi.id] ? '#00FF99' : '#444' }]} />
                )}
              </LinearGradient>
              <Text style={[styles.slotLabel, registry[yakumi.id] && { color: '#FFF' }]}>{yakumi.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* Connection / Settings Modal */}
      <Modal visible={!!selectedYakumi} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <View style={styles.modalTitleRow}>
                <selectedYakumi.icon size={24} color={selectedYakumi?.color} />
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

      <View style={styles.footer}>
        <Text style={styles.footerText}>Integrating 12 Flavors of Cloud & Local Agents</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  header: { padding: 24, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#111' },
  headerTitle: { color: '#FFF', fontSize: 36, fontWeight: '900', letterSpacing: -2 },
  headerSubtitle: { color: '#444', fontSize: 11, fontWeight: '700', textTransform: 'uppercase' },
  liveCounter: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#001105', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 4, borderWidth: 1, borderColor: '#003311' },
  liveText: { color: '#00FF99', fontSize: 10, fontWeight: '900' },
  grid: { padding: 12 },
  yakumiWrapper: { flexDirection: 'row', flexWrap: 'wrap' },
  slotContainer: { width: COLUMN_WIDTH, height: 130, margin: 8, alignItems: 'center', justifyContent: 'center' },
  slotIcon: { width: 75, height: 75, borderRadius: 24, alignItems: 'center', justifyContent: 'center', backgroundColor: '#080808', borderWidth: 1, borderColor: '#111', marginBottom: 10, position: 'relative' },
  statusIndicator: { position: 'absolute', bottom: -2, right: -2, width: 14, height: 14, borderRadius: 7, borderSize: 3, borderColor: '#000' },
  activePulse: { shadowColor: '#FFF', shadowOffset: { width: 0, height: 0 }, shadowOpacity: 0.5, shadowRadius: 10, elevation: 10 },
  slotLabel: { color: '#333', fontSize: 10, fontWeight: '800', letterSpacing: 1, textAlign: 'center' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.95)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#0A0A0A', borderTopLeftRadius: 32, borderTopRightRadius: 32, padding: 32, borderTopWidth: 1, borderTopColor: '#222' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 40 },
  modalTitleRow: { flexDirection: 'row', alignItems: 'center' },
  modalTitle: { fontSize: 20, fontWeight: '900', letterSpacing: 1 },
  inputGroup: { marginBottom: 28 },
  inputLabel: { color: '#444', fontSize: 10, fontWeight: '900', marginBottom: 12, letterSpacing: 2 },
  input: { backgroundColor: '#050505', borderBottomWidth: 2, borderBottomColor: '#222', padding: 16, color: '#FFF', fontSize: 16, fontFamily: 'monospace' },
  saveButton: { padding: 20, borderRadius: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginTop: 10 },
  saveButtonText: { color: '#000', fontWeight: '900', fontSize: 15, marginLeft: 12, letterSpacing: 1 },
  securityBox: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginTop: 32, opacity: 0.5 },
  securityText: { color: '#00FF99', fontSize: 10, fontWeight: '700', marginLeft: 8 },
  footer: { padding: 20, alignItems: 'center' },
  footerText: { color: '#111', fontSize: 9, fontWeight: '800', letterSpacing: 2 }
});
