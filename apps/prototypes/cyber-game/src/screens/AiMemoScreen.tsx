import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  ScrollView, KeyboardAvoidingView, Platform, Dimensions,
  Keyboard, TouchableWithoutFeedback
} from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Sparkles, Mic, FileText, Send, ChevronLeft } from 'lucide-react-native';
import Animated, { FadeInDown, FadeInUp, useSharedValue, useAnimatedStyle, withSpring, withRepeat, withTiming, Easing } from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

// iOS風の送信ボタンのアニメーション
const SiriGlowButton = ({ onPress }: { onPress: () => void }) => {
  const scale = useSharedValue(1);
  const glow = useSharedValue(0.5);

  React.useEffect(() => {
    glow.value = withRepeat(withTiming(1, { duration: 1500, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const handlePressIn = () => { scale.value = withSpring(0.85); };
  const handlePressOut = () => { scale.value = withSpring(1); };

  const animatedStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
  const glowStyle = useAnimatedStyle(() => ({ opacity: glow.value }));

  return (
    <Animated.View style={animatedStyle}>
      <TouchableOpacity onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress} activeOpacity={1}>
        <Animated.View style={[styles.siriGlow, glowStyle]} />
        <LinearGradient colors={['#A020F0', '#00D4FF']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.sendButton}>
          <Sparkles color="#FFF" size={20} />
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
};

export default function AiMemoScreen() {
  const [inputText, setInputText] = useState('');
  const [memos, setMemos] = useState<{ id: string, text: string, type: 'user' | 'ai' }[]>([
    { id: '1', text: '今日はどんな思考を「外部脳」に委譲しますか？\n（就活の悩み、アイディア、何でもOKです）', type: 'ai' }
  ]);

  const handleSend = () => {
    if (!inputText.trim()) return;
    const newMemo = { id: Date.now().toString(), text: inputText, type: 'user' as const };
    setMemos(prev => [...prev, newMemo]);
    setInputText('');
    
    // AIの返信モック（Siri風の知的レスポンス）
    setTimeout(() => {
      setMemos(prev => [...prev, { 
        id: (Date.now()+1).toString(), 
        text: '記録完了。「魂のJSON化」に向けたデータとして外部脳に蓄積しました。\n何か深掘りして考察する要素はありますか？', 
        type: 'ai' 
      }]);
    }, 1000);
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
      
      {/* 🔮 背景の美しいグラデーションとブラー */}
      <View style={styles.bgGlow1} />
      <View style={styles.bgGlow2} />
      <BlurView intensity={Platform.OS === 'ios' ? 70 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <View style={styles.inner}>
          
          {/* iOS Notes 風のヘッダー */}
          <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.header}>
            <Text style={styles.title}>AI MEMO</Text>
            <Text style={styles.subtitle}>外部脳システム - 魂の記録</Text>
          </Animated.View>

          {/* メモ / チャットリスト */}
          <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
            {memos.map((memo, index) => (
              <Animated.View 
                key={memo.id} 
                entering={FadeInUp.delay(index * 150).springify().damping(15)}
                style={[styles.messageWrapper, memo.type === 'user' ? styles.messageUserWrapper : styles.messageAiWrapper]}
              >
                {memo.type === 'ai' && (
                  <LinearGradient colors={['#A020F0', '#00D4FF']} style={styles.aiAvatar}>
                    <BrainIcon color="#FFF" size={16} />
                  </LinearGradient>
                )}
                
                <View style={[styles.messageBubble, memo.type === 'user' ? styles.messageUser : styles.messageAi]}>
                  {memo.type === 'ai' && <View style={styles.aiGlowEffect} />}
                  <Text style={[styles.messageText, memo.type === 'user' && { color: '#FFF' }]}>{memo.text}</Text>
                </View>
              </Animated.View>
            ))}
          </ScrollView>

          {/* iOS風のフッター入力エリア */}
          <Animated.View entering={FadeInUp.delay(300).springify()} style={styles.inputContainer}>
            <BlurView intensity={80} tint="dark" style={styles.inputBlur}>
              <TouchableOpacity style={styles.iconButton}>
                <Mic color="#A0A0A0" size={22} />
              </TouchableOpacity>
              <TextInput
                style={styles.textInput}
                placeholder="思考を入力... (例: 未知への探求心について)"
                placeholderTextColor="#666"
                value={inputText}
                onChangeText={setInputText}
                multiline
              />
              <SiriGlowButton onPress={handleSend} />
            </BlurView>
          </Animated.View>

        </View>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}

const BrainIcon = (props: any) => <Sparkles {...props} />; // 一時的にSparklesをBrain代わりに

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  
  // 背景オーブ
  bgGlow1: { position: 'absolute', top: '-10%', left: '-20%', width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#4B0082', opacity: 0.5, filter: 'blur(100px)' as any },
  bgGlow2: { position: 'absolute', bottom: '10%', right: '-20%', width: width*0.7, height: width*0.7, borderRadius: width, backgroundColor: '#00BFFF', opacity: 0.4, filter: 'blur(100px)' as any },
  
  inner: { flex: 1, paddingTop: Platform.OS === 'web' ? 80 : 100 },

  header: { alignItems: 'center', marginBottom: 24 },
  title: { color: '#FFF', fontSize: 28, fontWeight: '800', fontFamily: 'Outfit_900Black', letterSpacing: 2 },
  subtitle: { color: '#888', fontSize: 12, fontFamily: 'Outfit_400Regular', marginTop: 4, letterSpacing: 1 },

  scrollContent: { paddingHorizontal: 20, paddingBottom: 120 },

  messageWrapper: { flexDirection: 'row', alignItems: 'flex-end', marginBottom: 20 },
  messageUserWrapper: { justifyContent: 'flex-end' },
  messageAiWrapper: { justifyContent: 'flex-start' },

  aiAvatar: { width: 30, height: 30, borderRadius: 15, justifyContent: 'center', alignItems: 'center', marginRight: 10, shadowColor: '#A020F0', shadowOpacity: 0.8, shadowRadius: 10, shadowOffset: { width:0, height:0 } },

  messageBubble: { maxWidth: '75%', paddingHorizontal: 18, paddingVertical: 14, borderRadius: 24, overflow: 'hidden' },
  messageUser: { backgroundColor: 'rgba(255, 255, 255, 0.15)', borderBottomRightRadius: 6, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  messageAi: { backgroundColor: 'rgba(10, 10, 20, 0.8)', borderBottomLeftRadius: 6, borderWidth: 1, borderColor: 'rgba(160, 32, 240, 0.3)' },
  
  aiGlowEffect: { position: 'absolute', top: -10, left: -10, right: -10, bottom: -10, backgroundColor: 'rgba(0, 212, 255, 0.05)' },
  
  messageText: { color: '#E0E0E0', fontSize: 15, lineHeight: 22, fontFamily: 'Outfit_400Regular' },

  inputContainer: { position: 'absolute', bottom: Platform.OS === 'ios' ? 30 : 20, left: 16, right: 16 },
  inputBlur: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 12, paddingVertical: 12, borderRadius: 30, backgroundColor: 'rgba(30,30,30,0.4)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  
  iconButton: { padding: 8 },
  textInput: { flex: 1, color: '#FFF', fontSize: 15, marginHorizontal: 8, maxHeight: 100, fontFamily: 'Outfit_400Regular' },

  siriGlow: { position: 'absolute', top: -4, left: -4, right: -4, bottom: -4, borderRadius: 24, backgroundColor: '#00D4FF', filter: 'blur(8px)' as any },
  sendButton: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', shadowColor: '#A020F0', shadowOpacity: 0.5, shadowRadius: 10, shadowOffset: { width:0, height:0 } }
});
