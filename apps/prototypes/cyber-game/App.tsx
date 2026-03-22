import React, { useState } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView
} from 'react-native';
import { 
  BrainCircuit, Gamepad2, GraduationCap, FileText, 
  MessageSquare, Camera, Shield, Mic, Calendar, 
  Zap, Map, Settings 
} from 'lucide-react-native';

import AiMemoScreen from './src/screens/AiMemoScreen';
import EducationScreen from './src/screens/EducationScreen';
import { LinearGradient } from 'expo-linear-gradient';

import VectorBrainScreen from './src/screens/VectorBrainScreen';
import CyberGameScreen from './src/screens/CyberGameScreen';
import DailyDiaryScreen from './src/screens/DailyDiaryScreen';
import NovelStudioScreen from './src/screens/NovelStudioScreen';

const { width } = Dimensions.get('window');

const SLOTS = [
  { id: '01', name: 'VECTOR BRAIN', icon: BrainCircuit, color: '#3b82f6', available: true },
  { id: '02', name: 'CYBER GAME', icon: Gamepad2, color: '#ec4899', available: true },
  { id: '03', name: 'TUTOR AI', icon: GraduationCap, color: '#00FF99', available: true },
  { id: '04', name: 'AI MEMO', icon: FileText, color: '#8b5cf6', available: true },
  { id: '05', name: 'LOCAL LLM', icon: MessageSquare, color: '#f59e0b', available: false },
  { id: '06', name: 'VISION', icon: Camera, color: '#10b981', available: false },
  { id: '07', name: 'SECURITY', icon: Shield, color: '#ef4444', available: false },
  { id: '08', name: 'SOUND', icon: Mic, color: '#06b6d4', available: false },
  { id: '09', name: 'DAILY LOG', icon: Calendar, color: '#f43f5e', available: true },
  { id: '10', name: 'NOVEL STUDIO', icon: Zap, color: '#eab308', available: true },
  { id: '11', name: 'G-MAPS', icon: Map, color: '#14b8a6', available: false },
  { id: '12', name: 'CONFIG', icon: Settings, color: '#64748b', available: false },
];

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'memo' | 'tutor' | 'vector' | 'game' | 'diary' | 'novel'>('home');

  if (currentScreen === 'memo') {
    return (
      <View style={{ flex: 1 }}>
        <TouchableOpacity 
          style={styles.floatingBackButton} 
          onPress={() => setCurrentScreen('home')}
          activeOpacity={0.8}
        >
          <Text style={{color: '#FFF', fontWeight: 'bold'}}>← 戻る</Text>
        </TouchableOpacity>
        <AiMemoScreen />
      </View>
    );
  }

  if (currentScreen === 'tutor') {
    return <EducationScreen onBack={() => setCurrentScreen('home')} />;
  }

  if (currentScreen === 'vector') {
    return <VectorBrainScreen onBack={() => setCurrentScreen('home')} />;
  }

  if (currentScreen === 'game') {
    return <CyberGameScreen onBack={() => setCurrentScreen('home')} />;
  }

  if (currentScreen === 'diary') {
    return <DailyDiaryScreen onBack={() => setCurrentScreen('home')} />;
  }

  if (currentScreen === 'novel') {
    return <NovelStudioScreen onBack={() => setCurrentScreen('home')} />;
  }

  // ─── Home Screen (12 Slots) ───
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <View style={styles.header}>
        <Text style={styles.title}>VECTIS CONTROLLER</Text>
        <View style={styles.badge}>
          <View style={styles.pulseDot} />
          <Text style={styles.badgeText}>LOCAL SERVER: OFFLINE</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.grid}>
        {SLOTS.map((slot) => {
          const Icon = slot.icon;
          return (
            <TouchableOpacity 
              key={slot.id} 
              style={[styles.slotCard, !slot.available && styles.slotDisabled]}
              activeOpacity={0.7}
              onPress={() => {
                if (slot.id === '04') setCurrentScreen('memo');
                if (slot.id === '03') setCurrentScreen('tutor');
                if (slot.id === '01') setCurrentScreen('vector');
                if (slot.id === '02') setCurrentScreen('game');
                if (slot.id === '09') setCurrentScreen('diary');
                if (slot.id === '10') setCurrentScreen('novel');
              }}
              disabled={!slot.available}
            >
              <LinearGradient 
                colors={[`${slot.color}33`, `${slot.color}05`]} 
                style={styles.iconBox}
              >
                <Icon color={slot.available ? slot.color : '#444'} size={32} />
              </LinearGradient>
              <Text style={styles.slotId}>{slot.id}</Text>
              <Text style={[styles.slotName, !slot.available && { color: '#666' }]}>
                {slot.name}
              </Text>
              {!slot.available && <Text style={styles.devText}>- IN DEV -</Text>}
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050505' },
  header: { alignItems: 'center', marginVertical: 32 },
  title: { color: '#FFF', fontSize: 24, fontWeight: '900', letterSpacing: 4, marginBottom: 12 },
  badge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1A1A1A', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16 },
  pulseDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#FF3B30', marginRight: 8 },
  badgeText: { color: '#888', fontSize: 10, fontWeight: 'bold', letterSpacing: 1 },
  
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', paddingBottom: 60 },
  slotCard: { 
    width: width * 0.28, 
    margin: 8, 
    alignItems: 'center', 
    backgroundColor: '#0A0A0A', 
    paddingVertical: 20,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#111'
  },
  slotDisabled: { opacity: 0.6 },
  iconBox: { width: 64, height: 64, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  slotId: { color: '#444', fontSize: 10, fontWeight: '900', letterSpacing: 1, marginBottom: 4 },
  slotName: { color: '#FFF', fontSize: 11, fontWeight: 'bold', letterSpacing: 0.5, textAlign: 'center' },
  devText: { color: '#FF3B30', fontSize: 8, marginTop: 6, fontWeight: 'bold' },

  floatingBackButton: {
    position: 'absolute', top: 50, left: 20, zIndex: 100, 
    backgroundColor: '#000', paddingHorizontal: 16, paddingVertical: 8,
    borderRadius: 20, borderWidth: 1, borderColor: '#333'
  }
});
