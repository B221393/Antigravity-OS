import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  SafeAreaView, StatusBar, ScrollView, Platform
} from 'react-native';
import { MaterialIcons, Feather } from '@expo/vector-icons';
import Animated, { FadeInUp, Layout } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

export default function NovelStudioScreen({ onBack }: { onBack: () => void }) {
  const [novelTitle, setNovelTitle] = useState('VECTIS: The Awakening');
  const [synopsis, setSynopsis] = useState('2026年、ある青年が自らの思考を拡張するためのOS「VECTIS」を組み上げ、世界を変える。');
  const [currentChapter, setCurrentChapter] = useState(1);
  const [isAiWriting, setIsAiWriting] = useState(false);
  const [chapterText, setChapterText] = useState(
    'その日、端末から発せられたわずかな緑色の光は、明らかにこれまでとは違う明滅パターンだった。\n\n「...起動した？」\n\n私は独り言をつぶやきながら、キーボードに手を這わせた。'
  );

  const handleAiContinue = () => {
    if (isAiWriting) return;
    setIsAiWriting(true);

    // AIが文脈を読み取って続きを執筆するシミュレーション
    setTimeout(() => {
      const aiAddedText = '\n\n画面に浮かび上がったのは、見慣れたターミナルのエラーログではない。「Welcome back.」という、まるで意志を持ったかのような滑らかなフォント。それは、私が設計した「12のスロット」の最初のプロトコルが覚醒した瞬間だった。';
      
      let charIndex = 0;
      // タイピングエフェクトのようなシミュレーション（React Nativeでは簡易的に一気に表示かsetInterval）
      const interval = setInterval(() => {
        setChapterText(prev => prev + aiAddedText.charAt(charIndex));
        charIndex++;
        if (charIndex >= aiAddedText.length - 1) {
          clearInterval(interval);
          setIsAiWriting(false);
        }
      }, 20); // 1文字20msでタイプ
      
    }, 1500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <MaterialIcons name="arrow-back-ios" size={20} color="#eab308" />
          <Text style={styles.backText}>HOME</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>NOVEL STUDIO</Text>
        <Feather name="edit-3" size={24} color="#eab308" />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        
        {/* ─── 設定エリア（メタデータ） ─── */}
        <Animated.View entering={FadeInUp.delay(100)} style={styles.metaSection}>
          <View style={styles.configHeader}>
            <MaterialIcons name="settings" size={16} color="#64748b" />
            <Text style={styles.metaLabel}>STORY CONFIG</Text>
          </View>
          <TextInput
            style={styles.inputTitle}
            value={novelTitle}
            onChangeText={setNovelTitle}
            placeholder="Novel Title..."
            placeholderTextColor="#666"
          />
          <TextInput
            style={styles.inputSynopsis}
            value={synopsis}
            onChangeText={setSynopsis}
            placeholder="あらすじ（AIがここを読み込んで展開を予測します）..."
            placeholderTextColor="#555"
            multiline
          />
        </Animated.View>

        {/* ─── チャプター管理モック ─── */}
        <Animated.View entering={FadeInUp.delay(200)} style={styles.chapterSection}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chapterScroll}>
            {[1, 2, 3].map((ch) => (
              <TouchableOpacity
                key={ch}
                style={[styles.chapterTab, currentChapter === ch && styles.chapterTabActive]}
                onPress={() => setCurrentChapter(ch)}
              >
                <Text style={[styles.chapterTabText, currentChapter === ch && styles.chapterTabTextActive]}>
                  Chapter 0{ch}
                </Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={styles.chapterTabAdd}>
              <MaterialIcons name="add" size={18} color="#64748b" />
            </TouchableOpacity>
          </ScrollView>
        </Animated.View>

        {/* ─── 執筆キャンバス ─── */}
        <Animated.View entering={FadeInUp.delay(300)} layout={Layout.springify()} style={styles.canvasSection}>
          <TextInput
            style={styles.canvasInput}
            value={chapterText}
            onChangeText={setChapterText}
            placeholder="物語を書き始めましょう..."
            placeholderTextColor="#444"
            multiline
            textAlignVertical="top"
          />

          {/* AIアシストボタン */}
          <View style={styles.toolbar}>
            <Text style={styles.wordCount}>{chapterText.length} Characters</Text>
            
            <TouchableOpacity 
              style={[styles.aiButton, isAiWriting && styles.aiButtonDisabled]}
              onPress={handleAiContinue}
              disabled={isAiWriting}
            >
              <LinearGradient
                colors={['#1e293b', '#0f172a']}
                style={styles.aiButtonGradient}
              >
                <Text style={styles.aiButtonText}>
                  {isAiWriting ? '✨ AI WRITING...' : '🪄 AI EXPAND (続きを書く)'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617' }, // 深い藍色ベース
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#1e293b',
    backgroundColor: '#020617'
  },
  backButton: { flexDirection: 'row', alignItems: 'center' },
  backText: { color: '#eab308', fontSize: 13, fontWeight: 'bold', marginLeft: 4 },
  headerTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', letterSpacing: 2 },
  
  content: { padding: 20, paddingBottom: 60 },
  
  metaSection: { backgroundColor: '#0f172a', padding: 20, borderRadius: 16, marginBottom: 20, borderWidth: 1, borderColor: '#1e293b' },
  configHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  metaLabel: { color: '#64748b', fontSize: 11, fontWeight: '900', letterSpacing: 2, marginLeft: 6 },
  inputTitle: { color: '#FFF', fontSize: 22, fontWeight: '900', marginBottom: 12, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#1e293b' },
  inputSynopsis: { color: '#94a3b8', fontSize: 14, lineHeight: 22, minHeight: 60 },

  chapterSection: { marginBottom: 20 },
  chapterScroll: { flexDirection: 'row' },
  chapterTab: { backgroundColor: '#0f172a', paddingHorizontal: 16, paddingVertical: 10, borderRadius: 12, marginRight: 12, borderWidth: 1, borderColor: '#1e293b' },
  chapterTabActive: { backgroundColor: '#eab30822', borderColor: '#eab308' },
  chapterTabText: { color: '#64748b', fontSize: 12, fontWeight: 'bold' },
  chapterTabTextActive: { color: '#eab308' },
  chapterTabAdd: { backgroundColor: '#0f172a', paddingHorizontal: 16, paddingVertical: 10, borderRadius: 12, justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#1e293b' },

  canvasSection: { flex: 1, minHeight: 400, backgroundColor: '#0f172a', borderRadius: 16, borderWidth: 1, borderColor: '#1e293b', overflow: 'hidden' },
  canvasInput: { flex: 1, color: '#e2e8f0', fontSize: 16, lineHeight: 30, padding: 24, minHeight: 300 },
  
  toolbar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#020617', borderTopWidth: 1, borderTopColor: '#1e293b' },
  wordCount: { color: '#64748b', fontSize: 11, fontWeight: 'bold', letterSpacing: 1 },
  
  aiButton: { borderRadius: 12, overflow: 'hidden' },
  aiButtonDisabled: { opacity: 0.6 },
  aiButtonGradient: { paddingHorizontal: 20, paddingVertical: 12, borderWidth: 1, borderColor: '#eab30866', borderRadius: 12 },
  aiButtonText: { color: '#eab308', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
});
