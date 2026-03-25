import React, { useState, useEffect } from 'react';
import {
  StyleSheet, Text, View, ScrollView, 
  TouchableOpacity, Dimensions, Platform, TextInput, FlatList
} from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Search, Filter, Rocket, Database, ChevronRight, X, Plus } from 'lucide-react-native';
import Animated, { FadeInDown, FadeInUp } from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

interface Idea {
  id: string;
  category: string;
  title: string;
  remodeling_insight: string;
}

export default function IdeaBankScreen() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [isAdding, setIsAdding] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newInsight, setNewInsight] = useState('');

  useEffect(() => {
    const mockIdeas: Idea[] = Array.from({ length: 200 }).map((_, i) => ({
      id: (i + 1).toString(),
      category: ['Cognition', 'Time', 'Identity', 'Environment', 'Society', 'Knowledge'][i % 6],
      title: i === 0 ? "記憶の外部化: インフラとしての記録" : `Remodeling Idea #${i + 1}`,
      remodeling_insight: i === 0 ? "AIに記憶を任せることで、人間のリソースは『覚える』から『問う』にシフトする" : 'AIによる環境適応プロセスの最適化と、人間の認知限界の突破。'
    }));
    setIdeas(mockIdeas);
  }, []);

  const handleAddIdea = () => {
    if (!newTitle.trim()) return;
    const newEntry: Idea = {
      id: (ideas.length + 1).toString(),
      category: 'NEW',
      title: newTitle,
      remodeling_insight: newInsight
    };
    setIdeas([newEntry, ...ideas]);
    setNewTitle('');
    setNewInsight('');
    setIsAdding(false);
  };

  const filteredIdeas = ideas.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         item.remodeling_insight.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || item.category.toUpperCase() === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['ALL', 'COGNITION', 'TIME', 'IDENTITY', 'ENVIRONMENT', 'SOCIETY', 'KNOWLEDGE', 'NEW'];

  const renderItem = ({ item, index }: { item: Idea, index: number }) => (
    <Animated.View entering={FadeInDown.delay(index % 10 * 50).springify()}>
      <BlurView intensity={20} tint="light" style={styles.card}>
        <View style={styles.cardHeader}>
          <View style={[styles.categoryBadge, { backgroundColor: getCategoryColor(item.category) }]}>
            <Text style={styles.categoryText}>{item.category.toUpperCase()}</Text>
          </View>
          <Text style={styles.idText}>#{item.id}</Text>
        </View>
        <Text style={styles.cardTitle}>{item.title}</Text>
        <Text style={styles.cardInsight}>{item.remodeling_insight}</Text>
        <TouchableOpacity style={styles.promoteBtn}>
          <Rocket color="#00FF99" size={14} />
          <Text style={styles.promoteText}>PROMOTE TO CHRONICLE</Text>
        </TouchableOpacity>
      </BlurView>
    </Animated.View>
  );

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#000', '#1A1A1A']} style={StyleSheet.absoluteFillObject} />
      
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Database color="#00D4FF" size={24} />
          <Text style={styles.title}>IDEA BANK</Text>
        </View>
        <Text style={styles.subtitle}>// TOTAL ASSETS: {ideas.length}</Text>
      </View>

      <View style={styles.searchContainer}>
        <BlurView intensity={40} tint="dark" style={styles.searchBlur}>
          <Search color="#666" size={18} />
          <TextInput
            style={styles.input}
            placeholder="Search ideas..."
            placeholderTextColor="#666"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </BlurView>
      </View>

      <View style={{ maxHeight: 50 }}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.categoryContent}>
          {categories.map((cat) => (
            <TouchableOpacity 
              key={cat} 
              onPress={() => setSelectedCategory(cat)}
              style={[styles.categoryTab, selectedCategory === cat && styles.selectedTab]}
            >
              <Text style={[styles.tabText, selectedCategory === cat && styles.selectedTabText]}>{cat}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      <FlatList
        data={filteredIdeas}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />

      <TouchableOpacity style={styles.fab} onPress={() => setIsAdding(true)}>
        <LinearGradient colors={['#00D4FF', '#A020F0']} style={styles.fabGradient}>
          <Plus color="#FFF" size={24} />
        </LinearGradient>
      </TouchableOpacity>

      {isAdding && (
        <Animated.View entering={FadeInUp} style={styles.modalOverlay}>
          <BlurView intensity={100} tint="dark" style={styles.modalContent}>
            <Text style={styles.modalTitle}>NEW INTEL</Text>
            <TextInput 
              style={styles.modalInput} 
              placeholder="Title..." 
              placeholderTextColor="#666"
              value={newTitle}
              onChangeText={setNewTitle}
            />
            <TextInput 
              style={[styles.modalInput, { height: 100 }]} 
              placeholder="Remodeling Insight..." 
              placeholderTextColor="#666"
              multiline
              value={newInsight}
              onChangeText={setNewInsight}
            />
            <View style={styles.modalButtons}>
              <TouchableOpacity onPress={() => setIsAdding(false)} style={styles.cancelBtn}>
                <Text style={styles.cancelText}>CANCEL</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={handleAddIdea} style={styles.addBtn}>
                <Text style={styles.addText}>SAVE</Text>
              </TouchableOpacity>
            </View>
          </BlurView>
        </Animated.View>
      )}
    </View>
  );
}

const getCategoryColor = (cat: string) => {
  switch (cat) {
    case 'Cognition': return '#00F0FF';
    case 'Time': return '#FF9E00';
    case 'Identity': return '#B026FF';
    case 'Environment': return '#FF0055';
    case 'Society': return '#00FF99';
    case 'Knowledge': return '#00D4FF';
    case 'NEW': return '#FFF';
    default: return '#666';
  }
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  header: { paddingHorizontal: 24, paddingTop: 80, marginBottom: 20 },
  titleRow: { flexDirection: 'row', alignItems: 'center' },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 2, marginLeft: 12 },
  subtitle: { color: '#666', fontSize: 10, letterSpacing: 4, marginTop: 8 },

  searchContainer: { paddingHorizontal: 20, marginBottom: 16 },
  searchBlur: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12, borderRadius: 24, backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  input: { flex: 1, color: '#FFF', marginLeft: 10, fontSize: 14 },

  categoryContent: { paddingHorizontal: 20, paddingBottom: 10 },
  categoryTab: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, marginRight: 8, backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'transparent' },
  selectedTab: { backgroundColor: 'rgba(0, 212, 255, 0.1)', borderColor: 'rgba(0, 212, 255, 0.3)' },
  tabText: { color: '#666', fontSize: 10, fontWeight: '900' },
  selectedTabText: { color: '#00D4FF' },

  listContent: { paddingHorizontal: 20, paddingBottom: 120 },
  card: { padding: 18, borderRadius: 24, marginBottom: 16, backgroundColor: 'rgba(10, 10, 15, 0.5)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)', overflow: 'hidden' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  categoryBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  categoryText: { color: '#000', fontSize: 9, fontWeight: '900' },
  idText: { color: '#444', fontSize: 10, fontWeight: 'bold' },
  cardTitle: { color: '#FFF', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  cardInsight: { color: '#888', fontSize: 13, lineHeight: 18, marginBottom: 16 },
  promoteBtn: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', paddingVertical: 6, paddingHorizontal: 10, borderRadius: 12, backgroundColor: 'rgba(0, 255, 153, 0.1)' },
  promoteText: { color: '#00FF99', fontSize: 9, fontWeight: '900', marginLeft: 8, letterSpacing: 1 },

  fab: { position: 'absolute', bottom: 30, right: 20, width: 56, height: 56, borderRadius: 28, overflow: 'hidden', elevation: 5 },
  fabGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  modalOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
  modalContent: { width: width * 0.85, padding: 24, borderRadius: 32, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)', overflow: 'hidden' },
  modalTitle: { color: '#FFF', fontSize: 18, fontWeight: '900', marginBottom: 20, letterSpacing: 2 },
  modalInput: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 16, color: '#FFF', marginBottom: 16, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  modalButtons: { flexDirection: 'row', justifyContent: 'flex-end' },
  cancelBtn: { padding: 12, marginRight: 8 },
  cancelText: { color: '#666', fontSize: 12, fontWeight: '900' },
  addBtn: { backgroundColor: 'rgba(0, 212, 255, 0.2)', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 12 },
  addText: { color: '#00D4FF', fontSize: 12, fontWeight: '900' }
});
