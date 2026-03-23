import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView, Platform
} from 'react-native';
import { 
  BrainCircuit, Gamepad2, GraduationCap, FileText, 
  MessageSquare, Camera, Shield, Mic, Calendar, 
  Zap, Map, Settings, Sparkles
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

const { width, height } = Dimensions.get('window');

const SLOTS = [
  { id: '01', name: 'VECTOR BRAIN', icon: BrainCircuit, color: '#00F0FF', available: true },
  { id: '02', name: 'CYBER GAME', icon: Gamepad2, color: '#FF003C', available: true },
  { id: '03', name: 'TUTOR AI', icon: GraduationCap, color: '#00FF99', available: true },
  { id: '04', name: 'AI MEMO', icon: FileText, color: '#B026FF', available: true },
  { id: '05', name: 'LOCAL LLM', icon: MessageSquare, color: '#FCEE09', available: true },
  { id: '06', name: 'VISION', icon: Camera, color: '#00FF66', available: true },
  { id: '07', name: 'SECURITY', icon: Shield, color: '#FF3366', available: true },
  { id: '08', name: 'SOUND', icon: Mic, color: '#00D4FF', available: true },
  { id: '09', name: 'DAILY LOG', icon: Calendar, color: '#FF5C93', available: true },
  { id: '10', name: 'NOVEL STUDIO', icon: Zap, color: '#FFAE00', available: true },
  { id: '11', name: 'G-MAPS', icon: Map, color: '#00F5D4', available: true },
  { id: '12', name: 'CONFIG', icon: Settings, color: '#666666', available: true },
];

const AppIcon = ({ slot, index, isDock = false, onPress }: { slot: any; index: number; isDock?: boolean; onPress: () => void }) => {
  const Icon = slot.icon;
  const scale = useSharedValue(1);

  const handlePressIn = () => { scale.value = withSpring(0.85, { damping: 15, stiffness: 400 }); };
  const handlePressOut = () => { scale.value = withSpring(1, { damping: 15, stiffness: 300 }); };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }]
  }));

  const iconBg = slot.available ? [`${slot.color}DD`, `${slot.color}88`] : ['#222', '#111'];

  return (
    <Animated.View entering={FadeInDown.delay(index * 40).springify().damping(15)} style={styles.appIconWrapper}>
      <TouchableOpacity 
        activeOpacity={1}
        onPressIn={slot.available ? handlePressIn : undefined}
        onPressOut={slot.available ? handlePressOut : undefined}
        onPress={slot.available ? onPress : undefined}
        disabled={!slot.available}
        style={{ alignItems: 'center' }}
      >
        <Animated.View style={[styles.appIconBox, animatedStyle]}>
          <LinearGradient colors={iconBg} style={styles.appIconGradient}>
            <Icon color={slot.available ? '#FFFFFF' : '#555'} size={isDock ? 30 : 28} strokeWidth={1.5} />
          </LinearGradient>
          {!slot.available && <View style={styles.lockedIconOverlay} />}
        </Animated.View>
        {!isDock && (
          <Text style={[styles.appLabel, !slot.available && { color: '#666' }]} numberOfLines={1}>
            {slot.name.replace('VECTOR ', 'V-').replace('STUDIO', '')}
          </Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

// ─── 新規実装：画面をコロコロ転がる・ドラッグできる「統合思考コア」の物理演算UI ───
import { Animated as RNAnimated, PanResponder } from 'react-native';

const DraggableCore = () => {
  const pan = useRef(new RNAnimated.ValueXY({ x: 0, y: height / 3 })).current;
  
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        pan.setOffset({ x: (pan.x as any)._value, y: (pan.y as any)._value });
        pan.setValue({ x: 0, y: 0 });
      },
      onPanResponderMove: RNAnimated.event([null, { dx: pan.x, dy: pan.y }], { useNativeDriver: false }),
      onPanResponderRelease: (e, gestureState) => {
        pan.flattenOffset();
        const endX = gestureState.moveX > width / 2 ? width / 2 - 40 : -width / 2 + 40;
        RNAnimated.spring(pan, {
          toValue: { x: endX, y: (pan.y as any)._value + gestureState.vy * 50 },
          friction: 6,
          tension: 40,
          useNativeDriver: false
        }).start();
      }
    })
  ).current;

  return (
    <RNAnimated.View
      {...panResponder.panHandlers}
      style={[
        pan.getLayout(),
        { position: 'absolute', top: '50%', left: '50%', zIndex: 999, elevation: 999 }
      ]}
    >
      <View style={{ transform: [{ translateX: -30 }, { translateY: -30 }] }}>
        <BlurView intensity={100} tint="dark" style={styles.floatingCore}>
          <LinearGradient colors={['#A020F0', '#00D4FF']} style={styles.coreGradient}>
            <Sparkles color="#FFF" size={24} />
          </LinearGradient>
        </BlurView>
        <View style={styles.coreGlow} />
      </View>
    </RNAnimated.View>
  );
};

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'memo' | 'tutor' | 'vector' | 'game' | 'diary' | 'novel' | 'llm' | 'vision' | 'security' | 'sound' | 'maps' | 'config'>('home');

  const [fontsLoaded] = useFonts({ Outfit_400Regular, Outfit_700Bold, Outfit_900Black });

  const orb1X = useSharedValue(0); 
  const orb1Y = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(150, { duration: 20000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-150, { duration: 18000, easing: Easing.inOut(Easing.ease) }), -1, true);
  }, []);

  const orb1Style = useAnimatedStyle(() => ({ transform: [{ translateX: orb1X.value }, { translateY: orb1Y.value }] }));

  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: '#000' }} />;

  const DOCK_APPS = SLOTS.filter(s => ['04', '03', '01', '02'].includes(s.id));
  const HOME_APPS = SLOTS.filter(s => !['04', '03', '01', '02'].includes(s.id));

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
            <Text style={styles.floatingBackText}>← Home</Text>
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

  // Web・PCブラウザ用の横幅最適化フラグ
  const isPC = width > 800;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      
      <Animated.View style={[styles.glowOrb, styles.orb1, orb1Style]} />
      <View style={styles.wallpaperOverlay} />

      {/* PC版ではステータスバーをMac風に少し控えめに */}
      <View style={[styles.iosStatusBar, isPC && { paddingHorizontal: 40, paddingTop: 20 }]}>
        <Text style={styles.iosTimeText}>QUMI : INTEGRATED OS</Text>
        <View style={styles.iosStatusIcons}>
          <View style={[styles.pulseDot, { backgroundColor: '#00FF99' }]} />
          <Text style={styles.iosSignalText}>Agent Online</Text>
        </View>
      </View>

      {/* ブラウザ版は中央にUIを寄せて超絶高級感を出す */}
      <ScrollView contentContainerStyle={isPC ? styles.pcHomeGrid : styles.homeGrid} showsVerticalScrollIndicator={false}>
        {HOME_APPS.map((slot, index) => (
          <AppIcon key={slot.id} slot={slot} index={index} onPress={() => handleOpenApp(slot.id)} />
        ))}
      </ScrollView>

      {/* PC版ではDockをMac風に中央固定、スマホは全幅 */}
      <View style={[styles.dockContainer, isPC && styles.pcDockContainer]}>
        <BlurView intensity={80} tint="dark" style={styles.dockBlur}>
          <View style={styles.dockInner}>
            {DOCK_APPS.map((slot, index) => (
              <AppIcon key={slot.id} slot={slot} index={index} isDock onPress={() => handleOpenApp(slot.id)} />
            ))}
          </View>
        </BlurView>
      </View>

      {/* 🔮 物理エンジンで転がる「統合思考コア」 */}
      <DraggableCore />

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  glowOrb: { position: 'absolute', width: 400, height: 400, borderRadius: 200, opacity: 0.6 },
  orb1: { top: -100, left: -100, backgroundColor: '#3b82f6', filter: 'blur(100px)' as any },
  wallpaperOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 0 },
  
  iosStatusBar: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 16, zIndex: 10 },
  iosTimeText: { color: '#FFF', fontSize: 13, fontWeight: 'bold', fontFamily: 'Outfit_700Bold', letterSpacing: 1 },
  iosStatusIcons: { flexDirection: 'row', alignItems: 'center' },
  iosSignalText: { color: '#FFF', fontSize: 11, fontWeight: '600', marginLeft: 6 },
  pulseDot: { width: 6, height: 6, borderRadius: 3, shadowColor: '#00FF99', shadowOpacity: 1, shadowRadius: 5 },
  
  homeGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 16, paddingTop: 40, zIndex: 10, paddingBottom: 150 },
  pcHomeGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', width: 800, alignSelf: 'center', paddingTop: 60, paddingBottom: 150 },
  
  appIconWrapper: { width: '25%', alignItems: 'center', marginBottom: 28 }, 
  appIconBox: { width: width > 600 ? 76 : 64, height: width > 600 ? 76 : 64, borderRadius: 18, overflow: 'hidden', shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.5, shadowRadius: 8 },
  appIconGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  lockedIconOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.5)' },
  appLabel: { color: '#FFF', fontSize: 11, fontFamily: 'Outfit_400Regular', marginTop: 8, textAlign: 'center', width: '120%' },
  
  dockContainer: { position: 'absolute', bottom: Platform.OS === 'ios' ? 30 : 20, left: 16, right: 16, borderRadius: 32, overflow: 'hidden', zIndex: 20 },
  pcDockContainer: { width: 400, alignSelf: 'center', left: undefined, right: undefined, bottom: 30, borderRadius: 40 },
  dockBlur: { paddingVertical: 18, paddingHorizontal: 12 },
  dockInner: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  
  floatingBackButton: { position: 'absolute', top: Platform.OS === 'web' ? 20 : 50, left: 20, zIndex: 100, borderRadius: 20, overflow: 'hidden' },
  backButtonBlur: { paddingHorizontal: 16, paddingVertical: 10, backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 20 },
  floatingBackText: { color: '#FFF', fontSize: 13, fontWeight: 'bold' },

  // コロコロ転がる物理オーブのスタイル
  floatingCore: { width: 60, height: 60, borderRadius: 30, overflow: 'hidden', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)' },
  coreGradient: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center', opacity: 0.8 },
  coreGlow: { position: 'absolute', top: -10, left: -10, right: -10, bottom: -10, borderRadius: 40, backgroundColor: '#00D4FF', opacity: 0.3, filter: 'blur(10px)' as any, zIndex: -1 }
});
