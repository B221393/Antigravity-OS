import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  ScrollView, KeyboardAvoidingView, Platform, Dimensions,
  Keyboard, TouchableWithoutFeedback, Linking
} from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Sparkles, Send, BrainCircuit, Zap } from 'lucide-react-native';
import Animated, { 
  FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, 
  withSpring, withRepeat, withTiming, Easing 
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

// ─── シンクロ率に連動するボタン ───
const SiriGlowButton = ({ onPress, syncRate }: { onPress: () => void, syncRate: Animated.SharedValue<number> }) => {
  const scale = useSharedValue(1);
  const glow = useSharedValue(0.5);

  useEffect(() => {
    glow.value = withRepeat(withTiming(1, { duration: 1500, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const handlePressIn = () => { scale.value = withSpring(0.8); };
  const handlePressOut = () => { scale.value = withSpring(1); };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: 0.8 + (syncRate.value / 200)
  }));

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glow.value + (syncRate.value / 100),
    transform: [{ scale: 1 + (syncRate.value / 100) }]
  }));

  return (
    <Animated.View style={animatedStyle}>
      <TouchableOpacity onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress} activeOpacity={1}>
        <Animated.View style={[styles.siriGlow, glowStyle]} />
        <LinearGradient colors={['#A020F0', '#00D4FF']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.sendButton}>
          <Zap color="#FFF" size={20} />
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
};

