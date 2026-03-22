import React, { useState, useEffect } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, Alert, TextInput
} from 'react-native';
import { Lock, Unlock, Shield, Terminal as TerminalIcon, Cpu, Database } from 'lucide-react-native';
import * as SecureStore from 'expo-secure-store';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withSequence,
  withTiming, Easing, withSpring
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');

// ─── 1. セキュリティ機能 (機密データの完全分離) ────────────
const CONFIDENTIAL_KEY = 'user_secret_data';

// ─── 2. ゲームロジック ──────────────────────────────────
const COLORS = ['#FF3B30', '#00FF99', '#5AC8FA', '#FFCC00'];

export default function App() {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [sequence, setSequence] = useState<number[]>([]);
  const [playerInput, setPlayerInput] = useState<number[]>([]);
  const [secretData, setSecretData] = useState<string>('まだ機密情報はありません。');
  const [newSecret, setNewSecret] = useState('');

  // アニメーション用
  const lockShake = useSharedValue(0);
  const pulseScale = useSharedValue(1);

  useEffect(() => {
    // ランダムな4つの正解シーケンスを生成（ゲームの初期化）
    initGame();
    // SecureStoreから保存された機密情報を読み込む
    loadSecret();

    // 鼓動アニメーション（ゲームらしく）
    pulseScale.value = withRepeat(
      withSequence(
        withTiming(1.05, { duration: 800, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 800, easing: Easing.inOut(Easing.ease) })
      ),
      -1, true
    );
  }, []);

  const initGame = () => {
    const newSeq = Array.from({ length: 4 }, () => Math.floor(Math.random() * COLORS.length));
    setSequence(newSeq);
  };

  const loadSecret = async () => {
    const data = await SecureStore.getItemAsync(CONFIDENTIAL_KEY);
    if (data) setSecretData(data);
  };

  const saveSecret = async () => {
    if (!newSecret.trim()) return;
    // 極秘情報をデバイスのSecureStore（KeyChain等）に安全に保存する
    await SecureStore.setItemAsync(CONFIDENTIAL_KEY, newSecret);
    setSecretData(newSecret);
    setNewSecret('');
    Alert.alert('暗号化保管完了', '機密情報がデバイスの極秘領域に保存されました。GitHub等には絶対に上がりません。');
  };

  const handleNodePress = (index: number) => {
    const currentStep = playerInput.length;
    
    // 不正解の場合：シェイクアニメーションしてリセット
    if (index !== sequence[currentStep]) {
      lockShake.value = withSequence(
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      setPlayerInput([]);
      Alert.alert('HACK FAILED', 'アクセスが拒否されました。パターンが違います。');
      return;
    }

    const nextInput = [...playerInput, index];
    setPlayerInput(nextInput);

    // 全て正解した場合
    if (nextInput.length === sequence.length) {
      setIsUnlocked(true);
    }
  };

  const lockStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: lockShake.value }]
  }));

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }]
  }));

  // ──────────────────────────────────────────────────────────
  // 画面1: サイバー・ハッキング・ゲーム（公開ロジック）
  // ──────────────────────────────────────────────────────────
  if (!isUnlocked) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />
        
        <View style={styles.gameHeader}>
          <Shield color="#FF3B30" size={32} />
          <Text style={styles.title}>VECTIS FIREWALL</Text>
          <Text style={styles.subtitle}>// UNAUTHORIZED ACCESS DETECTED //</Text>
        </View>

        <Animated.View style={[styles.lockContainer, lockStyle]}>
          <Lock color="#444" size={80} />
          <Text style={styles.lockText}>RESTRICTED VAULT</Text>
          <Text style={styles.hintText}>
            機密領域にアクセスするには、このセッションのバイパス・シーケンス（4つの色）を推理してください。
          </Text>
        </Animated.View>

        <View style={styles.progressRow}>
          {Array.from({ length: 4 }).map((_, i) => (
            <View key={i} style={[
              styles.progressDot, 
              i < playerInput.length ? { backgroundColor: COLORS[playerInput[i]], borderColor: COLORS[playerInput[i]] } : {}
            ]} />
          ))}
        </View>

        <View style={styles.nodeGrid}>
          {COLORS.map((color, index) => (
            <TouchableOpacity 
              key={index}
              activeOpacity={0.6}
              onPress={() => handleNodePress(index)}
              style={styles.nodeWrapper}
            >
              <LinearGradient
                colors={[`${color}44`, `${color}11`]}
                style={[styles.node, { borderColor: color }]}
              >
                <Cpu color={color} size={32} />
              </LinearGradient>
            </TouchableOpacity>
          ))}
        </View>
        
        {/* チート：テスト用に正解を表示（本来は消す） */}
        <Text style={styles.cheatText}>
          DEBUG BYPASS: {sequence.map(i => COLORS[i] === '#FF3B30' ? '赤' : COLORS[i] === '#00FF99' ? '緑' : COLORS[i] === '#5AC8FA' ? '青' : '黄').join(' > ')}
        </Text>
      </SafeAreaView>
    );
  }

  // ──────────────────────────────────────────────────────────
  // 画面2: 機密領域（セキュリティ機能実証）
  // ──────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={styles.unlockedContainer}>
      <StatusBar barStyle="light-content" />
      
      <Animated.View style={[styles.unlockedHeader, pulseStyle]}>
        <Unlock color="#00FF99" size={48} />
        <Text style={styles.unlockedTitle}>ACCESS GRANTED</Text>
        <Text style={styles.unlockedSubtitle}>Welcome back, Admin.</Text>
      </Animated.View>

      <View style={styles.secretBox}>
        <View style={styles.secretBoxHeader}>
          <Database color="#00FF99" size={18} />
          <Text style={styles.secretBoxTitle}>DEVICE SECURE STORE (極秘領域)</Text>
        </View>
        <Text style={styles.secretDataText}>
          {secretData}
        </Text>
        <Text style={styles.secretNotice}>
          ※このデータはメモリ上とiPhone内部の暗号化領域（Keychain）にのみ存在し、GitHubには絶対にアップロードされません。
        </Text>
      </View>

      <View style={styles.inputSection}>
        <TerminalIcon color="#00FF99" size={18} style={{ marginBottom: 8 }} />
        <TextInput 
          style={styles.input}
          placeholder="新しい機密情報（パスワードやAPIキーなど）を入力..."
          placeholderTextColor="#444"
          value={newSecret}
          onChangeText={setNewSecret}
          secureTextEntry
        />
        <TouchableOpacity style={styles.saveButton} onPress={saveSecret}>
          <Text style={styles.saveButtonText}>暗号化してローカルに保存</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.lockButton} onPress={() => {
        setIsUnlocked(false);
        setPlayerInput([]);
        initGame(); // ロック時にシーケンスを変更
      }}>
        <Lock color="#FFF" size={16} />
        <Text style={styles.lockButtonText}>VAULT を再ロックする</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505', alignItems: 'center' },
  gameHeader: { alignItems: 'center', marginTop: 60, marginBottom: 40 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 4, marginTop: 12 },
  subtitle: { color: '#FF3B30', fontSize: 10, fontWeight: '700', letterSpacing: 2, marginTop: 4 },
  
  lockContainer: { alignItems: 'center', marginBottom: 40, padding: 20 },
  lockText: { color: '#444', fontSize: 18, fontWeight: '900', letterSpacing: 2, marginTop: 16 },
  hintText: { color: '#666', fontSize: 12, textAlign: 'center', marginTop: 16, paddingHorizontal: 40, lineHeight: 20 },
  
  progressRow: { flexDirection: 'row', gap: 16, marginBottom: 60 },
  progressDot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: '#333', backgroundColor: 'transparent' },
  
  nodeGrid: { flexDirection: 'row', flexWrap: 'wrap', width: width * 0.8, justifyContent: 'center', gap: 16 },
  nodeWrapper: { width: '45%', aspectRatio: 1 },
  node: { flex: 1, borderRadius: 24, borderWidth: 2, alignItems: 'center', justifyContent: 'center' },
  
  cheatText: { color: '#222', fontSize: 10, position: 'absolute', bottom: 40, fontFamily: 'monospace' },

  unlockedContainer: { flex: 1, backgroundColor: '#001A0A', padding: 24 },
  unlockedHeader: { alignItems: 'center', marginTop: 60, marginBottom: 40 },
  unlockedTitle: { color: '#00FF99', fontSize: 32, fontWeight: '900', letterSpacing: 2, marginTop: 16 },
  unlockedSubtitle: { color: '#FFF', fontSize: 14, fontWeight: '800', opacity: 0.8 },
  
  secretBox: { backgroundColor: '#000', borderWidth: 1, borderColor: '#00FF99', borderRadius: 16, padding: 24, marginBottom: 40 },
  secretBoxHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, borderBottomWidth: 1, borderBottomColor: '#113311', paddingBottom: 12, marginBottom: 16 },
  secretBoxTitle: { color: '#00FF99', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  secretDataText: { color: '#FFF', fontSize: 16, fontWeight: '700', fontFamily: 'monospace', marginBottom: 20 },
  secretNotice: { color: '#00FF99', fontSize: 10, lineHeight: 16, opacity: 0.6 },
  
  inputSection: { marginTop: 'auto', marginBottom: 24 },
  input: { backgroundColor: '#000', borderWidth: 1, borderColor: '#113311', borderRadius: 12, padding: 16, color: '#FFF', fontFamily: 'monospace', marginBottom: 16 },
  saveButton: { backgroundColor: '#00FF99', padding: 16, borderRadius: 12, alignItems: 'center' },
  saveButtonText: { color: '#000', fontWeight: '900', fontSize: 14 },
  
  lockButton: { flexDirection: 'row', backgroundColor: '#FF3B30', padding: 16, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
  lockButtonText: { color: '#FFF', fontWeight: '900', fontSize: 14, marginLeft: 8 },
});
