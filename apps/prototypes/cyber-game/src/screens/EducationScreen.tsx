import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  KeyboardAvoidingView, Platform, ScrollView, SafeAreaView
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import Animated, { FadeInUp, Layout } from 'react-native-reanimated';

type Message = {
  id: string;
  text: string;
  sender: 'user' | 'tutor';
  isHint?: boolean;
};

export default function EducationScreen({ onBack }: { onBack: () => void }) {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'よく来ましたね。今日はどんなテーマについて深く考えたいですか？',
      sender: 'tutor'
    }
  ]);
  const scrollViewRef = useRef<ScrollView>(null);

  // 送信テスト用ロジック（実際にはローカルOllama等に送る）
  const handleSend = () => {
    if (!inputText.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      sender: 'user'
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputText('');

    // モック：数秒後にソクラテス式の返答を返す
    setTimeout(() => {
      const tutorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: `なるほど、「${userMsg.text}」と考えているのですね。では、もしその前提が少し違っていたとしたら、どういう結論になると思いますか？`,
        sender: 'tutor',
        isHint: true
      };
      setMessages(prev => [...prev, tutorMsg]);
    }, 1500);
  };

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  return (
    <SafeAreaView style={styles.container}>
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <MaterialIcons name="arrow-back-ios" size={20} color="#00FF99" />
          <Text style={styles.backText}>HOME</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>TUTOR AI</Text>
        <MaterialIcons name="school" size={24} color="#00FF99" />
      </View>

      <KeyboardAvoidingView 
        style={{ flex: 1 }} 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView 
          ref={scrollViewRef}
          contentContainerStyle={styles.chatContainer}
          showsVerticalScrollIndicator={false}
        >
          {messages.map((msg, index) => (
            <Animated.View
              key={msg.id}
              entering={FadeInUp.delay(index * 100).springify().damping(12).stiffness(100)}
              layout={Layout.springify()}
              style={[
                styles.messageWrapper,
                msg.sender === 'user' ? styles.messageWrapperUser : styles.messageWrapperTutor
              ]}
            >
              {msg.sender === 'tutor' && (
                <View style={styles.tutorIcon}>
                  <MaterialIcons name="lightbulb-outline" size={16} color="#0b1c30" />
                </View>
              )}
              
              <View style={[
                styles.messageBubble,
                msg.sender === 'user' ? styles.bubbleUser : styles.bubbleTutor,
                msg.isHint && styles.bubbleHint
              ]}>
                <Text style={styles.messageText}>{msg.text}</Text>
              </View>
            </Animated.View>
          ))}
        </ScrollView>

        {/* ─── Input Area ─── */}
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            placeholder="あなたの考えを入力して対話を開始..."
            placeholderTextColor="#666"
            value={inputText}
            onChangeText={setInputText}
            multiline
          />
          <TouchableOpacity 
            style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]} 
            onPress={handleSend}
            disabled={!inputText.trim()}
          >
            <MaterialIcons name="send" size={20} color="#000" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#1A1A1A',
    backgroundColor: '#050505'
  },
  backButton: { flexDirection: 'row', alignItems: 'center' },
  backText: { color: '#00FF99', fontSize: 14, fontWeight: 'bold' },
  headerTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', letterSpacing: 2 },
  
  chatContainer: { paddingHorizontal: 16, paddingVertical: 24, paddingBottom: 60 },
  messageWrapper: { flexDirection: 'row', marginBottom: 24, alignItems: 'flex-end' },
  messageWrapperUser: { justifyContent: 'flex-end' },
  messageWrapperTutor: { justifyContent: 'flex-start' },
  
  tutorIcon: { width: 30, height: 30, borderRadius: 15, backgroundColor: '#00FF99', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  
  messageBubble: { paddingHorizontal: 16, paddingVertical: 12, borderRadius: 20, maxWidth: '80%' },
  bubbleUser: { backgroundColor: '#222', borderBottomRightRadius: 4 },
  bubbleTutor: { backgroundColor: '#111', borderWidth: 1, borderColor: '#333', borderBottomLeftRadius: 4 },
  bubbleHint: { borderColor: '#00FF99', borderWidth: 1, backgroundColor: 'rgba(0, 255, 153, 0.05)' },
  
  messageText: { color: '#FFF', fontSize: 15, lineHeight: 24 },
  
  inputArea: {
    flexDirection: 'row', alignItems: 'flex-end', padding: 16,
    backgroundColor: '#0A0A0A', borderTopWidth: 1, borderTopColor: '#1A1A1A',
    paddingBottom: Platform.OS === 'ios' ? 32 : 16
  },
  textInput: {
    flex: 1, backgroundColor: '#151515', color: '#FFF', borderRadius: 24, paddingHorizontal: 20,
    paddingTop: 14, paddingBottom: 14, fontSize: 15, minHeight: 48, maxHeight: 120, borderWidth: 1, borderColor: '#222'
  },
  sendButton: {
    width: 48, height: 48, borderRadius: 24, backgroundColor: '#00FF99',
    justifyContent: 'center', alignItems: 'center', marginLeft: 12
  },
  sendButtonDisabled: { backgroundColor: '#333' }
});
