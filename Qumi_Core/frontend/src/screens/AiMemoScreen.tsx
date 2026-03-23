import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Platform, Dimensions } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeInUp, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, Layout } from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

type ChatMessage = { id: string, role: 'user' | 'agent', text: string };

const INITIAL_MESSAGES: ChatMessage[] = [
  { id: 'start', role: 'agent', text: 'Abstract Layer Activated. 思考のベクトルを入力してください。永続化ストレージは接続済みです。' }
];

export default function AiMemoScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const pulse = useSharedValue(1);

  useEffect(() => {
    pulse.value = withRepeat(withTiming(1.5, { duration: 1500, easing: Easing.inOut(Easing.ease) }), -1, true);
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const saved = await AsyncStorage.getItem('@qumi_ai_chats');
      if (saved) setMessages(JSON.parse(saved));
    } catch(e) {}
  };

  const saveData = async (msgs: ChatMessage[]) => {
    try {
      await AsyncStorage.setItem('@qumi_ai_chats', JSON.stringify(msgs));
    } catch(e) {}
  }

  const siriRingStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }]
  }));

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setIsProcessing(true);
    saveData(newMessages);

    setTimeout(() => {
      const agentMsg: ChatMessage = { 
        id: (Date.now() + 1).toString(), 
        role: 'agent', 
        text: `【ベクトル解析完了】\n"${userMsg.text}"\nこの思考はローカルに永久保存されました。自己拡張システムがこれを学習し、次の行動に委譲します。`
      };
      const finalized = [...newMessages, agentMsg];
      setMessages(finalized);
      setIsProcessing(false);
      saveData(finalized);
    }, 1500);
  };

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={Platform.OS === 'ios' ? 80 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <ScrollView contentContainerStyle={styles.chatArea} showsVerticalScrollIndicator={false}>
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <Text style={styles.title}>AI MEMO</Text>
          <Text style={styles.subtitle}>Memory Sync: Active</Text>
        </Animated.View>

        {messages.map((msg, index) => (
          <Animated.View key={msg.id} layout={Layout.springify()} entering={FadeInUp.delay(index * 50).springify().damping(15)} 
            style={[styles.messageRow, msg.role === 'user' ? styles.userRow : styles.agentRow]}
          >
            <BlurView intensity={60} tint="dark" style={[styles.bubble, msg.role === 'user' ? styles.userBubble : styles.agentBubble]}>
              <Text style={styles.messageText}>{msg.text}</Text>
            </BlurView>
          </Animated.View>
        ))}
      </ScrollView>

      <Animated.View entering={FadeInUp.delay(500).springify()} style={styles.inputArea}>
        <BlurView intensity={90} tint="dark" style={styles.inputBlur}>
           {isProcessing ? (
             <View style={styles.siriContainer}>
               <Animated.View style={[styles.siriPulse, siriRingStyle]} />
               <LinearGradient colors={['#A020F0', '#00D4FF']} style={styles.siriOrb} />
               <Text style={styles.processingText}>Processing Vectors...</Text>
             </View>
           ) : (
             <View style={styles.inputRow}>
               <TextInput 
                 style={styles.textInput} 
                 placeholder="思考を記録..." 
                 placeholderTextColor="#888" 
                 value={input} 
                 onChangeText={setInput} 
                 onSubmitEditing={handleSend}
               />
               <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
                 <LinearGradient colors={['#B026FF', '#00D4FF']} style={styles.sendGradient}>
                   <Text style={styles.sendIcon}>↑</Text>
                 </LinearGradient>
               </TouchableOpacity>
             </View>
           )}
        </BlurView>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow: { position: 'absolute', top: height * 0.2, left: -50, width: width, height: height * 0.8, backgroundColor: '#A020F0', opacity: 0.15, filter: 'blur(100px)' as any },
  
  header: { alignItems: 'center', marginVertical: 30, marginTop: Platform.OS === 'web' ? 80 : 100 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', fontFamily: 'Outfit_900Black', letterSpacing: 2 },
  subtitle: { color: '#00FF99', fontSize: 13, fontFamily: 'Outfit_700Bold', marginTop: 4, letterSpacing: 1 },

  chatArea: { paddingHorizontal: 20, paddingBottom: 150 },
  messageRow: { marginBottom: 20, width: '100%', flexDirection: 'row' },
  userRow: { justifyContent: 'flex-end' },
  agentRow: { justifyContent: 'flex-start' },
  
  bubble: { padding: 16, borderRadius: 24, overflow: 'hidden', maxWidth: '85%' },
  userBubble: { backgroundColor: 'rgba(176, 38, 255, 0.2)', borderWidth: 1, borderColor: 'rgba(176, 38, 255, 0.4)' },
  agentBubble: { backgroundColor: 'rgba(255, 255, 255, 0.05)', borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.1)' },
  messageText: { color: '#FFF', fontSize: 15, fontFamily: 'Outfit_400Regular', lineHeight: 22 },

  inputArea: { position: 'absolute', bottom: 30, left: 16, right: 16, borderRadius: 32, overflow: 'hidden' },
  inputBlur: { padding: 8 },
  inputRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 28, paddingLeft: 20, paddingRight: 8, paddingVertical: 8 },
  textInput: { flex: 1, color: '#FFF', fontSize: 16, fontFamily: 'Outfit_400Regular', height: 40 },
  sendButton: { width: 40, height: 40, borderRadius: 20, overflow: 'hidden', marginLeft: 12 },
  sendGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  sendIcon: { color: '#FFF', fontSize: 20, fontWeight: 'bold' },

  siriContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12 },
  siriPulse: { position: 'absolute', left: 40, width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(0, 212, 255, 0.4)' },
  siriOrb: { width: 30, height: 30, borderRadius: 15, shadowColor: '#00D4FF', shadowOpacity: 1, shadowRadius: 10 },
  processingText: { color: '#00D4FF', marginLeft: 20, fontFamily: 'Outfit_700Bold', fontSize: 14, letterSpacing: 1 }
});
