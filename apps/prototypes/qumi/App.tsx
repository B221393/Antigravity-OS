import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView, Platform
} from 'react-native';
import { 
  BrainCircuit, Gamepad2, GraduationCap, FileText, 
  MessageSquare, Camera, Shield, Mic, Calendar, 
  Zap, Map, Settings, Sparkles, BookOpen
} from 'lucide-react-native';

import AiMemoScreen from './src/screens/AiMemoScreen';
import EducationScreen from './src/screens/EducationScreen';
import VectorBrainScreen from './src/screens/VectorBrainScreen';
import CyberGameScreen from './src/screens/CyberGameScreen';
import DailyDiaryScreen from './src/screens/DailyDiaryScreen';
import NovelStudioScreen from './src/screens/NovelStudioScreen';
import LocalLlmScreen from './src/screens/LocalLlmScreen';
import VisionScreen from './src/screens/VisionScreen';
import SecurityScreen from './src/screens/SecurityScreen';
import SoundScreen from './src/screens/SoundScreen';
import GMapsScreen from './src/screens/GMapsScreen';
import ConfigScreen from './src/screens/ConfigScreen';

import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, withSpring } from 'react-native-reanimated';
import { useFonts, Outfit_400Regular, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';
import { Animated as RNAnimated, PanResponder } from 'react-native';

const { width, height } = Dimensions.get('window');

// 12 Core OS Slots (Layer Categorized)
const SLOTS = [
  // INTEL LAYER (知能層)
  { id: '01', name: 'VECTOR CORE',  icon: BrainCircuit,   color: '#00F0FF', layer: 'INTEL', available: true },
  { id: '05', name: 'LOCAL LLM',    icon: Zap,             color: '#FF9E00', layer: 'INTEL', available: true },
  { id: '03', name: 'TUTOR AI',     icon: GraduationCap,   color: '#00FF99', layer: 'INTEL', available: true },
  
  // THOUGHT LAYER (思考層)
  { id: '04', name: 'AI MEMO',      icon: FileText,        color: '#B026FF', layer: 'THOUGHT', available: true },
  { id: '10', name: 'NOVEL STD',    icon: MessageSquare,   color: '#FF00B3', layer: 'THOUGHT', available: true },
  { id: '09', name: 'DAILY LOG',    icon: Calendar,        color: '#FF5C93', layer: 'THOUGHT', available: true },
  
  // SENSE LAYER (知覚層)
  { id: '06', name: 'VISION',       icon: Camera,          color: '#FF0055', layer: 'SENSE', available: true },
  { id: '08', name: 'SOUND',        icon: Mic,             color: '#00D4FF', layer: 'SENSE', available: true },
  { id: '11', name: 'G-MAPS',       icon: Map,             color: '#00CC44', layer: 'SENSE', available: true },

  // SYSTEM LAYER (システム層)
  { id: '02', name: 'CYBER GAME',   icon: Gamepad2,        color: '#FF003C', layer: 'SYSTEM', available: true },
  { id: '07', name: 'SECURITY',     icon: Shield,          color: '#444444', layer: 'SYSTEM', available: true },
  { id: '12', name: 'SYS CONFIG',   icon: Settings,        color: '#666666', layer: 'SYSTEM', available: true },
];

const AppIcon = ({ slot, index, onPress }: { slot: any; index: number; onPress: () => void }) => {
  const Icon = slot.icon;
  const scale = useSharedValue(1);
  const handlePressIn = () => { scale.value = withSpring(0.82, { damping: 12, stiffness: 500 }); };
  const handlePressOut = () => { scale.value = withSpring(1, { damping: 12, stiffness: 300 }); };
  const animatedStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  return (
    <Animated.View entering={FadeInDown.delay(index * 50).springify().damping(14)} style={styles.appIconWrapper}>
      <TouchableOpacity activeOpacity={1} onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress} style={{ alignItems: 'center' }}>
        <Animated.View style={[styles.appIconBox, animatedStyle]}>
          <LinearGradient colors={[`${slot.color}DD`, `${slot.color}55`]} style={styles.appIconGradient}>
            <Icon color="#FFFFFF" size={26} strokeWidth={1.5} />
          </LinearGradient>
        </Animated.View>
        <Text style={styles.appLabel} numberOfLines={1}>{slot.name.replace('VECTOR ', 'V-').replace('STUDIO', '')}</Text>
      </TouchableOpacity>
    </Animated.View>
  );
};

