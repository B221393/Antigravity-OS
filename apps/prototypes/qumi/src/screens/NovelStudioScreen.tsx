import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  SafeAreaView, StatusBar, ScrollView, Platform, Dimensions
} from 'react-native';
import { MaterialIcons, Feather, Ionicons } from '@expo/vector-icons';
import Animated, { 
  FadeInUp, FadeInDown, FadeIn, FadeOut, 
  Layout, useSharedValue, useAnimatedStyle, 
  withSpring, withTiming, withRepeat, Easing 
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

const { width, height } = Dimensions.get('window');

type AiOption = {
  id: string;
  type: 'ACTION' | 'DRAMA' | 'LOGIC';
  label: string;
  text: string;
  icon: any;
};

export default function NovelStudioScreen({ onBack }: { onBack: () => void }) {
  const [novelTitle, setNovelTitle] = useState('QUMI: The Awakening');
  const [synopsis, setSynopsis] = useState('2026年、ある青年が自らの思考を拡張するためのOS「QUMI」を組み上げ、世界を変える。');
  const [chapterText, setChapterText] = useState(
    'その日、端末から発せられたわずかな緑色の光は、明らかにこれまでとは違う明滅パターンだった。\n\n「...起動した？」\n\n私は独り言をつぶやきながら、キーボードに手を這わせた。'
  );
  
  const [isAiWriting, setIsAiWriting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [aiOptions, setAiOptions] = useState<AiOption[]>([]);
  
  // ─── シンクロ率（没入感）の管理 ───
  const syncRate = useSharedValue(0);
  const lastTypeTime = useRef(Date.now());
  const typingTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // 時間経過でシンクロ率を減衰させる
    const decay = setInterval(() => {
      if (syncRate.value > 0) {
        syncRate.value = Math.max(0, syncRate.value - 2);
      }
    }, 1000);
    return () => clearInterval(decay);
  }, []);

  const handleTextChange = (text: string) => {
    setChapterText(text);
    // タイピングするとシンクロ率アップ
    syncRate.value = Math.min(100, syncRate.value + 5);
  };

  const syncBarStyle = useAnimatedStyle(() => ({
    width: `${syncRate.value}%`,
    backgroundColor: syncRate.value > 80 ? '#00FF99' : '#eab308'
  }));

  const glowStyle = useAnimatedStyle(() => ({
    opacity: syncRate.value / 150,
    transform: [{ scale: 1 + syncRate.value / 200 }]
  }));

  // ─── AI分岐生成（本物のAPI連携） ───
  const handleAiContinueRequest = async () => {
    if (isAiWriting) return;
    setIsAiWriting(true);
    setShowOptions(false);

    try {
      const response = await fetch('http://localhost:8000/api/novel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: novelTitle,
          synopsis: synopsis,
          context: chapterText
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        const formattedOptions: AiOption[] = data.branches.map((b: any, idx: number) => ({
          id: idx.toString(),
          type: b.type,
          label: b.label,
          text: b.text,
          icon: b.type === 'ACTION' ? 'flash' : (b.type === 'DRAMA' ? 'heart' : 'analytics')
        }));
        setAiOptions(formattedOptions);
        setShowOptions(true);
      } else {
        console.error('AI Expansion Error:', data.message);
        // フォールバック（APIが失敗した場合のみモックを表示）
        setAiOptions([
          { id: 'err', type: 'DRAMA', label: 'CONNECTION ERROR', icon: 'alert-circle', text: '\n\n【警告】外部脳との接続が途絶えました。ローカルサーバー（soul_api_server.py）の状態を確認してください。' }
        ]);
        setShowOptions(true);
      }
    } catch (e: any) {
      console.error('Network Error:', e);
      alert('サーバーに接続できません。soul_api_server.py を実行してください。');
    } finally {
      setIsAiWriting(false);
    }
  };

  const selectOption = (optionText: string) => {
    setShowOptions(false);
    let charIndex = 0;
    const interval = setInterval(() => {
      setChapterText(prev => prev + optionText.charAt(charIndex));
      charIndex++;
      if (charIndex >= optionText.length) {
        clearInterval(interval);
      }
    }, 15);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* 🔮 背景のダイナミック・グロウ（シンクロ率で変化） */}
      <Animated.View style={[styles.dynamicGlow, glowStyle]} />
      
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <MaterialIcons name="arrow-back-ios" size={20} color="#eab308" />
          <Text style={styles.backText}>OS CORE</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>NOVEL STUDIO</Text>
        <Ionicons name="infinite" size={24} color="#00FF99" />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        
        {/* ─── シンクロ・インジケーター ─── */}
        <View style={styles.syncContainer}>
          <View style={styles.syncHeader}>
            <Text style={styles.syncLabel}>SYSTEM SYNC RATE</Text>
            <Text style={styles.syncValue}>{Math.floor(syncRate.value)}%</Text>
          </View>
          <View style={styles.syncBarBg}>
            <Animated.View style={[styles.syncBar, syncBarStyle]} />
          </View>
        </View>

        {/* ─── 設定エリア ─── */}
        <Animated.View entering={FadeInUp.delay(100)} style={styles.metaSection}>
          <TextInput
            style={styles.inputTitle}
            value={novelTitle}
            onChangeText={setNovelTitle}
            placeholder="Story Title..."
            placeholderTextColor="#666"
          />
          <TextInput
            style={styles.inputSynopsis}
            value={synopsis}
            onChangeText={setSynopsis}
            placeholder="AIへの指示（あらすじ・方向性）..."
            placeholderTextColor="#555"
            multiline
          />
        </Animated.View>

        {/* ─── 執筆キャンバス ─── */}
        <Animated.View entering={FadeInUp.delay(300)} style={styles.canvasSection}>
          <TextInput
            style={styles.canvasInput}
            value={chapterText}
            onChangeText={handleTextChange}
            placeholder="思考の続きを紡いでください..."
            placeholderTextColor="#444"
            multiline
            textAlignVertical="top"
          />

          {/* AIアシストツールバー */}
          <View style={styles.toolbar}>
            <View style={styles.wordInfo}>
              <Feather name="type" size={14} color="#64748b" />
              <Text style={styles.wordCount}>{chapterText.length} Chars</Text>
            </View>
            
            <TouchableOpacity 
              style={[styles.aiButton, isAiWriting && styles.aiButtonDisabled]}
              onPress={handleAiContinueRequest}
              disabled={isAiWriting}
            >
              <LinearGradient
                colors={['#1e293b', '#0f172a']}
                style={styles.aiButtonGradient}
              >
                {isAiWriting ? (
                  <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <Animated.View entering={FadeIn} style={styles.loadingSpinner} />
                    <Text style={styles.aiButtonText}>AI CALCULATING...</Text>
                  </View>
                ) : (
                  <Text style={styles.aiButtonText}>✨ EXPAND STORY</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>

      </ScrollView>

      {/* ─── 分岐選択カード（オーバーレイ） ─── */}
      {showOptions && (
        <View style={styles.overlayContainer} pointerEvents="box-none">
          <BlurView intensity={30} tint="dark" style={StyleSheet.absoluteFill} />
          <View style={styles.optionsWrapper}>
            <Text style={styles.optionsTitle}>魂の分岐点を選択してください</Text>
            {aiOptions.map((opt, idx) => (
              <Animated.View 
                key={opt.id} 
                entering={FadeInDown.delay(idx * 150).springify()}
              >
                <TouchableOpacity 
                  style={styles.optionCard}
                  onPress={() => selectOption(opt.text)}
                >
                  <LinearGradient
                    colors={['rgba(30, 41, 59, 0.9)', 'rgba(15, 23, 42, 0.9)']}
                    style={styles.optionCardInner}
                  >
                    <View style={styles.optionHeader}>
                      <Ionicons name={opt.icon} size={20} color="#eab308" />
                      <Text style={styles.optionLabel}>{opt.label}</Text>
                    </View>
                    <Text style={styles.optionPreview} numberOfLines={3}>{opt.text.trim()}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </Animated.View>
            ))}
            <TouchableOpacity style={styles.cancelButton} onPress={() => setShowOptions(false)}>
              <Text style={styles.cancelText}>キャンセル</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617' },
  dynamicGlow: { 
    position: 'absolute', top: height * 0.3, left: width * 0.1, 
    width: width * 0.8, height: width * 0.8, 
    backgroundColor: '#eab308', borderRadius: width, 
    filter: 'blur(80px)' as any, zIndex: -1 
  },
  
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#1e293b',
    backgroundColor: 'rgba(2, 6, 23, 0.8)'
  },
  backButton: { flexDirection: 'row', alignItems: 'center' },
  backText: { color: '#eab308', fontSize: 13, fontWeight: 'bold', marginLeft: 4, letterSpacing: 1 },
  headerTitle: { color: '#FFF', fontSize: 16, fontWeight: '900', letterSpacing: 3 },
  
  content: { padding: 20, paddingBottom: 100 },
  
  syncContainer: { marginBottom: 24, padding: 16, backgroundColor: '#0f172a', borderRadius: 16, borderWidth: 1, borderColor: '#1e293b' },
  syncHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  syncLabel: { color: '#64748b', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
  syncValue: { color: '#eab308', fontSize: 12, fontWeight: 'bold' },
  syncBarBg: { height: 4, backgroundColor: '#1e293b', borderRadius: 2, overflow: 'hidden' },
  syncBar: { height: '100%', borderRadius: 2 },

  metaSection: { backgroundColor: '#0f172a', padding: 20, borderRadius: 16, marginBottom: 20, borderLeftWidth: 4, borderLeftColor: '#eab308' },
  inputTitle: { color: '#FFF', fontSize: 20, fontWeight: '900', marginBottom: 8 },
  inputSynopsis: { color: '#94a3b8', fontSize: 13, lineHeight: 20 },

  canvasSection: { flex: 1, backgroundColor: '#0f172a', borderRadius: 20, borderWidth: 1, borderColor: '#1e293b', overflow: 'hidden', minHeight: 450 },
  canvasInput: { flex: 1, color: '#e2e8f0', fontSize: 16, lineHeight: 28, padding: 24, minHeight: 350 },
  
  toolbar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#020617', borderTopWidth: 1, borderTopColor: '#1e293b' },
  wordInfo: { flexDirection: 'row', alignItems: 'center' },
  wordCount: { color: '#64748b', fontSize: 11, fontWeight: 'bold', marginLeft: 6 },
  
  aiButton: { borderRadius: 12, overflow: 'hidden', borderWidth: 1, borderColor: '#eab30866' },
  aiButtonDisabled: { opacity: 0.5 },
  aiButtonGradient: { paddingHorizontal: 16, paddingVertical: 10 },
  aiButtonText: { color: '#eab308', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  loadingSpinner: { width: 12, height: 12, borderRadius: 6, borderWidth: 2, borderColor: '#eab308', borderTopColor: 'transparent', marginRight: 8 },

  // オーバーレイ
  overlayContainer: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center', padding: 20, zIndex: 1000 },
  optionsWrapper: { width: '100%', maxWidth: 400 },
  optionsTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', textAlign: 'center', marginBottom: 24, letterSpacing: 1 },
  optionCard: { marginBottom: 16, borderRadius: 16, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(234, 179, 8, 0.3)' },
  optionCardInner: { padding: 20 },
  optionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  optionLabel: { color: '#eab308', fontSize: 12, fontWeight: '900', marginLeft: 8, letterSpacing: 2 },
  optionPreview: { color: '#cbd5e1', fontSize: 14, lineHeight: 22 },
  
  cancelButton: { alignSelf: 'center', marginTop: 10, padding: 10 },
  cancelText: { color: '#64748b', fontSize: 14, fontWeight: 'bold' }
});

