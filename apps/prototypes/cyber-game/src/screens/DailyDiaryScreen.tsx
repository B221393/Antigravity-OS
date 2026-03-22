import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  SafeAreaView, StatusBar, ScrollView, Platform
} from 'react-native';
import { MaterialIcons, Feather } from '@expo/vector-icons';
import Animated, { FadeIn, FadeInUp, Layout } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

type Mood = 'great' | 'good' | 'neutral' | 'bad';
const MOOD_COLORS = {
  great: '#00FF99', // グリーン
  good: '#5AC8FA',  // ブルー
  neutral: '#FFCC00',// イエロー
  bad: '#FF3B30'    // レッド
};
const MOOD_LABELS = {
  great: '最高 / THE BEST',
  good: '良い / GOOD',
  neutral: '普通 / NEUTRAL',
  bad: '疲労 / EXHAUSTED'
};

export default function DailyDiaryScreen({ onBack }: { onBack: () => void }) {
  const [diaryText, setDiaryText] = useState('');
  const [mood, setMood] = useState<Mood>('neutral');
  const [isProcessing, setIsProcessing] = useState(false);
  const [entries, setEntries] = useState<any[]>([
    {
      id: '1',
      date: '2026/03/21',
      text: '面接の戦略について深く考えた。Antigravityという名前をやめて、抽象化した表現を使うことに決めた。',
      mood: 'good',
      aiComment: '素晴らしい洞察です。客観視できる能力は就職活動で非常に高く評価されます。'
    }
  ]);

  const handleSave = () => {
    if (!diaryText.trim()) return;
    setIsProcessing(true);

    // AIによる「日記振り返りコメント生成」をシミュレート
    setTimeout(() => {
      const newEntry = {
        id: Date.now().toString(),
        date: new Date().toLocaleDateString('ja-JP'),
        text: diaryText,
        mood: mood,
        aiComment: mood === 'bad' 
          ? '今日はいろいろあってお疲れのようですね。まずはゆっくり休んで、明日また整理しましょう。'
          : 'その記録は未来の自分にとっての大きな資産になります。今日も一日お疲れ様でした！'
      };
      setEntries([newEntry, ...entries]);
      setDiaryText('');
      setMood('neutral');
      setIsProcessing(false);
      if (Platform.OS === 'web') alert('日記がローカルに保存され、AIの分析が完了しました。');
    }, 1500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <MaterialIcons name="arrow-back-ios" size={20} color="#f43f5e" />
          <Text style={styles.backText}>HOME</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>DAILY LOG</Text>
        <Feather name="book-open" size={24} color="#f43f5e" />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        
        {/* ─── 日記記入エリア ─── */}
        <Animated.View entering={FadeInUp.delay(100)} style={styles.editorSection}>
          <View style={styles.dateHeader}>
            <Text style={styles.todayDate}>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</Text>
            <Text style={styles.timeClock}>TODAY'S RECORD</Text>
          </View>

          <View style={styles.moodSelector}>
            {(Object.keys(MOOD_COLORS) as Mood[]).map((m) => (
              <TouchableOpacity 
                key={m} 
                onPress={() => setMood(m)}
                style={[
                  styles.moodButton, 
                  mood === m && { backgroundColor: `${MOOD_COLORS[m]}22`, borderColor: MOOD_COLORS[m] }
                ]}
              >
                <View style={[styles.moodDot, { backgroundColor: MOOD_COLORS[m] }]} />
                {mood === m && <Text style={[styles.moodLabel, { color: MOOD_COLORS[m] }]}>{MOOD_LABELS[m].split('/')[0]}</Text>}
              </TouchableOpacity>
            ))}
          </View>

          <TextInput
            style={styles.diaryInput}
            placeholder="今日はどんな一日でしたか？（AIが最後に振り返りコメントをくれます）"
            placeholderTextColor="#555"
            multiline
            value={diaryText}
            onChangeText={setDiaryText}
            textAlignVertical="top"
          />

          <TouchableOpacity 
            style={[styles.saveButton, !diaryText.trim() && styles.saveButtonDisabled]} 
            onPress={handleSave}
            disabled={!diaryText.trim() || isProcessing}
          >
            <LinearGradient
              colors={['#e11d48', '#f43f5e']}
              start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              style={styles.saveGradient}
            >
              <Text style={styles.saveButtonText}>
                {isProcessing ? 'AI 分析中...' : 'SAVE JOURNAL'}
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        </Animated.View>

        {/* ─── 過去のログエリア ─── */}
        <View style={styles.historySection}>
          <Text style={styles.historySectionTitle}>// PREVIOUS LOGS</Text>
          
          {entries.map((entry, index) => (
            <Animated.View 
              key={entry.id} 
              entering={FadeInUp.delay(200 + index * 100).springify()}
              layout={Layout.springify()}
              style={[styles.entryCard, { borderLeftColor: MOOD_COLORS[entry.mood as Mood] }]}
            >
              <View style={styles.entryHeader}>
                <Text style={styles.entryDate}>{entry.date}</Text>
                <View style={[styles.moodTag, { backgroundColor: `${MOOD_COLORS[entry.mood as Mood]}22` }]}>
                  <Text style={[styles.moodTagText, { color: MOOD_COLORS[entry.mood as Mood] }]}>{MOOD_LABELS[entry.mood as Mood]}</Text>
                </View>
              </View>
              <Text style={styles.entryText}>{entry.text}</Text>
              
              <View style={styles.aiInsightBox}>
                <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
                  <MaterialIcons name="auto-awesome" size={14} color="#f43f5e" style={{ marginRight: 6 }} />
                  <Text style={styles.aiInsightTitle}>AI REFLECTION</Text>
                </View>
                <Text style={styles.aiInsightText}>{entry.aiComment}</Text>
              </View>
            </Animated.View>
          ))}
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#09090b' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#27272a',
    backgroundColor: 'rgba(9, 9, 11, 0.95)'
  },
  backButton: { flexDirection: 'row', alignItems: 'center' },
  backText: { color: '#f43f5e', fontSize: 13, fontWeight: 'bold', marginLeft: 4 },
  headerTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', letterSpacing: 2 },
  
  content: { padding: 20, paddingBottom: 60 },
  
  editorSection: { marginBottom: 40 },
  dateHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 20 },
  todayDate: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 1 },
  timeClock: { color: '#f43f5e', fontSize: 10, fontWeight: 'bold', letterSpacing: 2 },

  moodSelector: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  moodButton: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10, borderRadius: 20, backgroundColor: '#18181b', borderWidth: 1, borderColor: '#27272a' },
  moodDot: { width: 10, height: 10, borderRadius: 5, marginRight: 6 },
  moodLabel: { fontSize: 11, fontWeight: '900' },

  diaryInput: {
    backgroundColor: '#18181b', borderWidth: 1, borderColor: '#27272a',
    borderRadius: 16, padding: 20, color: '#FFF', fontSize: 15, lineHeight: 24,
    minHeight: 180, marginBottom: 20
  },
  saveButton: { borderRadius: 16, overflow: 'hidden' },
  saveButtonDisabled: { opacity: 0.5 },
  saveGradient: { paddingVertical: 18, alignItems: 'center', justifyContent: 'center' },
  saveButtonText: { color: '#FFF', fontSize: 13, fontWeight: '900', letterSpacing: 2 },

  historySection: { marginTop: 20 },
  historySectionTitle: { color: '#52525b', fontSize: 12, fontWeight: '900', letterSpacing: 3, marginBottom: 20 },
  
  entryCard: {
    backgroundColor: '#18181b', borderRadius: 16, padding: 20, marginBottom: 16,
    borderLeftWidth: 4, borderWidth: 1, borderColor: '#27272a'
  },
  entryHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  entryDate: { color: '#a1a1aa', fontSize: 12, fontWeight: 'bold', letterSpacing: 1 },
  moodTag: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  moodTagText: { fontSize: 9, fontWeight: '900', letterSpacing: 1 },
  
  entryText: { color: '#e4e4e7', fontSize: 15, lineHeight: 24, marginBottom: 16 },
  
  aiInsightBox: { backgroundColor: '#27272a44', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#f43f5e22' },
  aiInsightTitle: { color: '#f43f5e', fontSize: 10, fontWeight: '900', letterSpacing: 2 },
  aiInsightText: { color: '#a1a1aa', fontSize: 13, lineHeight: 20 },
});
