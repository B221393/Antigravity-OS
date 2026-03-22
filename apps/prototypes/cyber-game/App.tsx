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
import Animated, { FadeIn, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, withSpring } from 'react-native-reanimated';
import { useFonts, Outfit_400Regular, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';

const { width } = Dimensions.get('window');

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

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'memo' | 'tutor' | 'vector' | 'game' | 'diary' | 'novel'>('home');

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
        {currentScreen === 'diary' && <DailyDiaryScreen onBack={() => setCurrentScreen('home')} />}
        {currentScreen === 'novel' && <NovelStudioScreen onBack={() => setCurrentScreen('home')} />}
      </Animated.View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      
      <Animated.View style={[styles.glowOrb, styles.orb1, orb1Style]} />
      <View style={styles.wallpaperOverlay} />

      <View style={styles.iosStatusBar}>
        <Text style={styles.iosTimeText}>VECTIS OS</Text>
        <View style={styles.iosStatusIcons}>
          <View style={[styles.pulseDot, { backgroundColor: '#00FF99' }]} />
          <Text style={styles.iosSignalText}>MCP Connected</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.homeGrid} showsVerticalScrollIndicator={false}>
        {HOME_APPS.map((slot, index) => (
          <AppIcon key={slot.id} slot={slot} index={index} onPress={() => handleOpenApp(slot.id)} />
        ))}
      </ScrollView>

      <View style={styles.dockContainer}>
        <BlurView intensity={60} tint="dark" style={styles.dockBlur}>
          <View style={styles.dockInner}>
            {DOCK_APPS.map((slot, index) => (
              <AppIcon key={slot.id} slot={slot} index={index} isDock onPress={() => handleOpenApp(slot.id)} />
            ))}
          </View>
        </BlurView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  glowOrb: { position: 'absolute', width: 400, height: 400, borderRadius: 200, opacity: 0.6 },
  orb1: { top: -100, left: -100, backgroundColor: '#3b82f6', filter: 'blur(100px)' as any },
  wallpaperOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 0 },
  iosStatusBar: { flexDirection: 'row', justifyContent: 'space-between', paddingHorizontal: 24, paddingTop: 16, zIndex: 10 },
  iosTimeText: { color: '#FFF', fontSize: 13, fontWeight: 'bold', fontFamily: 'Outfit_700Bold' },
  iosStatusIcons: { flexDirection: 'row', alignItems: 'center' },
  iosSignalText: { color: '#FFF', fontSize: 11, fontWeight: '600', marginLeft: 6 },
  pulseDot: { width: 6, height: 6, borderRadius: 3, shadowColor: '#00FF99', shadowOpacity: 1, shadowRadius: 5 },
  homeGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 16, paddingTop: 40, zIndex: 10 },
  appIconWrapper: { width: '25%', alignItems: 'center', marginBottom: 28 }, 
  appIconBox: { width: width > 600 ? 80 : 64, height: width > 600 ? 80 : 64, borderRadius: 16, overflow: 'hidden', shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.5, shadowRadius: 8 },
  appIconGradient: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  lockedIconOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.4)' },
  appLabel: { color: '#FFF', fontSize: 11, fontFamily: 'Outfit_400Regular', marginTop: 6, textAlign: 'center', width: '120%' },
  dockContainer: { position: 'absolute', bottom: Platform.OS === 'ios' ? 30 : 20, left: 16, right: 16, borderRadius: 32, overflow: 'hidden', zIndex: 20 },
  dockBlur: { paddingVertical: 16, paddingHorizontal: 8 },
  dockInner: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  floatingBackButton: { position: 'absolute', top: Platform.OS === 'web' ? 20 : 50, left: 20, zIndex: 100, borderRadius: 20, overflow: 'hidden' },
  backButtonBlur: { paddingHorizontal: 16, paddingVertical: 10, backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: 20 },
  floatingBackText: { color: '#FFF', fontSize: 13, fontWeight: 'bold' }
});
