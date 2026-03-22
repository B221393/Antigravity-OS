import React, { useState, useEffect } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView, Platform
} from 'react-native';
import { 
  BrainCircuit, Gamepad2, GraduationCap, FileText, 
  MessageSquare, Camera, Shield, Mic, Calendar, 
  Zap, Map, Settings 
} from 'lucide-react-native';

import AiMemoScreen from './src/screens/AiMemoScreen';
import EducationScreen from './src/screens/EducationScreen';
import VectorBrainScreen from './src/screens/VectorBrainScreen';
import CyberGameScreen from './src/screens/CyberGameScreen';
import DailyDiaryScreen from './src/screens/DailyDiaryScreen';
import NovelStudioScreen from './src/screens/NovelStudioScreen';

import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, withSequence, withSpring } from 'react-native-reanimated';
import { useFonts, Outfit_700Bold, Outfit_900Black, Outfit_400Regular } from '@expo-google-fonts/outfit';

const { width, height } = Dimensions.get('window');

const SLOTS = [
  { id: '01', name: 'VECTOR BRAIN', icon: BrainCircuit, color: '#00F0FF', available: true },
  { id: '02', name: 'CYBER GAME', icon: Gamepad2, color: '#FF003C', available: true },
  { id: '03', name: 'TUTOR AI', icon: GraduationCap, color: '#00FF99', available: true },
  { id: '04', name: 'AI MEMO', icon: FileText, color: '#B026FF', available: true },
  { id: '05', name: 'LOCAL LLM', icon: MessageSquare, color: '#FCEE09', available: false },
  { id: '06', name: 'VISION', icon: Camera, color: '#00FF66', available: false },
  { id: '07', name: 'SECURITY', icon: Shield, color: '#FF3366', available: false },
  { id: '08', name: 'SOUND', icon: Mic, color: '#00D4FF', available: false },
  { id: '09', name: 'DAILY LOG', icon: Calendar, color: '#FF5C93', available: true },
  { id: '10', name: 'NOVEL STUDIO', icon: Zap, color: '#FFAE00', available: true },
  { id: '11', name: 'G-MAPS', icon: Map, color: '#00F5D4', available: false },
  { id: '12', name: 'CONFIG', icon: Settings, color: '#666666', available: false },
];

