import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  ScrollView, KeyboardAvoidingView, Platform, Dimensions,
  Keyboard, TouchableWithoutFeedback, Linking
} from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Sparkles, Send, BrainCircuit, Zap, Users, MessageSquare } from 'lucide-react-native';
import Animated, { 
  FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, 
  withSpring, withRepeat, withTiming, Easing 
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

const SiriGlowButton = ({ onPress, syncRate, isActive }: { onPress: () => void, syncRate: Animated.SharedValue<number>, isActive: boolean }) => {
  const scale = useSharedValue(1);
  const glow = useSharedValue(0.5);

  useEffect(() => {
    glow.value = withRepeat(withTiming(1, { duration: 1500, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: withSpring(scale.value) }],
    opacity: 0.8 + (syncRate.value / 200)
  }));

  const glowStyle = useAnimatedStyle(() => ({
    opacity: glow.value + (syncRate.value / 100),
    transform: [{ scale: 1 + (syncRate.value / 100) }]
  }));

  return (
    <Animated.View style={animatedStyle}>
      <TouchableOpacity 
        onPressIn={() => { scale.value = 0.8; }} 
        onPressOut={() => { scale.value = 1; }} 
        onPress={onPress} 
        activeOpacity={1}
      >
        <Animated.View style={[styles.siriGlow, glowStyle, isActive && { backgroundColor: '#FF00B3' }]} />
        <LinearGradient 
          colors={isActive ? ['#FF00B3', '#FF5C93'] : ['#A020F0', '#00D4FF']} 
          start={{ x: 0, y: 0 }} 
          end={{ x: 1, y: 1 }} 
          style={styles.sendButton}
        >
          {isActive ? <Users color="#FFF" size={20} /> : <Zap color="#FFF" size={20} />}
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
};

export default function AiMemoScreen() {
  const [inputText, setInputText] = useState('');
  const [isDebateMode, setIsDebateMode] = useState(false);
  const [memos, setMemos] = useState<{ id: string, text: string, type: 'user' | 'ai' | 'debate', debateData?: any }[]>([
    { id: '1', text: 'Abstract Layer Activated. 思考のベクトルを入力してください。', type: 'ai' }
  ]);
  
  const syncRate = useSharedValue(0);

  useEffect(() => {
    const decay = setInterval(() => {
      if (syncRate.value > 0) syncRate.value = Math.max(0, syncRate.value - 3);
    }, 1000);
    return () => clearInterval(decay);
  }, []);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    const userInput = inputText;
    setMemos(prev => [...prev, { id: Date.now().toString(), text: userInput, type: 'user' }]);
    setInputText('');
    syncRate.value = 100;
    
    const aiMessageId = (Date.now()+1).toString();
    setMemos(prev => [...prev, { id: aiMessageId, text: isDebateMode ? '👥 複数人格が議論を開始します...' : '🧠 思考を解析中...', type: 'ai' }]);
    
    const endpoint = isDebateMode ? 'http://localhost:8000/api/debate' : 'http://localhost:8000/api/soul';
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(isDebateMode ? { thought: userInput } : { thought: userInput })
      });
      const data = await response.json();
      
      if (isDebateMode && data.debate) {
        setMemos(prev => prev.map(m => m.id === aiMessageId ? { 
          id: m.id, type: 'debate', text: data.debate.synthesis, debateData: data.debate 
        } : m));
      } else {
        const resultText = data.result ? (typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2)) : '解析エラー';
        setMemos(prev => prev.map(m => m.id === aiMessageId ? { ...m, text: resultText } : m));
      }
    } catch (e) {
      setMemos(prev => prev.map(m => m.id === aiMessageId ? { ...m, text: '⚠️ 外部脳オフライン。ローカル同期に切り替えてください。' } : m));
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
      <BlurView intensity={Platform.OS === 'ios' ? 70 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.inner}>
        <View style={styles.header}>
          <Text style={styles.title}>AI MEMO</Text>
          <TouchableOpacity onPress={() => setIsDebateMode(!isDebateMode)} style={[styles.modeToggle, isDebateMode && styles.modeToggleActive]}>
            <Users color={isDebateMode ? "#FFF" : "#666"} size={14} />
            <Text style={[styles.modeToggleText, isDebateMode && { color: '#FFF' }]}>{isDebateMode ? "MULTI-AGENT" : "SOLO AI"}</Text>
          </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {memos.map((memo, index) => (
            <Animated.View key={memo.id} entering={FadeInUp.delay(index * 100)} style={styles.messageWrapper}>
              {memo.type === 'debate' ? (
                <View style={styles.debateContainer}>
                  <Text style={styles.debateTitle}>MULTI-AGENT DEBATE</Text>
                  <View style={styles.agentBox}>
                    <Text style={[styles.agentName, { color: '#00D4FF' }]}>ARCHITECT</Text>
                    <Text style={styles.agentText}>{memo.debateData.architect}</Text>
                  </View>
                  <View style={styles.agentBox}>
                    <Text style={[styles.agentName, { color: '#FF0055' }]}>CRITIC</Text>
                    <Text style={styles.agentText}>{memo.debateData.critic}</Text>
                  </View>
                  <View style={styles.agentBox}>
                    <Text style={[styles.agentName, { color: '#FF9E00' }]}>VISIONARY</Text>
                    <Text style={styles.agentText}>{memo.debateData.visionary}</Text>
                  </View>
                  <View style={styles.synthesisBox}>
                    <Text style={styles.synthesisTitle}>SYNTHESIS</Text>
                    <Text style={styles.synthesisText}>{memo.debateData.synthesis}</Text>
                  </View>
                </View>
              ) : (
                <View style={[styles.bubble, memo.type === 'user' ? styles.userBubble : styles.aiBubble]}>
                  <Text style={styles.messageText}>{memo.text}</Text>
                </View>
              )}
            </Animated.View>
          ))}
        </ScrollView>

        <View style={styles.inputArea}>
          <BlurView intensity={80} tint="dark" style={styles.inputBlur}>
            <TextInput
              style={styles.textInput}
              placeholder={isDebateMode ? "議論を開始..." : "思考を入力..."}
              placeholderTextColor="#666"
              value={inputText}
              onChangeText={setInputText}
              multiline
            />
            <SiriGlowButton onPress={handleSend} syncRate={syncRate} isActive={isDebateMode} />
          </BlurView>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  inner: { flex: 1, paddingTop: 60 },
  header: { alignItems: 'center', marginBottom: 20 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 4 },
  scrollContent: { paddingHorizontal: 20, paddingBottom: 150 },
  
  modeToggle: { flexDirection: 'row', alignItems: 'center', marginTop: 12, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  modeToggleActive: { backgroundColor: 'rgba(255, 0, 179, 0.2)', borderColor: 'rgba(255, 0, 179, 0.4)' },
  modeToggleText: { color: '#666', fontSize: 10, fontWeight: '900', marginLeft: 6, letterSpacing: 1 },

  messageWrapper: { marginBottom: 20 },
  bubble: { padding: 16, borderRadius: 20, maxWidth: '85%' },
  userBubble: { alignSelf: 'flex-end', backgroundColor: 'rgba(0, 212, 255, 0.15)', borderBottomRightRadius: 4 },
  aiBubble: { alignSelf: 'flex-start', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderBottomLeftRadius: 4 },
  messageText: { color: '#FFF', fontSize: 14, lineHeight: 22 },

  debateContainer: { backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 24, padding: 20, borderWidth: 1, borderColor: 'rgba(255,0,179,0.2)' },
  debateTitle: { color: '#FF00B3', fontSize: 11, fontWeight: '900', letterSpacing: 2, marginBottom: 16, textAlign: 'center' },
  agentBox: { marginBottom: 16 },
  agentName: { fontSize: 10, fontWeight: '900', marginBottom: 4, letterSpacing: 1 },
  agentText: { color: '#BBB', fontSize: 13, lineHeight: 18 },
  synthesisBox: { marginTop: 8, padding: 16, borderRadius: 16, backgroundColor: 'rgba(255,255,255,0.05)' },
  synthesisTitle: { color: '#FFF', fontSize: 10, fontWeight: '900', marginBottom: 8 },
  synthesisText: { color: '#FFF', fontSize: 14, fontWeight: '700', lineHeight: 22 },

  inputArea: { position: 'absolute', bottom: 30, left: 16, right: 16 },
  inputBlur: { flexDirection: 'row', alignItems: 'center', padding: 12, borderRadius: 32, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  textInput: { flex: 1, color: '#FFF', fontSize: 15, paddingLeft: 12 },
  siriGlow: { position: 'absolute', top: -4, left: -4, right: -4, bottom: -4, borderRadius: 24, backgroundColor: '#00D4FF' },
  sendButton: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' }
});
