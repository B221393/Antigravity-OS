import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Platform, Dimensions, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, { FadeInUp, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, Layout } from 'react-native-reanimated';
import { Audio } from 'expo-av';
import axios from 'axios';
import { Mic, Send, Square } from 'lucide-react-native';

const { width, height } = Dimensions.get('window');

// 開発環境用のローカルIPアドレスを設定（バックエンドのポートに合わせてください）
const BACKEND_URL = 'http://127.0.0.1:8000'; 

type ChatMessage = { id: string, role: 'user' | 'agent', text: string };

const INITIAL_MESSAGES: ChatMessage[] = [
  { id: 'start', role: 'agent', text: 'Abstract Layer Activated. 思考のベクトルを入力、または音声で注入してください。' }
];

export default function AiMemoScreen() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const pulse = useSharedValue(1);

  useEffect(() => {
    pulse.value = withRepeat(withTiming(1.5, { duration: 1500, easing: Easing.inOut(Easing.ease) }), -1, true);
    loadData();
    
    // 音声パーミッションの要求
    (async () => {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    })();
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

  const startRecording = async () => {
    try {
      console.log('Starting recording...');
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert('Error', '録音の開始に失敗しました。');
    }
  };

  const stopRecording = async () => {
    console.log('Stopping recording...');
    setIsRecording(false);
    if (!recording) return;
    
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      
      if (uri) {
        processVoice(uri);
      }
    } catch (error) {
      console.error('Failed to stop recording', error);
    }
  };

  const processVoice = async (uri: string) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      // @ts-ignore
      formData.append('file', {
        uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
        name: 'recording.m4a',
        type: 'audio/m4a',
      });
      formData.append('persona', 'soul');

      const response = await axios.post(`${BACKEND_URL}/voice`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const { transcription, structured_result } = response.data;
      
      const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: transcription };
      const agentMsg: ChatMessage = { 
        id: (Date.now() + 1).toString(), 
        role: 'agent', 
        text: `【音声ベクトル解析完了】\n"${transcription}"\n\n${JSON.stringify(structured_result, null, 2)}`
      };
      
      const newMessages = [...messages, userMsg, agentMsg];
      setMessages(newMessages);
      saveData(newMessages);
    } catch (error) {
      console.error('Voice processing error:', error);
      Alert.alert('Error', '音声の処理に失敗しました。バックエンドが起動しているか確認してください。');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;
    
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setIsProcessing(true);
    saveData(newMessages);

    try {
      const response = await axios.post(`${BACKEND_URL}/delegate`, {
        thought: input,
        persona: 'soul'
      });
      
      const agentMsg: ChatMessage = { 
        id: (Date.now() + 1).toString(), 
        role: 'agent', 
        text: `【ベクトル解析完了】\n"${input}"\n\n${JSON.stringify(response.data.result, null, 2)}`
      };
      const finalized = [...newMessages, agentMsg];
      setMessages(finalized);
      saveData(finalized);
    } catch (err) {
      console.error('Delegate error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={Platform.OS === 'ios' ? 80 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <ScrollView contentContainerStyle={styles.chatArea} showsVerticalScrollIndicator={false}>
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <Text style={styles.title}>AI MEMO</Text>
          <Text style={styles.subtitle}>Memory Sync: {isProcessing ? 'Processing...' : 'Active'}</Text>
        </Animated.View>

        {messages.map((msg, index) => (
          <Animated.View key={index} layout={Layout.springify()} entering={FadeInUp.delay(index * 50).springify().damping(15)} 
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
               <TouchableOpacity 
                 style={[styles.micButton, isRecording && styles.micButtonActive]} 
                 onPress={isRecording ? stopRecording : startRecording}
               >
                 {isRecording ? <Square color="#FFF" size={20} /> : <Mic color="#FFF" size={20} />}
               </TouchableOpacity>
               
               <TextInput 
                 style={styles.textInput} 
                 placeholder={isRecording ? "録音中..." : "思考を記録..."} 
                 placeholderTextColor="#888" 
                 value={input} 
                 onChangeText={setInput} 
                 onSubmitEditing={handleSend}
                 editable={!isRecording}
               />
               
               <TouchableOpacity style={styles.sendButton} onPress={handleSend} disabled={!input.trim()}>
                 <LinearGradient colors={['#B026FF', '#00D4FF']} style={styles.sendGradient}>
                   <Send color="#FFF" size={18} />
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
  inputRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: 28, paddingHorizontal: 12, paddingVertical: 8 },
  micButton: { width: 44, height: 44, borderRadius: 22, backgroundColor: 'rgba(255, 255, 255, 0.05)', justifyContent: 'center', alignItems: 'center', marginRight: 8 },
  micButtonActive: { backgroundColor: 'rgba(255, 0, 0, 0.3)', borderColor: 'rgba(255, 0, 0, 0.5)', borderWidth: 1 },
  textInput: { flex: 1, color: '#FFF', fontSize: 16, fontFamily: 'Outfit_400Regular', height: 44 },
  sendButton: { width: 44, height: 44, borderRadius: 22, overflow: 'hidden', marginLeft: 8 },
  sendGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  sendIcon: { color: '#FFF', fontSize: 20, fontWeight: 'bold' },

  siriContainer: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12 },
  siriPulse: { position: 'absolute', left: 40, width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(0, 212, 255, 0.4)' },
  siriOrb: { width: 30, height: 30, borderRadius: 15, shadowColor: '#00D4FF', shadowOpacity: 1, shadowRadius: 10 },
  processingText: { color: '#00D4FF', marginLeft: 20, fontFamily: 'Outfit_700Bold', fontSize: 14, letterSpacing: 1 }
});
