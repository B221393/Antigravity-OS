import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView, Platform
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { 
  BrainCircuit, Gamepad2, GraduationCap, FileText, 
  MessageSquare, Camera, Shield, Mic, Calendar, 
  Zap, Map, Settings, Sparkles, BookOpen
} from 'lucide-react-native';

import AiMemoScreen from './src/screens/AiMemoScreen';
import EducationScreen from './src/screens/EducationScreen';
import VectorBrainScreen from './src/screens/VectorBrainScreen';
import DailyDiaryScreen from './src/screens/DailyDiaryScreen';
import ConfigScreen from './src/screens/ConfigScreen';
import WikiArchiveScreen from './src/screens/WikiArchiveScreen';
import LocalLlmScreen from './src/screens/LocalLlmScreen';
import VisionScreen from './src/screens/VisionScreen';
import SecurityScreen from './src/screens/SecurityScreen';
import SoundScreen from './src/screens/SoundScreen';
import GMapsScreen from './src/screens/GMapsScreen';
import NovelStudioScreen from './src/screens/NovelStudioScreen';

import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, withSpring } from 'react-native-reanimated';
import { useFonts, Outfit_400Regular, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';

const { width, height } = Dimensions.get('window');

const SLOTS = [
  { id: '04', name: 'AI MEMO', icon: FileText, color: '#B026FF', available: true },
  { id: '03', name: 'TUTOR AI', icon: GraduationCap, color: '#00FF99', available: true },
  { id: '09', name: 'DAILY LOG', icon: Calendar, color: '#FF5C93', available: true },
  { id: '01', name: 'VECTOR CORE', icon: BrainCircuit, color: '#00F0FF', available: true },
  { id: '02', name: 'WIKI INTEL', icon: BookOpen, color: '#00FF99', available: true },
  { id: '05', name: 'LOCAL LLM', icon: Zap, color: '#FF9E00', available: true },
  { id: '06', name: 'VISION', icon: Camera, color: '#FF0055', available: true },
  { id: '07', name: 'SECURITY', icon: Shield, color: '#444444', available: true },
  { id: '08', name: 'SOUND', icon: Mic, color: '#00D4FF', available: true },
  { id: '10', name: 'NOVEL STD', icon: MessageSquare, color: '#FF00B3', available: true },
  { id: '11', name: 'G-MAPS', icon: Map, color: '#00CC44', available: true },
  { id: '12', name: 'SYS CONFIG', icon: Settings, color: '#666666', available: true }
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
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={onPress}
        style={{ alignItems: 'center' }}
      >
        <Animated.View style={[styles.appIconBox, animatedStyle]}>
          <LinearGradient colors={iconBg} style={styles.appIconGradient}>
            <Icon color="#FFFFFF" size={isDock ? 32 : 28} strokeWidth={1.5} />
          </LinearGradient>
        </Animated.View>
        {!isDock && (
          <Text style={styles.appLabel} numberOfLines={1}>{slot.name}</Text>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
};

// Physics Rolling Engine
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
  const [currentScreen, setCurrentScreen] = useState<string>('home');
  const [fontsLoaded] = useFonts({ Outfit_400Regular, Outfit_700Bold, Outfit_900Black });
  const orb1X = useSharedValue(0); 
  const orb1Y = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(150, { duration: 20000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-150, { duration: 18000, easing: Easing.inOut(Easing.ease) }), -1, true);

    const enforceUpdate = async () => {
      if (Platform.OS !== 'web') return;
      try {
        const response = await fetch(`/Qumi/version.json?t=${new Date().getTime()}`);
        const data = await response.json();
        const currentVersion = await AsyncStorage.getItem('@qumi_pwa_version');
        if (currentVersion !== data.version) {
          await AsyncStorage.setItem('@qumi_pwa_version', data.version);
          if (currentVersion !== null) {
            window.location.reload(true);
          }
        }
      } catch (e) {
        console.log('Update check failed', e);
      }
    };
    enforceUpdate();
  }, []);

  const orb1Style = useAnimatedStyle(() => ({ transform: [{ translateX: orb1X.value }, { translateY: orb1Y.value }] }));

  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: '#000' }} />;

  const DOCK_APPS = SLOTS.filter(s => ['04', '03', '09'].includes(s.id));
  const HOME_APPS = SLOTS.filter(s => !['04', '03', '09'].includes(s.id));

  const handleOpenApp = (id: string) => {
    setCurrentScreen(id);
  };

  if (currentScreen !== 'home') {
    return (
      <Animated.View entering={FadeIn.duration(300)} style={{ flex: 1, backgroundColor: '#000' }}>
        <TouchableOpacity style={styles.floatingBackButton} onPress={() => setCurrentScreen('home')} activeOpacity={0.7}>
          <BlurView intensity={80} tint="dark" style={styles.backButtonBlur}>
            <Text style={styles.floatingBackText}>← System Home</Text>
          </BlurView>
        </TouchableOpacity>

        {currentScreen === '01' && <VectorBrainScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === '02' && <WikiArchiveScreen />}
        {currentScreen === '03' && <EducationScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === '04' && <AiMemoScreen />}
        {currentScreen === '05' && <LocalLlmScreen />}
        {currentScreen === '06' && <VisionScreen />}
        {currentScreen === '07' && <SecurityScreen />}
        {currentScreen === '08' && <SoundScreen />}
        {currentScreen === '09' && <DailyDiaryScreen />}
        {currentScreen === '10' && <NovelStudioScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === '11' && <GMapsScreen />}
        {currentScreen === '12' && <ConfigScreen />}
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
        <Text style={styles.iosTimeText}>QUMI OS (UNIFIED)</Text>
        <View style={styles.iosStatusIcons}>
          <View style={[styles.pulseDot, { backgroundColor: '#00FF99' }]} />
          <Text style={styles.iosSignalText}>Agent Online</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={isPC ? styles.pcHomeGrid : styles.homeGrid} showsVerticalScrollIndicator={false}>
        {HOME_APPS.map((slot, index) => (
          <AppIcon key={slot.id} slot={slot} index={index} onPress={() => handleOpenApp(slot.id)} />
        ))}
      </ScrollView>

      <View style={[styles.dockContainer, isPC && styles.pcDockContainer]}>
        <BlurView intensity={80} tint="dark" style={styles.dockBlur}>
          <View style={styles.dockInner}>
            {DOCK_APPS.map((slot, index) => (
              <AppIcon key={slot.id} slot={slot} index={index} isDock onPress={() => handleOpenApp(slot.id)} />
            ))}
          </View>
        </BlurView>
      </View>

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
  appIconWrapper: { width: '25%', alignItems: 'center', marginBottom: 20 }, 
  appIconBox: { width: width > 600 ? 76 : 64, height: width > 600 ? 76 : 64, borderRadius: 18, overflow: 'hidden', shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.5, shadowRadius: 8 },
  appIconGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  appLabel: { color: '#FFF', fontSize: 11, fontFamily: 'Outfit_700Bold', marginTop: 8, textAlign: 'center', width: '120%' },
  dockContainer: { position: 'absolute', bottom: Platform.OS === 'ios' ? 30 : 20, left: 16, right: 16, borderRadius: 32, overflow: 'hidden', zIndex: 20 },
  pcDockContainer: { width: 400, alignSelf: 'center', left: undefined, right: undefined, bottom: 30, borderRadius: 40 },
  dockBlur: { paddingVertical: 18, paddingHorizontal: 24 },
  dockInner: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  floatingBackButton: { position: 'absolute', top: Platform.OS === 'web' ? 20 : 50, left: 20, zIndex: 100, borderRadius: 20, overflow: 'hidden' },
  backButtonBlur: { paddingHorizontal: 16, paddingVertical: 10, backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 20 },
  floatingBackText: { color: '#FFF', fontSize: 13, fontWeight: 'bold' },
  floatingCore: { width: 60, height: 60, borderRadius: 30, overflow: 'hidden', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)' },
  coreGradient: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center', opacity: 0.8 },
  coreGlow: { position: 'absolute', top: -10, left: -10, right: -10, bottom: -10, borderRadius: 40, backgroundColor: '#00D4FF', opacity: 0.3, filter: 'blur(10px)' as any, zIndex: -1 }
});
