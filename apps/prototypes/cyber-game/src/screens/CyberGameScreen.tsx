import React, { useState, useEffect } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, Alert, Platform
} from 'react-native';
import { Lock, Unlock, Shield, Database, Cpu } from 'lucide-react-native';
import * as SecureStore from 'expo-secure-store';
import Animated, {
  useSharedValue, useAnimatedStyle, withRepeat, withSequence,
  withTiming, Easing
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

const { width } = Dimensions.get('window');
const COLORS = ['#FF3B30', '#00FF99', '#5AC8FA', '#FFCC00'];

export default function CyberGameScreen({ onBack }: { onBack: () => void }) {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [sequence, setSequence] = useState<number[]>([]);
  const [playerInput, setPlayerInput] = useState<number[]>([]);

  // 鼓動・シェイクのアニメーション用
  const lockShake = useSharedValue(0);
  const pulseScale = useSharedValue(1);

  useEffect(() => {
    initGame();
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

  const handleNodePress = (index: number) => {
    const currentStep = playerInput.length;
    
    // 不正解
    if (index !== sequence[currentStep]) {
      lockShake.value = withSequence(
        withTiming(10, { duration: 50 }),
        withTiming(-10, { duration: 50 }),
        withTiming(10, { duration: 50 }),
        withTiming(0, { duration: 50 })
      );
      setPlayerInput([]);
      if (Platform.OS === 'web') alert('アクセス拒否: パスコードが違います。');
      else Alert.alert('HACK FAILED', 'アクセスが拒否されました。パターンが違います。');
      return;
    }

    const nextInput = [...playerInput, index];
    setPlayerInput(nextInput);

    // 全て正解
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>← HOME</Text>
        </TouchableOpacity>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>02 / CYBER GAME</Text>
        </View>
      </View>

      {!isUnlocked ? (
        // ─── ゲーム画面 ───
        <View style={styles.gameArea}>
          <View style={styles.gameTitleBox}>
            <Shield color="#FF3B30" size={32} />
            <Text style={styles.title}>VECTIS FIREWALL</Text>
            <Text style={styles.subtitle}>// UNAUTHORIZED ACCESS DETECTED //</Text>
          </View>

          <Animated.View style={[styles.lockContainer, lockStyle]}>
            <Lock color="#444" size={80} />
            <Text style={styles.lockText}>RESTRICTED VAULT</Text>
            <Text style={styles.hintText}>
              機密領域にアクセスするには、最新のバイパス・シーケンス（4つの色）を推理して解除せよ。
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
          
          <Text style={styles.cheatText}>
            【チート】正解: {sequence.map(i => COLORS[i] === '#FF3B30' ? '🟥' : COLORS[i] === '#00FF99' ? '🟩' : COLORS[i] === '#5AC8FA' ? '🟦' : '🟨').join(' > ')}
          </Text>
        </View>
      ) : (
        // ─── クリア画面（極秘Vault） ───
        <Animated.View style={[styles.gameArea, pulseStyle]}>
          <Unlock color="#00FF99" size={64} style={{ marginBottom: 20 }} />
          <Text style={styles.unlockedTitle}>ACCESS GRANTED</Text>
          <Text style={styles.unlockedSubtitle}>Welcome back, Agent Yuto.</Text>
          
          <View style={styles.secretBox}>
            <View style={styles.secretBoxHeader}>
              <Database color="#00FF99" size={18} />
              <Text style={styles.secretBoxTitle}>DEVICE SECURE STORE</Text>
            </View>
            <Text style={styles.secretDataText}>
              VECTIS_CORE_OVERRIDE="ENABLED"{'\n'}
              INTERNAL_IP="192.168.x.x"{'\n'}
              AUTH_STATUS="VERIFIED"
            </Text>
            <Text style={styles.secretNotice}>
              ※このデータはゲームをクリアしたユーザー（管理者）のみがローカル環境でアクセスできる情報です。
            </Text>
          </View>

          <TouchableOpacity style={styles.lockButton} onPress={() => {
            setIsUnlocked(false);
            setPlayerInput([]);
            initGame();
          }}>
            <Lock color="#FFF" size={16} />
            <Text style={styles.lockButtonText}>VAULT を再ロックする</Text>
          </TouchableOpacity>
        </Animated.View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505' },
  header: { flexDirection: 'row', justifyContent: 'space-between', padding: 20, alignItems: 'center' },
  backButton: { padding: 8, backgroundColor: '#111', borderRadius: 8, borderWidth: 1, borderColor: '#333' },
  backButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 12 },
  badge: { backgroundColor: '#FF3B3022', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, borderWidth: 1, borderColor: '#FF3B3055' },
  badgeText: { color: '#FF3B30', fontWeight: 'bold', fontSize: 10, letterSpacing: 1 },

  gameArea: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  gameTitleBox: { alignItems: 'center', marginBottom: 20 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 4, marginTop: 12 },
  subtitle: { color: '#FF3B30', fontSize: 10, fontWeight: '700', letterSpacing: 2, marginTop: 4 },
  
  lockContainer: { alignItems: 'center', marginBottom: 40 },
  lockText: { color: '#444', fontSize: 18, fontWeight: '900', letterSpacing: 2, marginTop: 16 },
  hintText: { color: '#666', fontSize: 12, textAlign: 'center', marginTop: 16, paddingHorizontal: 40, lineHeight: 20 },
  
  progressRow: { flexDirection: 'row', gap: 16, marginBottom: 40 },
  progressDot: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: '#333', backgroundColor: 'transparent' },
  
  nodeGrid: { flexDirection: 'row', flexWrap: 'wrap', width: width * 0.7, justifyContent: 'center', gap: 16 },
  nodeWrapper: { width: '45%', aspectRatio: 1 },
  node: { flex: 1, borderRadius: 24, borderWidth: 2, alignItems: 'center', justifyContent: 'center' },
  
  cheatText: { color: '#222', fontSize: 10, position: 'absolute', bottom: 40, fontFamily: 'monospace' },

  unlockedTitle: { color: '#00FF99', fontSize: 32, fontWeight: '900', letterSpacing: 2 },
  unlockedSubtitle: { color: '#FFF', fontSize: 14, fontWeight: '800', opacity: 0.8, marginBottom: 40 },
  
  secretBox: { backgroundColor: '#000', borderWidth: 1, borderColor: '#00FF99', borderRadius: 16, padding: 24, width: '85%', marginBottom: 40 },
  secretBoxHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, borderBottomWidth: 1, borderBottomColor: '#113311', paddingBottom: 12, marginBottom: 16 },
  secretBoxTitle: { color: '#00FF99', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  secretDataText: { color: '#FFF', fontSize: 13, fontWeight: '700', fontFamily: 'monospace', marginBottom: 20, lineHeight: 24 },
  secretNotice: { color: '#00FF99', fontSize: 10, lineHeight: 16, opacity: 0.6 },
  
  lockButton: { flexDirection: 'row', backgroundColor: '#FF3B30', paddingHorizontal: 24, paddingVertical: 16, borderRadius: 12, alignItems: 'center' },
  lockButtonText: { color: '#FFF', fontWeight: '900', fontSize: 14, marginLeft: 8 },
});
