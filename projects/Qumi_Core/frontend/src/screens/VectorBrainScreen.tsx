import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TextInput, TouchableOpacity,
  SafeAreaView, StatusBar, ScrollView, Animated as RNAnimated
} from 'react-native';
import { MaterialIcons, Ionicons } from '@expo/vector-icons';
import Animated, { FadeIn, FadeInUp, FadeInDown, Layout } from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import ThoughtCapture from '../components/ThoughtCapture';

export default function VectorBrainScreen({ onBack }: { onBack: () => void }) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [capturedSoul, setCapturedSoul] = useState<any>(null);

  // 検索アクション（デモ用）
  const handleSearch = () => {
    if (!query.trim()) return;
    setIsSearching(true);
    setResults([]);

    // AIによる「768次元での意味類似度検索」をシミュレート
    setTimeout(() => {
      setIsSearching(false);
      setResults([
        {
          id: '1',
          score: 0.942, // コサイン類似度
          title: 'STRATEGIC_INTEL_LOG のメモ',
          snippet: `「...${query}について、次回Brexaの面接で語る際は、単なる仕組み化という言葉ではなく『未知への探求心』に言い換える...」`
        },
        {
          id: '2',
          score: 0.825,
          title: 'AI_LAB/moltbot の仕様書',
          snippet: `「...関連するアーキテクチャとして、APIキーを排除したローカル完結型の通信プロトコルについて以前検討した形跡があります...」`
        }
      ]);
    }, 2000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* ─── Header ─── */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <MaterialIcons name="arrow-back-ios" size={20} color="#3b82f6" />
          <Text style={styles.backText}>HOME</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>VECTOR BRAIN</Text>
        <Ionicons name="analytics" size={24} color="#3b82f6" />
      </View>

      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        
        <View style={styles.heroSection}>
          <Text style={styles.heroTitle}>768D SEMANTIC SEARCH</Text>
          <Text style={styles.heroSubtitle}>あなたの「外部脳」にアクセスします。キーワードが一致しなくても、"意味の近さ" で過去の自分を探し出します。</Text>
        </View>

        {/* 音声思考キャプチャ */}
        <ThoughtCapture onResult={(res) => {
          console.log("Captured Soul:", res);
          setCapturedSoul(res);
        }} />

        {capturedSoul && (
          <Animated.View 
            entering={FadeInDown} 
            style={styles.capturedSoulCard}
          >
            <View style={styles.capturedSoulHeader}>
              <Ionicons name="sparkles" size={20} color="#fbbf24" />
              <Text style={styles.capturedSoulTitle}>CAPTURED SOUL STRUCTURE</Text>
              <TouchableOpacity onPress={() => setCapturedSoul(null)}>
                <Ionicons name="close" size={20} color="#64748b" />
              </TouchableOpacity>
            </View>
            
            <View style={styles.capturedSoulContent}>
              <Text style={styles.soulLabel}>TITLE:</Text>
              <Text style={styles.soulValue}>{capturedSoul.structured_result.title || capturedSoul.transcription}</Text>
              
              <Text style={styles.soulLabel}>CORE PHILOSOPHY:</Text>
              <Text style={styles.soulValue}>{capturedSoul.structured_result.core_philosophy}</Text>
              
              <Text style={styles.soulLabel}>ACTIONABLE INSIGHTS:</Text>
              {Array.isArray(capturedSoul.structured_result.actionable_insights) ? (
                capturedSoul.structured_result.actionable_insights.map((insight: string, i: number) => (
                  <Text key={i} style={styles.soulValue}>• {insight}</Text>
                ))
              ) : (
                <Text style={styles.soulValue}>{capturedSoul.structured_result.actionable_insights}</Text>
              )}
            </View>
            
            <View style={styles.transcriptionSource}>
              <Text style={styles.sourceText}>Source: "{capturedSoul.transcription}"</Text>
            </View>
          </Animated.View>
        )}

        {/* 検索バー */}
        <Animated.View style={styles.searchBox} entering={FadeInUp.delay(200)}>
          <Ionicons name="search" size={20} color="#3b82f6" style={{ marginRight: 12 }} />
          <TextInput
            style={styles.searchInput}
            placeholder="なんとなく思い出した曖昧な記憶をここに..."
            placeholderTextColor="#555"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={handleSearch}
          />
          <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
            <Text style={styles.searchButtonText}>SEARCH</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* 検索アニメーション */}
        {isSearching && (
          <Animated.View entering={FadeIn} style={styles.loadingArea}>
            <LinearGradient
              colors={['#1a1a1a', '#000000']}
              style={styles.loadingBox}
            >
              <Ionicons name="hardware-chip" size={32} color="#3b82f6" />
              <Text style={styles.loadingText}>CALCULATING VECTOR DISTANCE...</Text>
              <Text style={styles.loadingDesc}>PC母艦（192.168.x.x）のChromaデータベースと通信中...</Text>
            </LinearGradient>
          </Animated.View>
        )}

        {/* 検索結果 */}
        {!isSearching && results.length > 0 && (
          <View style={styles.resultsArea}>
            <Text style={styles.resultHeader}>// NEAREST MEMORIES FOUND</Text>
            {results.map((res, index) => (
              <Animated.View 
                key={res.id} 
                style={styles.resultCard}
                entering={FadeInUp.delay(index * 200).springify().damping(15)}
                layout={Layout.springify()}
              >
                <View style={styles.resultCardHeader}>
                  <Text style={styles.resultTitle}>{res.title}</Text>
                  <View style={styles.scoreBadge}>
                    <Text style={styles.scoreText}>MATCH: {res.score}</Text>
                  </View>
                </View>
                <Text style={styles.resultSnippet}>{res.snippet}</Text>
              </Animated.View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#020617' }, // 深い藍色ベースのハッカー色
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1, borderBottomColor: '#0f172a',
    backgroundColor: 'rgba(2, 6, 23, 0.9)'
  },
  backButton: { flexDirection: 'row', alignItems: 'center' },
  backText: { color: '#3b82f6', fontSize: 14, fontWeight: 'bold' },
  headerTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', letterSpacing: 2 },
  
  content: { padding: 24, paddingBottom: 60 },
  
  heroSection: { alignItems: 'center', marginTop: 24, marginBottom: 40 },
  heroTitle: { color: '#3b82f6', fontSize: 24, fontWeight: '900', letterSpacing: 2, marginBottom: 12 },
  heroSubtitle: { color: '#64748b', fontSize: 14, textAlign: 'center', lineHeight: 22, paddingHorizontal: 16 },

  searchBox: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#0f172a', borderWidth: 1, borderColor: '#1e293b',
    borderRadius: 16, padding: 8, paddingHorizontal: 16, marginBottom: 40
  },
  searchInput: { flex: 1, color: '#FFF', fontSize: 15, paddingVertical: 16, minHeight: 50 },
  searchButton: { backgroundColor: '#3b82f6', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 12 },
  searchButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 13, letterSpacing: 1 },

  loadingArea: { alignItems: 'center', marginTop: 20 },
  loadingBox: { padding: 32, borderRadius: 24, alignItems: 'center', width: '100%', borderWidth: 1, borderColor: '#1e293b' },
  loadingText: { color: '#3b82f6', fontSize: 12, fontWeight: '900', letterSpacing: 2, marginTop: 16, marginBottom: 8 },
  loadingDesc: { color: '#475569', fontSize: 10 },

  resultsArea: { marginTop: 10 },
  resultHeader: { color: '#475569', fontSize: 12, fontWeight: 'bold', letterSpacing: 2, marginBottom: 16 },
  
  resultCard: { backgroundColor: '#0f172a', padding: 20, borderRadius: 16, marginBottom: 16, borderWidth: 1, borderColor: '#1e293b', borderLeftWidth: 4, borderLeftColor: '#3b82f6' },
  resultCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  resultTitle: { color: '#FFF', fontSize: 16, fontWeight: 'bold', flex: 1 },
  scoreBadge: { backgroundColor: '#1e3a8a', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, marginLeft: 12 },
  scoreText: { color: '#93c5fd', fontSize: 10, fontWeight: '900', letterSpacing: 1 },
  resultSnippet: { color: '#94a3b8', fontSize: 14, lineHeight: 22 },

  capturedSoulCard: {
    backgroundColor: 'rgba(30, 41, 59, 0.8)',
    borderRadius: 24,
    padding: 24,
    marginBottom: 40,
    borderWidth: 1,
    borderColor: '#fbbf24',
    shadowColor: '#fbbf24',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
  },
  capturedSoulHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  capturedSoulTitle: { color: '#fbbf24', fontSize: 12, fontWeight: '900', letterSpacing: 2, flex: 1, marginLeft: 10 },
  capturedSoulContent: { gap: 16 },
  soulLabel: { color: '#64748b', fontSize: 10, fontWeight: 'bold', letterSpacing: 1 },
  soulValue: { color: '#f8fafc', fontSize: 15, lineHeight: 24 },
  transcriptionSource: { marginTop: 20, paddingTop: 16, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.05)' },
  sourceText: { color: '#475569', fontSize: 12, fontStyle: 'italic' },
});
