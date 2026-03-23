import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, Platform, Dimensions, TouchableOpacity, TextInput } from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { BookOpen, Search, ChevronRight, X } from 'lucide-react-native';
import Animated, { FadeInUp, FadeInDown, Layout } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

const WIKI_DB = [
  { 
    id: '1', 
    title: '抽象レイヤーとシステム委譲', 
    category: 'Architecture', 
    content: 'n8nのような視覚的ノード制御（低い抽象度）であっても、LLMのCLIエージェント（高い抽象度）であっても、システムの根幹である「外部の機能へタスクや思考を委譲する」という本質は同一である。エンジニアリングはその技術のレイヤー（抽象度）を行き来する行為にすぎない。' 
  },
  { 
    id: '2', 
    title: 'パーソルAVCと設計開発の未来', 
    category: 'Industry Research', 
    content: 'パーソルAVCにおいて求められる設計開発エンジニアとは、単一のツールに固執せず、常に新しい未知の領域へ飛び込む探求心を持った人材である。馬術部で培った言葉なき対象への観察力や、小売店での適応力が、変化の激しい開発現場における最大の強みとなる。' 
  },
  { 
    id: '3', 
    title: 'Glassmorphism UI Principles', 
    category: 'Design System', 
    content: '美しいUIは単なる装飾ではなく「毎日使いたくなる道具（自己拡張システム）」のモチベーションに直結する。Appleのデザイン言語にあるSquircle（滑らかな角丸）やBlur（すりガラス効果）、そしてコロコロと弾性のあるアニメーションを取り入れることで、認知の負荷を下げる。' 
  },
  { 
    id: '4', 
    title: 'MCP (Model Context Protocol)', 
    category: 'Technology', 
    content: 'コンテキストモデルプロトコル。ローカルの環境（ファイル、API、ターミナル）と大希望言語モデル（Gemini等）を双方向にセキュアに接続するためのオープン標準。Qumi OSのバックエンドルーターにおける中核機能。' 
  }
];

export default function WikiArchiveScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArticle, setSelectedArticle] = useState<any>(null);

  const filteredDB = WIKI_DB.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    doc.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={Platform.OS === 'ios' ? 80 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.header}>
        <Animated.View entering={FadeInDown.springify()} style={styles.headerTop}>
          <LinearGradient colors={['#00FF99', '#00D4FF']} style={styles.iconCircle}>
            <BookOpen color="#FFF" size={28} />
          </LinearGradient>
          <View style={styles.headerTextCol}>
            <Text style={styles.title}>WIKI INTEL</Text>
            <Text style={styles.subtitle}>Open Knowledge Base</Text>
          </View>
        </Animated.View>
        
        {/* Apple Spotlight風 検索バー */}
        <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.searchBar}>
          <Search color="#888" size={20} />
          <TextInput 
            style={styles.searchInput} 
            placeholder="Search external brain..." 
            placeholderTextColor="#666" 
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </Animated.View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {!selectedArticle ? (
          <View style={styles.listContainer}>
             {filteredDB.map((doc, index) => (
                <Animated.View key={doc.id} layout={Layout.springify()} entering={FadeInUp.delay(index * 100).springify().damping(15)}>
                  <TouchableOpacity activeOpacity={0.7} onPress={() => setSelectedArticle(doc)} style={styles.docCardWrapper}>
                    <BlurView intensity={60} tint="dark" style={styles.docCard}>
                      <View style={{ flex: 1 }}>
                        <Text style={styles.docCategory}>{doc.category}</Text>
                        <Text style={styles.docTitle}>{doc.title}</Text>
                      </View>
                      <ChevronRight color="#888" size={20} />
                    </BlurView>
                  </TouchableOpacity>
                </Animated.View>
             ))}
          </View>
        ) : (
          /* Wikipediaライクなハイエンド記事ビュー */
          <Animated.View layout={Layout.springify()} entering={FadeInUp.springify().damping(15)} style={styles.articleView}>
             <BlurView intensity={70} tint="dark" style={styles.articleBlur}>
                <TouchableOpacity style={styles.closeBtn} onPress={() => setSelectedArticle(null)}>
                  <X color="#FFF" size={24} />
                </TouchableOpacity>
                
                <Text style={styles.articleCategory}>{selectedArticle.category}</Text>
                <Text style={styles.articleTitle}>{selectedArticle.title}</Text>
                <View style={styles.articleDivider} />
                <Text style={styles.articleBody}>{selectedArticle.content}</Text>
             </BlurView>
          </Animated.View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow: { position: 'absolute', top: -100, right: -100, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#00FF99', opacity: 0.15, filter: 'blur(100px)' as any },
  
  header: { paddingHorizontal: 20, paddingTop: Platform.OS === 'web' ? 80 : 100, marginBottom: 20, zIndex: 10 },
  headerTop: { flexDirection: 'row', alignItems: 'center', marginBottom: 24 },
  iconCircle: { width: 60, height: 60, borderRadius: 30, justifyContent: 'center', alignItems: 'center', shadowColor: '#00FF99', shadowOpacity: 0.8, shadowRadius: 15 },
  headerTextCol: { marginLeft: 16 },
  title: { color: '#FFF', fontSize: 26, fontWeight: '900', fontFamily: 'Outfit_900Black', letterSpacing: 2 },
  subtitle: { color: '#00FF99', fontSize: 13, fontFamily: 'Outfit_700Bold', marginTop: 4, letterSpacing: 1 },

  searchBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 16, paddingHorizontal: 16, height: 50, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  searchInput: { flex: 1, color: '#FFF', fontSize: 16, fontFamily: 'Outfit_400Regular', marginLeft: 12 },

  scrollContent: { paddingHorizontal: 20, paddingBottom: 150 },
  
  listContainer: { marginTop: 10 },
  docCardWrapper: { marginBottom: 16 },
  docCard: { flexDirection: 'row', alignItems: 'center', padding: 20, borderRadius: 24, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)', overflow: 'hidden', backgroundColor: 'rgba(30, 40, 30, 0.4)' },
  docCategory: { color: '#00FF99', fontSize: 11, fontFamily: 'Outfit_700Bold', letterSpacing: 1, marginBottom: 6 },
  docTitle: { color: '#FFF', fontSize: 18, fontFamily: 'Outfit_700Bold' },
  
  articleView: { marginTop: 10, borderRadius: 32, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0, 255, 153, 0.3)' },
  articleBlur: { padding: 30, minHeight: 400, backgroundColor: 'rgba(0, 20, 10, 0.6)' },
  closeBtn: { alignSelf: 'flex-end', width: 40, height: 40, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.1)', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  articleCategory: { color: '#00FF99', fontSize: 12, fontFamily: 'Outfit_700Bold', letterSpacing: 2, marginBottom: 10 },
  articleTitle: { color: '#FFF', fontSize: 28, fontFamily: 'Outfit_900Black', lineHeight: 36 },
  articleDivider: { height: 1, backgroundColor: 'rgba(0, 255, 153, 0.3)', marginVertical: 24 },
  articleBody: { color: '#DDD', fontSize: 16, fontFamily: 'Outfit_400Regular', lineHeight: 28 }
});