// クラスター（グループ）表示用コンポーネント
const SlotCluster = ({ title, layer, onOpenApp }: { title: string, layer: string, onOpenApp: (id: string) => void }) => {
  const layerSlots = SLOTS.filter(s => s.layer === layer);
  
  return (
    <View style={styles.clusterContainer}>
      <Text style={styles.clusterTitle}>// {title}</Text>
      <BlurView intensity={20} tint="dark" style={styles.clusterBlur}>
        <View style={styles.clusterGrid}>
          {layerSlots.map((slot, index) => (
            <AppIcon key={slot.id} slot={slot} index={index} onPress={() => onOpenApp(slot.id)} />
          ))}
        </View>
      </BlurView>
    </View>
  );
};

const DraggableCore = () => {
  const pan = useRef(new RNAnimated.ValueXY({ x: 0, y: height / 2.5 })).current;
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderGrant: () => { pan.setOffset({ x: (pan.x as any)._value, y: (pan.y as any)._value }); pan.setValue({ x: 0, y: 0 }); },
      onPanResponderMove: RNAnimated.event([null, { dx: pan.x, dy: pan.y }], { useNativeDriver: false }),
      onPanResponderRelease: (_, gs) => {
        pan.flattenOffset();
        RNAnimated.spring(pan, { toValue: { x: gs.moveX > width / 2 ? width / 2 - 40 : -width / 2 + 40, y: (pan.y as any)._value + gs.vy * 50 }, friction: 6, tension: 40, useNativeDriver: false }).start();
      }
    })
  ).current;

  return (
    <RNAnimated.View {...panResponder.panHandlers} style={[pan.getLayout(), { position: 'absolute', top: '50%', left: '50%', zIndex: 999 }]}>
      <View style={{ transform: [{ translateX: -35 }, { translateY: -35 }] }}>
        <BlurView intensity={100} tint="dark" style={styles.floatingCore}>
          <LinearGradient colors={['#A020F0', '#00D4FF']} style={styles.coreGradient}>
            <Sparkles color="#FFF" size={28} />
          </LinearGradient>
        </BlurView>
        <View style={styles.coreGlow} />
      </View>
    </RNAnimated.View>
  );
};

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<string>('home');
  const [fontsLoaded] = useFonts({ Outfit_400Regular, Outfit_700Bold, Outfit_900Black });

  const orb1X = useSharedValue(0); 
  const orb1Y = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(100, { duration: 25000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-100, { duration: 22000, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const orb1Style = useAnimatedStyle(() => ({ transform: [{ translateX: orb1X.value }, { translateY: orb1Y.value }] }));

  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: '#000' }} />;

  const handleOpenApp = (id: string) => {
    if (id === '04') setCurrentScreen('memo');
    if (id === '03') setCurrentScreen('tutor');
    if (id === '01') setCurrentScreen('vector');
    if (id === '02') setCurrentScreen('game');
    if (id === '09') setCurrentScreen('diary');
    if (id === '10') setCurrentScreen('novel');
    if (id === '05') setCurrentScreen('llm');
    if (id === '06') setCurrentScreen('vision');
    if (id === '07') setCurrentScreen('security');
    if (id === '08') setCurrentScreen('sound');
    if (id === '11') setCurrentScreen('maps');
    if (id === '12') setCurrentScreen('config');
  };

  if (currentScreen !== 'home') {
    return (
      <Animated.View entering={FadeIn.duration(300)} style={{ flex: 1, backgroundColor: '#000' }}>
        <TouchableOpacity style={styles.floatingBackButton} onPress={() => setCurrentScreen('home')} activeOpacity={0.7}>
          <BlurView intensity={80} tint="dark" style={styles.backButtonBlur}>
            <Text style={styles.floatingBackText}>← System Home</Text>
          </BlurView>
        </TouchableOpacity>

        {currentScreen === 'memo' && <AiMemoScreen />}
        {currentScreen === 'tutor' && <EducationScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === 'vector' && <VectorBrainScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === 'game' && <CyberGameScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === 'diary' && <DailyDiaryScreen />}
        {currentScreen === 'novel' && <NovelStudioScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === 'llm' && <LocalLlmScreen />}
        {currentScreen === 'vision' && <VisionScreen />}
        {currentScreen === 'security' && <SecurityScreen />}
        {currentScreen === 'sound' && <SoundScreen />}
        {currentScreen === 'maps' && <GMapsScreen />}
        {currentScreen === 'config' && <ConfigScreen />}
      </Animated.View>
    );
  }

  const isPC = width > 800;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      
      <Animated.View style={[styles.glowOrb, styles.orb1, orb1Style]} />
      <View style={styles.wallpaperOverlay} />

      <View style={[styles.iosStatusBar, isPC && { paddingHorizontal: 40, paddingTop: 20 }]}>
        <Text style={styles.iosTimeText}>QUMI : INTEGRATED OS</Text>
        <View style={styles.iosStatusIcons}>
          <View style={[styles.pulseDot, { backgroundColor: '#00FF99' }]} />
          <Text style={styles.iosSignalText}>Agent Online</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={isPC ? styles.pcHomeGrid : styles.homeGrid} showsVerticalScrollIndicator={false}>
        <View style={isPC ? styles.pcClusterWrapper : {}}>
          <SlotCluster title="THOUGHT LAYER" layer="THOUGHT" onOpenApp={handleOpenApp} />
          <SlotCluster title="INTEL LAYER" layer="INTEL" onOpenApp={handleOpenApp} />
          <SlotCluster title="SENSE LAYER" layer="SENSE" onOpenApp={handleOpenApp} />
          <SlotCluster title="SYSTEM LAYER" layer="SYSTEM" onOpenApp={handleOpenApp} />
        </View>
      </ScrollView>

      <DraggableCore />

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  glowOrb: { position: 'absolute', width: 500, height: 500, borderRadius: 250, opacity: 0.4 },
  orb1: { top: -150, left: -150, backgroundColor: '#00D4FF', filter: 'blur(120px)' as any },
  wallpaperOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.6)', zIndex: 0 },
  
  iosStatusBar: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 16, zIndex: 10 },
  iosTimeText: { color: '#FFF', fontSize: 13, fontWeight: 'bold', fontFamily: 'Outfit_700Bold', letterSpacing: 2 },
  iosStatusIcons: { flexDirection: 'row', alignItems: 'center' },
  iosSignalText: { color: '#FFF', fontSize: 11, fontWeight: '600', marginLeft: 6 },
  pulseDot: { width: 6, height: 6, borderRadius: 3, shadowColor: '#00FF99', shadowOpacity: 1, shadowRadius: 5 },
  
  homeGrid: { paddingHorizontal: 20, paddingTop: 20, paddingBottom: 150, zIndex: 10 },
  pcHomeGrid: { width: '100%', alignItems: 'center', paddingTop: 40, paddingBottom: 150, zIndex: 10 },
  pcClusterWrapper: { width: 800, flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },

  clusterContainer: { marginBottom: 28, width: width > 800 ? '48%' : '100%' },
  clusterTitle: { color: '#00D4FF', fontSize: 11, fontFamily: 'Outfit_900Black', letterSpacing: 3, marginBottom: 8, opacity: 0.8 },
  clusterBlur: { borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  clusterGrid: { flexDirection: 'row', justifyContent: 'space-around', paddingVertical: 20, paddingHorizontal: 10, backgroundColor: 'rgba(15, 23, 42, 0.4)' },

  appIconWrapper: { alignItems: 'center', width: '30%' }, 
  appIconBox: { width: width > 600 ? 76 : 64, height: width > 600 ? 76 : 64, borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  appIconGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  appLabel: { color: '#FFF', fontSize: 10, fontFamily: 'Outfit_700Bold', marginTop: 10, textAlign: 'center', opacity: 0.8, letterSpacing: 1 },
  
  floatingBackButton: { position: 'absolute', top: Platform.OS === 'web' ? 20 : 50, left: 20, zIndex: 100, borderRadius: 20, overflow: 'hidden' },
  backButtonBlur: { paddingHorizontal: 16, paddingVertical: 10, backgroundColor: 'rgba(0,0,0,0.6)', borderRadius: 20, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  floatingBackText: { color: '#FFF', fontSize: 13, fontWeight: 'bold' },
  
  floatingCore: { width: 70, height: 70, borderRadius: 35, overflow: 'hidden', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: 'rgba(0, 212, 255, 0.4)' },
  coreGradient: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center', opacity: 0.9 },
  coreGlow: { position: 'absolute', top: -15, left: -15, right: -15, bottom: -15, borderRadius: 50, backgroundColor: '#A020F0', opacity: 0.4, filter: 'blur(15px)' as any, zIndex: -1 }
});