const SlotCard = ({ slot, index, onPress }: { slot: any; index: number; onPress: () => void }) => {
  const Icon = slot.icon;
  
  // 押した時の「ぷにっ」としたバウンスアニメーション
  const scale = useSharedValue(1);
  const handlePressIn = () => { scale.value = withSpring(0.9, { damping: 10, stiffness: 300 }); };
  const handlePressOut = () => { scale.value = withSpring(1, { damping: 12, stiffness: 200 }); };

  // アイコンが常にフワフワ浮遊するアニメーション
  const floatY = useSharedValue(0);
  useEffect(() => {
    if (slot.available) {
      floatY.value = withRepeat(withTiming(-5, { duration: 1500 + Math.random() * 500, easing: Easing.inOut(Easing.ease) }), -1, true);
    }
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }));
  const iconStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: floatY.value }]
  }));

  // ネオンの呼吸（明滅）アニメーション
  const glowOpacity = useSharedValue(0.4);
  useEffect(() => {
    if (slot.available) {
      glowOpacity.value = withRepeat(withTiming(0.8, { duration: 2000 + index * 200, easing: Easing.inOut(Easing.ease) }), -1, true);
    }
  }, []);
  const glowStyle = useAnimatedStyle(() => ({ opacity: glowOpacity.value }));

  return (
    <Animated.View entering={FadeInDown.delay(200 + index * 100).springify().damping(12)} style={[{ width: width > 600 ? 180 : width * 0.42, aspectRatio: 1, margin: 8 }]}>
      <TouchableOpacity 
        activeOpacity={1}
        onPressIn={slot.available ? handlePressIn : undefined}
        onPressOut={slot.available ? handlePressOut : undefined}
        onPress={slot.available ? onPress : undefined}
        disabled={!slot.available}
        style={{ flex: 1, opacity: slot.available ? 1 : 0.5 }}
      >
        <Animated.View style={[styles.glassCard, slot.available && { borderColor: `${slot.color}55` }, animatedStyle]}>
          
          <BlurView intensity={80} tint="dark" style={StyleSheet.absoluteFillObject} />

          {/* 呼吸するネオンシャドウ */}
          {slot.available && (
            <Animated.View style={[styles.neonGlow, { shadowColor: slot.color, backgroundColor: `${slot.color}11` }, glowStyle]} />
          )}

          {/* フワフワ動くアイコン */}
          <Animated.View style={iconStyle}>
            <LinearGradient 
              colors={slot.available ? [`${slot.color}44`, `${slot.color}00`] : ['#222222', '#0A0A0A']} 
              style={styles.iconCircle}
            >
              <Icon color={slot.available ? slot.color : '#444'} size={28} strokeWidth={1.5} />
            </LinearGradient>
          </Animated.View>

          <View style={styles.cardTextContainer}>
            <Text style={[styles.slotId, slot.available && { color: slot.color }]}>{slot.id}</Text>
            <Text style={[styles.slotName, !slot.available && { color: '#666' }]}>{slot.name}</Text>
          </View>

          {!slot.available && (
            <View style={styles.lockedOverlay}>
              <Text style={styles.lockedText}>LOCKED</Text>
            </View>
          )}
        </Animated.View>
      </TouchableOpacity>
    </Animated.View>
  );
};

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'memo' | 'tutor' | 'vector' | 'game' | 'diary' | 'novel'>('home');

  // カスタムフォント（Google Fonts）の読み込み
  const [fontsLoaded] = useFonts({
    Outfit_400Regular,
    Outfit_700Bold,
    Outfit_900Black,
  });

  // 背景の光るオーブアニメーション
  const orb1X = useSharedValue(0);
  const orb1Y = useSharedValue(0);
  const orb2X = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(150, { duration: 15000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-150, { duration: 12000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb2X.value = withRepeat(withTiming(-200, { duration: 18000, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const orb1Style = useAnimatedStyle(() => ({
    transform: [{ translateX: orb1X.value }, { translateY: orb1Y.value }]
  }));
  const orb2Style = useAnimatedStyle(() => ({
    transform: [{ translateX: orb2X.value }]
  }));

  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: '#050511' }} />;

  // ─── 画面遷移 ───
  if (currentScreen === 'memo') return (
    <View style={{ flex: 1 }}>
      <TouchableOpacity style={styles.floatingBackButton} onPress={() => setCurrentScreen('home')} activeOpacity={0.8}>
        <Text style={styles.floatingBackText}>← 戻る / Back</Text>
      </TouchableOpacity>
      <AiMemoScreen />
    </View>
  );
  if (currentScreen === 'tutor') return <EducationScreen onBack={() => setCurrentScreen('home')} />;
  if (currentScreen === 'vector') return <VectorBrainScreen onBack={() => setCurrentScreen('home')} />;
  if (currentScreen === 'game') return <CyberGameScreen onBack={() => setCurrentScreen('home')} />;
  if (currentScreen === 'diary') return <DailyDiaryScreen onBack={() => setCurrentScreen('home')} />;
  if (currentScreen === 'novel') return <NovelStudioScreen onBack={() => setCurrentScreen('home')} />;

  // ─── Home Screen (Glassmorphism & Neon Design & Physics Animations) ───
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#050511" />
      
      {/* 🔮 背景の美しいアニメーション付きの光るオーブ（ブラーエフェクト用） */}
      <Animated.View style={[styles.glowOrb, styles.orb1, orb1Style]} />
      <Animated.View style={[styles.glowOrb, styles.orb2, orb2Style]} />

      <ScrollView contentContainerStyle={{ paddingBottom: 100 }} showsVerticalScrollIndicator={false}>
        
        {/* ─── Header ─── */}
        <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.header}>
          <Text style={styles.title}>VECTIS</Text>
          <Text style={styles.subtitle}>// ADVANCED THINKING OS //</Text>
          
          <BlurView intensity={Platform.OS === 'ios' ? 40 : 100} tint="dark" style={styles.statusBadgeWrapper}>
            <View style={styles.statusBadge}>
              <View style={styles.pulseDot} />
              <Text style={styles.badgeText}>MCP SERVER: SECURE CONNECTION</Text>
            </View>
          </BlurView>
        </Animated.View>

        {/* ─── Grid (12 Slots Animated) ─── */}
        <View style={styles.grid}>
          {SLOTS.map((slot, index) => (
            <SlotCard 
              key={slot.id} 
              slot={slot} 
              index={index} 
              onPress={() => {
                if (slot.id === '04') setCurrentScreen('memo');
                if (slot.id === '03') setCurrentScreen('tutor');
                if (slot.id === '01') setCurrentScreen('vector');
                if (slot.id === '02') setCurrentScreen('game');
                if (slot.id === '09') setCurrentScreen('diary');
                if (slot.id === '10') setCurrentScreen('novel');
              }}
            />
          ))}
        </View>

      </ScrollView>

      {/* 画面下部のオシャレグラデーション */}
      <LinearGradient colors={['transparent', '#050511']} style={styles.bottomFade} pointerEvents="none" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#050511' }, // 極めて深いミッドナイトブルー/ブラック

  // Background Animations
  glowOrb: { position: 'absolute', width: 300, height: 300, borderRadius: 150, opacity: 0.4 },
  orb1: { top: -50, right: -50, backgroundColor: '#B026FF', filter: 'blur(80px)' as any }, // Web CSS blur
  orb2: { bottom: 100, left: -50, backgroundColor: '#00F0FF', filter: 'blur(100px)' as any },

  // Header Typography 
  header: { alignItems: 'center', marginTop: 60, marginBottom: 40, zIndex: 10 },
  title: { fontFamily: 'Outfit_900Black', color: '#FFF', fontSize: 64, letterSpacing: 8, lineHeight: 70, textShadowColor: 'rgba(255,255,255,0.3)', textShadowOffset: { width: 0, height: 4 }, textShadowRadius: 10 },
  subtitle: { fontFamily: 'Outfit_700Bold', color: '#00F0FF', fontSize: 12, letterSpacing: 6, marginBottom: 24, textShadowColor: 'rgba(0, 240, 255, 0.4)', textShadowRadius: 8 },
  
  statusBadgeWrapper: { borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  statusBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 8, backgroundColor: 'rgba(0,0,0,0.3)' },
  pulseDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#00FF66', marginRight: 8, shadowColor: '#00FF66', shadowOffset: { width: 0, height: 0 }, shadowOpacity: 1, shadowRadius: 6 },
  badgeText: { fontFamily: 'Outfit_400Regular', color: '#CCC', fontSize: 10, letterSpacing: 2 },
  
  // Custom 12-Slot CSS Grid (Glassmorphism)
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', zIndex: 10, paddingHorizontal: 10 },
  slotWrapper: { width: width > 600 ? 180 : width * 0.42, aspectRatio: 1, margin: 8 },
  slotDisabled: { opacity: 0.5 },
  
  glassCard: {
    flex: 1, borderRadius: 24, overflow: 'hidden', alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)', backgroundColor: 'rgba(15, 15, 30, 0.4)',
    paddingTop: 16
  },
  neonGlow: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 24,
    shadowOffset: { width: 0, height: 10 }, shadowOpacity: 0.6, shadowRadius: 20, zIndex: -1
  },
  
  iconCircle: { width: 56, height: 56, borderRadius: 28, justifyContent: 'center', alignItems: 'center', marginBottom: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  
  cardTextContainer: { alignItems: 'center' },
  slotId: { fontFamily: 'Outfit_900Black', color: '#555', fontSize: 13, letterSpacing: 2, marginBottom: 2 },
  slotName: { fontFamily: 'Outfit_700Bold', color: '#FFF', fontSize: 12, letterSpacing: 1, textAlign: 'center' },
  
  lockedOverlay: { position: 'absolute', bottom: 12, width: '100%', alignItems: 'center', paddingVertical: 4, backgroundColor: 'rgba(255,0,0,0.1)' },
  lockedText: { fontFamily: 'Outfit_700Bold', color: '#FF3366', fontSize: 9, letterSpacing: 2 },

  bottomFade: { position: 'absolute', bottom: 0, width: '100%', height: 100, zIndex: 5 },

  floatingBackButton: {
    position: 'absolute', top: Platform.OS === 'web' ? 20 : 50, left: 20, zIndex: 100, 
    backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 16, paddingVertical: 10,
    borderRadius: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)'
  },
  floatingBackText: { fontFamily: 'Outfit_700Bold', color: '#FFF', fontSize: 12, letterSpacing: 1 }
});
