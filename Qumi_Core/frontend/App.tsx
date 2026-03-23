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

import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, withSpring } from 'react-native-reanimated';
import { useFonts, Outfit_400Regular, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';
import { Animated as RNAnimated, PanResponder } from 'react-native';

const { width, height } = Dimensions.get('window');
const BASE = '/Qumi';

// 12 Core OS Slots mapped to WBC HTML Simulations
const SLOTS = [
  { id: '01', name: 'VECTOR CORE',  icon: BrainCircuit,   color: '#00F0FF', sim: 'neural_brain' },
  { id: '02', name: 'WIKI INTEL',   icon: BookOpen,        color: '#00FF99', sim: 'content_memory' },
  { id: '03', name: 'TUTOR AI',     icon: GraduationCap,   color: '#00FF99', sim: 'intelligence_stream' },
  { id: '04', name: 'AI MEMO',      icon: FileText,        color: '#B026FF', sim: 'agent_core' },
  { id: '05', name: 'LOCAL LLM',    icon: Zap,             color: '#FF9E00', sim: 'terminal' },
  { id: '06', name: 'VISION',       icon: Camera,          color: '#FF0055', sim: 'digital_brain' },
  { id: '07', name: 'SECURITY',     icon: Shield,          color: '#444444', sim: 'encrypted_tunnel' },
  { id: '08', name: 'SOUND',        icon: Mic,             color: '#00D4FF', sim: 'quantum_core' },
  { id: '09', name: 'DAILY LOG',    icon: Calendar,        color: '#FF5C93', sim: 'holo_calendar' },
  { id: '10', name: 'NOVEL STD',    icon: MessageSquare,   color: '#FF00B3', sim: 'cyber_city' },
  { id: '11', name: 'G-MAPS',       icon: Map,             color: '#00CC44', sim: 'globe_nexus' },
  { id: '12', name: 'SYS CONFIG',   icon: Settings,        color: '#666666', sim: 'system_monitor' },
];

// === Bouncy App Icon ===
const AppIcon = ({ slot, index, isDock = false, onPress }: { slot: any; index: number; isDock?: boolean; onPress: () => void }) => {
  const Icon = slot.icon;
  const scale = useSharedValue(1);
  const handlePressIn = () => { scale.value = withSpring(0.82, { damping: 12, stiffness: 500 }); };
  const handlePressOut = () => { scale.value = withSpring(1, { damping: 12, stiffness: 300 }); };
  const animatedStyle = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));

  return (
    <Animated.View entering={FadeInDown.delay(index * 35).springify().damping(14)} style={styles.appIconWrapper}>
      <TouchableOpacity activeOpacity={1} onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress} style={{ alignItems: 'center' }}>
        <Animated.View style={[styles.appIconBox, animatedStyle]}>
          <LinearGradient colors={[`${slot.color}DD`, `${slot.color}66`]} style={styles.appIconGradient}>
            <Icon color="#FFFFFF" size={isDock ? 30 : 26} strokeWidth={1.5} />
          </LinearGradient>
        </Animated.View>
        {!isDock && <Text style={styles.appLabel} numberOfLines={1}>{slot.name}</Text>}
      </TouchableOpacity>
    </Animated.View>
  );
};

// === Physics Draggable Core ===
const DraggableCore = () => {
  const pan = useRef(new RNAnimated.ValueXY({ x: 0, y: height / 3 })).current;
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

// === Simulation Viewer (iframe embedding WBC HTMLs) ===
const SimViewer = ({ simName, onBack }: { simName: string; onBack: () => void }) => {
  const simUrl = `${BASE}/sims/${simName}.html`;
  
  return (
    <View style={{ flex: 1, backgroundColor: '#000' }}>
      <TouchableOpacity style={styles.floatingBackButton} onPress={onBack} activeOpacity={0.7}>
        <BlurView intensity={80} tint="dark" style={styles.backButtonBlur}>
          <Text style={styles.floatingBackText}>← System Home</Text>
        </BlurView>
      </TouchableOpacity>
      {Platform.OS === 'web' ? (
        <iframe 
          src={simUrl} 
          style={{ width: '100%', height: '100%', border: 'none', backgroundColor: '#000' } as any}
          allow="accelerometer; autoplay; camera; microphone"
        />
      ) : (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Text style={{ color: '#FFF', fontSize: 16 }}>Web Only Module</Text>
        </View>
      )}
    </View>
  );
};

// === Main App ===
export default function App() {
  const [currentScreen, setCurrentScreen] = useState<string>('home');
  const [fontsLoaded] = useFonts({ Outfit_400Regular, Outfit_700Bold, Outfit_900Black });
  const orb1X = useSharedValue(0);
  const orb1Y = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(150, { duration: 20000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-150, { duration: 18000, easing: Easing.inOut(Easing.ease) }), -1, true);

    // PWA Auto Cache Buster
    const enforceUpdate = async () => {
      if (Platform.OS !== 'web') return;
      try {
        const r = await fetch(`${BASE}/version.json?t=${Date.now()}`);
        const d = await r.json();
        const cur = await AsyncStorage.getItem('@qumi_pwa_version');
        if (cur !== d.version) {
          await AsyncStorage.setItem('@qumi_pwa_version', d.version);
          if (cur !== null) window.location.reload(true);
        }
      } catch (e) {}
    };
    enforceUpdate();
  }, []);

  const orb1Style = useAnimatedStyle(() => ({ transform: [{ translateX: orb1X.value }, { translateY: orb1Y.value }] }));

  if (!fontsLoaded) return <View style={{ flex: 1, backgroundColor: '#000' }} />;

  const DOCK_APPS = SLOTS.filter(s => ['04', '03', '09'].includes(s.id));
  const HOME_APPS = SLOTS.filter(s => !['04', '03', '09'].includes(s.id));

  // Open slot => show its WBC simulation
  if (currentScreen !== 'home') {
    const slot = SLOTS.find(s => s.id === currentScreen);
    if (slot) {
      return <SimViewer simName={slot.sim} onBack={() => setCurrentScreen('home')} />;
    }
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
        {HOME_APPS.map((slot, index) => (
          <AppIcon key={slot.id} slot={slot} index={index} onPress={() => setCurrentScreen(slot.id)} />
        ))}
      </ScrollView>

      <View style={[styles.dockContainer, isPC && styles.pcDockContainer]}>
        <BlurView intensity={80} tint="dark" style={styles.dockBlur}>
          <View style={styles.dockInner}>
            {DOCK_APPS.map((slot, index) => (
              <AppIcon key={slot.id} slot={slot} index={index} isDock onPress={() => setCurrentScreen(slot.id)} />
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