export default function AiMemoScreen() {
  const [inputText, setInputText] = useState('');
  const [memos, setMemos] = useState<{ id: string, text: string, type: 'user' | 'ai' }[]>([
    { id: '1', text: 'Abstract Layer Activated. 思考のベクトルを入力してください。\nシステムがあなたの「魂」を解析し、外部脳へと委譲します。', type: 'ai' }
  ]);
  
  const syncRate = useSharedValue(0);

  useEffect(() => {
    const decay = setInterval(() => {
      if (syncRate.value > 0) syncRate.value = Math.max(0, syncRate.value - 3);
    }, 1000);
    return () => clearInterval(decay);
  }, []);

  const handleTextChange = (text: string) => {
    setInputText(text);
    syncRate.value = Math.min(100, syncRate.value + 8);
  };

  const glowStyle = useAnimatedStyle(() => ({
    opacity: 0.3 + (syncRate.value / 150),
    transform: [{ scale: 1 + (syncRate.value / 200) }]
  }));

  const handleSend = async () => {
    if (!inputText.trim()) return;
    const userInput = inputText;
    const newMemo = { id: Date.now().toString(), text: userInput, type: 'user' as const };
    setMemos(prev => [...prev, newMemo]);
    setInputText('');
    syncRate.value = 100;
    
    const aiMessageId = (Date.now()+1).toString();
    setMemos(prev => [...prev, { id: aiMessageId, text: '🧠 思考のベクトルを解析中...\n外部脳（Soul API）が情報を拡張しています。', type: 'ai' }]);
    
    try {
      const response = await fetch('http://localhost:8000/api/soul', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thought: userInput })
      });
      const data = await response.json();
      const resultText = data.result ? (typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2)) : '解析エラー';
      setMemos(prev => prev.map(m => m.id === aiMessageId ? { ...m, text: resultText } : m));
    } catch (e: any) {
      setMemos(prev => prev.map(m => m.id === aiMessageId ? { 
        ...m, text: `⚠️ PC Agent Offline\n同期は GitHub で確立されています。[GITHUB PORTAL] ボタンから最新の外部脳を確認してください。` 
      } : m));
    }
  };

  const openGithubPortal = () => {
    const url = 'https://github.com/b221393/my-syukatu-app/blob/main/logs/STRATEGIC_INTEL_LOG.md';
    Linking.openURL(url);
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
      
      <Animated.View style={[styles.bgGlow1, glowStyle]} />
      <View style={styles.bgGlow2} />
      <BlurView intensity={Platform.OS === 'ios' ? 70 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <View style={styles.inner}>
          
          <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.header}>
            <View style={styles.headerRow}>
              <BrainCircuit color="#00D4FF" size={24} />
              <Text style={styles.title}>AI MEMO</Text>
            </View>
            <TouchableOpacity onPress={openGithubPortal} style={styles.githubPortal}>
              <BlurView intensity={20} tint="light" style={styles.portalBlur}>
                <Sparkles color="#00FF99" size={14} />
                <Text style={styles.portalText}>GITHUB PORTAL</Text>
              </BlurView>
            </TouchableOpacity>
            <View style={styles.syncIndicator}>
              <Text style={styles.syncLabel}>THOUGHT SYNC:</Text>
              <Text style={styles.syncValue}>{Math.floor(syncRate.value)}%</Text>
            </View>
          </Animated.View>

          <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
            {/* 📜 AI Remodeling Chronicle Insight */}
            <Animated.View entering={FadeInDown.delay(200).springify()}>
              <BlurView intensity={30} tint="light" style={styles.chronicleCard}>
                <View style={styles.chronicleHeader}>
                  <Sparkles color="#00FF99" size={16} />
                  <Text style={styles.chronicleLabel}>LATEST CHRONICLE: VOL.01</Text>
                </View>
                <Text style={styles.chronicleText}>AIインフラによる「覚えるコスト」の削減。人間は「問いを立てる」ことに特化し始める。</Text>
                <TouchableOpacity style={styles.readMoreBtn} onPress={() => {
                   Linking.openURL('https://github.com/b221393/my-syukatu-app/blob/main/apps/prototypes/qumi/docs/remodeling/vol_01_external_brain.md');
                }}>
                  <Text style={styles.readMoreText}>READ FULL ANALYSIS</Text>
                </TouchableOpacity>
              </BlurView>
            </Animated.View>

            {memos.map((memo, index) => (
              <Animated.View 
                key={memo.id} 
                entering={FadeInUp.delay(index * 100).springify().damping(15)}
                style={[styles.messageWrapper, memo.type === 'user' ? styles.messageUserWrapper : styles.messageAiWrapper]}
              >
                {memo.type === 'ai' && (
                  <LinearGradient colors={['#A020F0', '#00D4FF']} style={styles.aiAvatar}>
                    <Sparkles color="#FFF" size={14} />
                  </LinearGradient>
                )}
                
                <View style={[styles.messageBubble, memo.type === 'user' ? styles.messageUser : styles.messageAi]}>
                  <Text style={[styles.messageText, memo.type === 'user' && { color: '#FFF' }]}>{memo.text}</Text>
                </View>
              </Animated.View>
            ))}
          </ScrollView>

          <Animated.View entering={FadeInUp.delay(300).springify()} style={styles.inputContainer}>
            <BlurView intensity={80} tint="dark" style={styles.inputBlur}>
              <TextInput
                style={styles.textInput}
                placeholder="思考を入力..."
                placeholderTextColor="#666"
                value={inputText}
                onChangeText={handleTextChange}
                multiline
              />
              <SiriGlowButton onPress={handleSend} syncRate={syncRate} />
            </BlurView>
          </Animated.View>

        </View>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  
  bgGlow1: { position: 'absolute', top: '-10%', left: '-20%', width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#4B0082', opacity: 0.5 },
  bgGlow2: { position: 'absolute', bottom: '10%', right: '-20%', width: width*0.7, height: width*0.7, borderRadius: width, backgroundColor: '#00BFFF', opacity: 0.4 },
  
  inner: { flex: 1, paddingTop: Platform.OS === 'web' ? 60 : 80 },

  header: { alignItems: 'center', marginBottom: 20 },
  headerRow: { flexDirection: 'row', alignItems: 'center' },
  githubPortal: { marginTop: 12, borderRadius: 16, overflow: 'hidden' },
  portalBlur: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 6, backgroundColor: 'rgba(0, 255, 153, 0.1)' },
  portalText: { color: '#00FF99', fontSize: 10, fontFamily: 'Outfit_900Black', marginLeft: 6, letterSpacing: 1 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '800', fontFamily: 'Outfit_900Black', letterSpacing: 4, marginLeft: 10 },
  syncIndicator: { flexDirection: 'row', marginTop: 8 },
  syncLabel: { color: '#666', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
  syncValue: { color: '#00D4FF', fontSize: 10, fontWeight: '900', marginLeft: 6 },

  chronicleCard: { marginVertical: 20, padding: 16, borderRadius: 20, borderWidth: 1, borderColor: 'rgba(0, 255, 153, 0.2)', backgroundColor: 'rgba(0, 0, 0, 0.3)' },
  chronicleHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  chronicleLabel: { color: '#00FF99', fontSize: 10, fontWeight: '900', marginLeft: 8, letterSpacing: 1 },
  chronicleText: { color: '#CCC', fontSize: 13, lineHeight: 18 },
  readMoreBtn: { marginTop: 12, alignSelf: 'flex-start' },
  readMoreText: { color: '#00D4FF', fontSize: 10, fontWeight: '900', letterSpacing: 1 },

  scrollContent: { paddingHorizontal: 20, paddingBottom: 150 },

  messageWrapper: { flexDirection: 'row', alignItems: 'flex-end', marginBottom: 20 },
  messageUserWrapper: { justifyContent: 'flex-end' },
  messageAiWrapper: { justifyContent: 'flex-start' },

  aiAvatar: { width: 28, height: 28, borderRadius: 14, justifyContent: 'center', alignItems: 'center', marginRight: 10, shadowColor: '#A020F0', shadowOpacity: 0.8, shadowRadius: 10 },

  messageBubble: { maxWidth: '80%', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20, overflow: 'hidden' },
  messageUser: { backgroundColor: 'rgba(255, 255, 255, 0.1)', borderBottomRightRadius: 4, borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  messageAi: { backgroundColor: 'rgba(10, 10, 20, 0.7)', borderBottomLeftRadius: 4, borderWidth: 1, borderColor: 'rgba(160, 32, 240, 0.2)' },
  
  messageText: { color: '#E0E0E0', fontSize: 14, lineHeight: 22 },

  inputContainer: { position: 'absolute', bottom: Platform.OS === 'ios' ? 40 : 20, left: 16, right: 16 },
  inputBlur: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 32, backgroundColor: 'rgba(30,30,30,0.5)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  
  textInput: { flex: 1, color: '#FFF', fontSize: 15, marginRight: 12, maxHeight: 120 },

  siriGlow: { position: 'absolute', top: -4, left: -4, right: -4, bottom: -4, borderRadius: 24, backgroundColor: '#00D4FF' },
  sendButton: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', shadowColor: '#A020F0', shadowOpacity: 0.5, shadowRadius: 10 }
});
