import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, TextInput, StatusBar, Animated } from 'react-native';
import { List, PenSquare, Robot, Info, Plus, RotateCw, Wand2 } from 'lucide-react-native';

const MemoCard = ({ memo }: any) => {
  const isAI = memo.content.includes('[AIエージェント');
  return (
    <View style={[styles.card, isAI && styles.aiCard]}>
      <View style={styles.cardHeader}>
        <View style={styles.titleContainer}>
          <Text style={styles.cardTitle}>{memo.title}</Text>
          {isAI && (
            <View style={styles.aiBadge}>
              <Wand2 size={10} color="#7E22CE" />
              <Text style={styles.aiBadgeText}>AI</Text>
            </View>
          )}
        </View>
        <Text style={styles.cardDate}>{memo.date}</Text>
      </View>
      <Text style={styles.cardContent}>{memo.content}</Text>
    </View>
  );
};

export default function App() {
  const [activeTab, setActiveTab] = useState('list');
  const [memos, setMemos] = useState([
    { id: 1, title: "プロジェクトのアイデア", content: "MCPを使った自動化ツールの構成案を作成する。", date: "2026-03-21 10:00" },
    { id: 2, title: "AIからの報告", content: "[AIエージェントによる自動追記] 競合アプリの調査を完了しました。", date: "2026-03-21 14:30" }
  ]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const handleAddMemo = () => {
    if (!title || !content) return;
    const now = new Date();
    const dateStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    const newMemo = { id: Date.now(), title, content, date: dateStr };
    setMemos([newMemo, ...memos]);
    setTitle('');
    setContent('');
    setActiveTab('list');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Robot color="#FFF" size={24} />
          <Text style={styles.headerText}>AI Memo Agent</Text>
        </View>
        <View style={styles.statusBadge}>
          <View style={styles.statusDot} />
          <Text style={styles.statusText}>MCP Ready</Text>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'list' && styles.activeTab]} 
          onPress={() => setActiveTab('list')}
        >
          <List size={20} color={activeTab === 'list' ? '#4F46E5' : '#64748B'} />
          <Text style={[styles.tabText, activeTab === 'list' && styles.activeTabText]}>メモ一覧</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'add' && styles.activeTab]} 
          onPress={() => setActiveTab('add')}
        >
          <PenSquare size={20} color={activeTab === 'add' ? '#4F46E5' : '#64748B'} />
          <Text style={[styles.tabText, activeTab === 'add' && styles.activeTabText]}>メモ追加</Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.content}>
        {activeTab === 'list' ? (
          <View>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>保存されたメモ</Text>
              <TouchableOpacity style={styles.refreshButton}>
                <RotateCw size={14} color="#4F46E5" />
                <Text style={styles.refreshText}>更新</Text>
              </TouchableOpacity>
            </View>
            {memos.map(memo => <MemoCard key={memo.id} memo={memo} />)}
          </View>
        ) : (
          <View>
            <Text style={styles.sectionTitle}>新しいメモを作成</Text>
            <View style={styles.inputCard}>
              <Text style={styles.label}>タイトル</Text>
              <TextInput 
                style={styles.input} 
                placeholder="例: 買い物リスト" 
                value={title}
                onChangeText={setTitle}
              />
              <Text style={styles.label}>内容</Text>
              <TextInput 
                style={[styles.input, styles.textArea]} 
                placeholder="AIに指示したい内容..." 
                multiline
                numberOfLines={4}
                value={content}
                onChangeText={setContent}
              />
              <TouchableOpacity style={styles.saveButton} onPress={handleAddMemo}>
                <Plus size={20} color="#FFF" />
                <Text style={styles.saveButtonText}>メモを保存する</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.infoBox}>
              <View style={styles.infoTitleRow}>
                <Info size={16} color="#1E40AF" />
                <Text style={styles.infoTitle}>AIエージェントとの連携</Text>
              </View>
              <Text style={styles.infoText}>
                MCP経由でAIに指示すると、このアプリを操作しなくても自動的にデータが追加されます。
              </Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  header: { 
    backgroundColor: '#4F46E5', 
    padding: 16, 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center' },
  headerText: { color: '#FFF', fontSize: 18, fontWeight: 'bold', marginLeft: 8 },
  statusBadge: { backgroundColor: '#4338CA', paddingHorizontal: 10, py: 4, borderRadius: 20, flexDirection: 'row', alignItems: 'center' },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#4ADE80', marginRight: 6 },
  statusText: { color: '#FFF', fontSize: 12 },
  tabContainer: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: '#E2E8F0', backgroundColor: '#FFF' },
  tab: { flex: 1, paddingVertical: 14, flexDirection: 'row', justifyContent: 'center', alignItems: 'center', borderBottomWidth: 2, borderBottomColor: 'transparent' },
  activeTab: { borderBottomColor: '#4F46E5' },
  tabText: { marginLeft: 8, fontSize: 14, fontWeight: '500', color: '#64748B' },
  activeTabText: { color: '#4F46E5' },
  content: { padding: 16 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#334155', marginBottom: 16 },
  refreshButton: { flexDirection: 'row', alignItems: 'center' },
  refreshText: { color: '#4F46E5', fontSize: 12, marginLeft: 4 },
  card: { backgroundColor: '#FFF', padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#F1F5F9', shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 2, elevation: 1 },
  aiCard: { borderLeftWidth: 4, borderLeftColor: '#A855F7' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  titleContainer: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  cardTitle: { fontSize: 15, fontWeight: '700', color: '#1E293B' },
  aiBadge: { backgroundColor: '#F3E8FF', paddingHorizontal: 6, py: 2, borderRadius: 4, borderWidth: 1, borderColor: '#E9D5FF', marginLeft: 8, flexDirection: 'row', alignItems: 'center' },
  aiBadgeText: { color: '#7E22CE', fontSize: 10, fontWeight: 'bold', marginLeft: 2 },
  cardDate: { fontSize: 11, color: '#94A3B8' },
  cardContent: { fontSize: 14, color: '#475569', lineHeight: 20 },
  inputCard: { backgroundColor: '#FFF', padding: 20, borderRadius: 16, borderWidth: 1, borderColor: '#F1F5F9' },
  label: { fontSize: 13, fontWeight: '600', color: '#64748B', marginBottom: 6 },
  input: { borderWidth: 1, borderColor: '#CBD5E1', borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 14, color: '#1E293B' },
  textArea: { height: 100, textAlignVertical: 'top' },
  saveButton: { backgroundColor: '#4F46E5', padding: 14, borderRadius: 8, flexDirection: 'row', justifyContent: 'center', alignItems: 'center' },
  saveButtonText: { color: '#FFF', fontWeight: '700', fontSize: 15, marginLeft: 8 },
  infoBox: { marginTop: 20, backgroundColor: '#EFF6FF', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#DBEAFE' },
  infoTitleRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  infoTitle: { color: '#1E40AF', fontSize: 13, fontWeight: '700', marginLeft: 8 },
  infoText: { color: '#1E40AF', fontSize: 12, lineHeight: 18 }
});
