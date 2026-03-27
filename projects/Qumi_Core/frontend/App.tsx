import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet, Text, View, TouchableOpacity, SafeAreaView,
  StatusBar, Dimensions, ScrollView, Platform, TextInput, Modal, ActivityIndicator
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { 
  BrainCircuit, LayoutGrid, FileText, 
  Settings, Sparkles, Shield, Mic, Send, X, ChevronRight
} from 'lucide-react-native';

import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Animated, { 
  FadeInDown, useSharedValue, useAnimatedStyle, 
  withRepeat, withTiming, Easing, withSpring 
} from 'react-native-reanimated';
import { useFonts, Outfit_400Regular, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';
import { Animated as RNAnimated, PanResponder } from 'react-native';

const { width, height } = Dimensions.get('window');
const BASE = '/Qumi';
const API_BASE = 'http://localhost:8000';

const SLOTS = [
  { id: '01', name: 'CORE LOG',    icon: Database,     color: '#00F0FF', sim: 'game_01', cat: 'INTEL', layer: 'INTEL', desc: 'AIの学習履歴とスキル確認' },
  { id: '04', name: 'SOUL HUB',    icon: BrainCircuit, color: '#B026FF', sim: 'game_04', cat: 'INTEL', layer: 'THOUGHT', desc: '構造化された思考の保存庫' },
  { id: '09', name: 'KNOWLEDGE',   icon: FileText,     color: '#FF5C93', sim: 'game_09', cat: 'INTEL', layer: 'INTEL', desc: '外部脳ナレッジベース' },
  
  { id: '06', name: 'SYSTEM 3D',   icon: Activity,     color: '#FF0055', sim: 'game_06', cat: 'VISUAL', layer: 'SYSTEM', desc: 'OS稼働状況の3D可視化' },
  { id: '14', name: 'SWARM FLOW',  icon: Sparkles,     color: '#00D4FF', sim: 'game_14', cat: 'VISUAL', layer: 'SENSE', desc: 'データフローの粒子表現' },
  { id: '15', name: 'TOPOLOGY',    icon: LayoutGrid,   color: '#FF9E00', sim: 'game_15', cat: 'VISUAL', layer: 'SENSE', desc: 'ネットワーク構造の歪み' },
  
  { id: '08', name: 'VOICE SENSE', icon: Mic,          color: '#00FF99', sim: 'game_08', cat: 'SYSTEM', layer: 'SENSE', desc: '音声認識と聴覚コア' },
  { id: '12', name: 'OS CONFIG',   icon: Settings,     color: '#666666', sim: 'game_12', cat: 'SYSTEM', layer: 'SYSTEM', desc: 'システム詳細設定' },
  { id: '16', name: 'SECURITY',    icon: Shield,       color: '#444444', sim: 'game_16', cat: 'SYSTEM', layer: 'SYSTEM', desc: 'アクセス権限と防壁' },
];

// Helper icons because Database and Activity might be missing from some builds of lucide-react-native
const Database = (props: any) => <FileText {...props} />;
const Activity = (props: any) => <Sparkles {...props} />;

const AppIcon = ({ slot, index, onPress }: { slot: any; index: number; onPress: () => void }) => {
  const Icon = slot.icon;
  const scale = useSharedValue(1);
  const translateY = useSharedValue(0);

  useEffect(() => {
    translateY.value = withRepeat(
      withTiming(index % 2 === 0 ? -4 : 4, {
        duration: 2000 + (index * 200),
        easing: Easing.inOut(Easing.ease),
      }),
      -1,
      true
    );
  }, []);

  const handlePressIn = () => { scale.value = withSpring(0.82, { damping: 12, stiffness: 500 }); };
  const handlePressOut = () => { scale.value = withSpring(1, { damping: 12, stiffness: 300 }); };
  
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { translateY: translateY.value }
    ]
  }));

  return (
    <Animated.View entering={FadeInDown.delay(index * 50).springify().damping(14)} style={styles.appIconWrapper}>
      <TouchableOpacity activeOpacity={1} onPressIn={handlePressIn} onPressOut={handlePressOut} onPress={onPress} style={{ alignItems: 'center' }}>
        <Animated.View style={[styles.appIconBox, animatedStyle]}>
          <LinearGradient colors={[`${slot.color}DD`, `${slot.color}55`]} style={styles.appIconGradient}>
            <Icon color="#FFFFFF" size={26} strokeWidth={1.5} />
          </LinearGradient>
        </Animated.View>
        <Text style={styles.appLabel} numberOfLines={1}>{slot.name}</Text>
      </TouchableOpacity>
    </Animated.View>
  );
};

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

const DraggableCore = ({ onPress }: { onPress: () => void }) => {
  const pan = useRef(new RNAnimated.ValueXY({ x: 0, y: height / 2.5 })).current;
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderGrant: () => { 
        pan.setOffset({ x: (pan.x as any)._value, y: (pan.y as any)._value }); 
        pan.setValue({ x: 0, y: 0 }); 
      },
      onPanResponderMove: RNAnimated.event([null, { dx: pan.x, dy: pan.y }], { useNativeDriver: false }),
      onPanResponderRelease: (_, gs) => {
        pan.flattenOffset();
        if (Math.abs(gs.dx) < 5 && Math.abs(gs.dy) < 5) { onPress(); }
        RNAnimated.spring(pan, { 
          toValue: { x: gs.moveX > width / 2 ? width / 2 - 40 : -width / 2 + 40, y: (pan.y as any)._value + gs.vy * 50 }, 
          friction: 6, tension: 40, useNativeDriver: false 
        }).start();
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

const ThoughtModal = ({ visible, onClose }: { visible: boolean, onClose: () => void }) => {
  const [thought, setThought] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [persona, setPersona] = useState('soul');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];
      mediaRecorder.current.ondataavailable = (e) => audioChunks.current.push(e.data);
      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        handleVoiceUpload(audioBlob);
      };
      mediaRecorder.current.start();
      setIsRecording(true);
    } catch (err) { alert('Microphone access denied'); }
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    setIsRecording(false);
  };

  const handleVoiceUpload = async (blob: Blob) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    try {
      const response = await fetch(`${API_BASE}/voice?persona=${persona}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.transcription) {
        setThought(data.transcription);
        setResult(data.structured_result);
      }
    } catch (error) { alert('Voice Processing Error'); }
    finally { setLoading(false); }
  };

  const handleDelegate = async () => {
    if (!thought) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/delegate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thought, persona })
      });
      const data = await response.json();
      setResult(data.result);
    } catch (error) { console.error(error); alert('Error connecting to Qumi Backend'); }
    finally { setLoading(false); }
  };

  const getPersonaColor = () => {
    if (persona === 'grill') return '#FF0055';
    if (persona === 'hermes') return '#00D4FF';
    return '#A020F0';
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <BlurView intensity={90} tint="dark" style={styles.modalOverlay}>
        <SafeAreaView style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={[styles.modalTitle, { color: getPersonaColor() }]}>
              {persona.toUpperCase()} DELEGATION
            </Text>
            <TouchableOpacity onPress={onClose}><X color="#FFF" size={24} /></TouchableOpacity>
          </View>
          
          <View style={styles.personaBar}>
            {['soul', 'grill', 'hermes'].map(p => (
              <TouchableOpacity 
                key={p} 
                onPress={() => setPersona(p)}
                style={[styles.personaTab, persona === p && { backgroundColor: getPersonaColor() + '44', borderColor: getPersonaColor() }]}
              >
                <Text style={[styles.personaText, persona === p && { color: '#FFF' }]}>{p.toUpperCase()}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {!result ? (
            <View style={styles.inputContainer}>
              <View style={{ position: 'relative' }}>
                <TextInput
                  style={styles.textInput}
                  placeholder={`${persona}の人格で思考を構造化します...`}
                  placeholderTextColor="rgba(255,255,255,0.4)"
                  value={thought}
                  onChangeText={setThought}
                  multiline
                />
                <TouchableOpacity 
                  style={[styles.micOverlay, isRecording && { backgroundColor: '#FF0055' }]} 
                  onPressIn={startRecording}
                  onPressOut={stopRecording}
                >
                  <Mic color="#FFF" size={24} />
                </TouchableOpacity>
              </View>

              <TouchableOpacity 
                style={[styles.sendButton, { backgroundColor: getPersonaColor() }, !thought && { opacity: 0.5 }]} 
                onPress={handleDelegate}
                disabled={loading || !thought}
              >
                {loading ? <ActivityIndicator color="#FFF" /> : <Send color="#FFF" size={20} />}
                <Text style={styles.sendButtonText}>{loading ? 'DELEGATING...' : 'DELEGATE TO AGENT'}</Text>
              </TouchableOpacity>
              {isRecording && <Text style={styles.recordingText}>RECORDING... RELEASE TO SEND</Text>}
            </View>
          ) : (
            <ScrollView style={styles.resultContainer}>
              <Text style={[styles.resultTitle, { color: getPersonaColor() }]}>// {persona.toUpperCase()} ANALYSIS COMPLETE</Text>
              <View style={styles.resultJsonBox}>
                <Text style={styles.resultJson}>{typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</Text>
              </View>
              <TouchableOpacity style={styles.resetButton} onPress={() => {setResult(null); setThought('');}}>
                <Text style={styles.resetButtonText}>NEW THOUGHT</Text>
              </TouchableOpacity>
            </ScrollView>
          )}
        </SafeAreaView>
      </BlurView>
    </Modal>
  );
};

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

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<string>('home');
  const [modalVisible, setModalVisible] = useState(false);
  const [fontsLoaded] = useFonts({ Outfit_400Regular, Outfit_700Bold, Outfit_900Black });
  
  const orb1X = useSharedValue(0);
  const orb1Y = useSharedValue(0);

  useEffect(() => {
    orb1X.value = withRepeat(withTiming(100, { duration: 25000, easing: Easing.inOut(Easing.ease) }), -1, true);
    orb1Y.value = withRepeat(withTiming(-100, { duration: 22000, easing: Easing.inOut(Easing.ease) }), -1, true);

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
        <View style={isPC ? styles.pcClusterWrapper : {}}>
          <SlotCluster title="THOUGHT LAYER" layer="THOUGHT" onOpenApp={setCurrentScreen} />
          <SlotCluster title="INTEL LAYER" layer="INTEL" onOpenApp={setCurrentScreen} />
          <SlotCluster title="SENSE LAYER" layer="SENSE" onOpenApp={setCurrentScreen} />
          <SlotCluster title="SYSTEM LAYER" layer="SYSTEM" onOpenApp={setCurrentScreen} />
        </View>
      </ScrollView>

      <DraggableCore onPress={() => setModalVisible(true)} />
      <ThoughtModal visible={modalVisible} onClose={() => setModalVisible(false)} />
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
  coreGlow: { position: 'absolute', top: -15, left: -15, right: -15, bottom: -15, borderRadius: 50, backgroundColor: '#A020F0', opacity: 0.4, filter: 'blur(15px)' as any, zIndex: -1 },

  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  modalContent: { width: width > 600 ? 500 : '90%', maxHeight: '80%', backgroundColor: 'rgba(15, 23, 42, 0.8)', borderRadius: 32, padding: 24, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  modalTitle: { color: '#00D4FF', fontSize: 14, fontFamily: 'Outfit_900Black', letterSpacing: 3 },
  
  personaBar: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  personaTab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)', marginHorizontal: 4 },
  personaText: { color: 'rgba(255,255,255,0.4)', fontSize: 10, fontFamily: 'Outfit_700Bold' },

  inputContainer: { width: '100%' },
  textInput: { color: '#FFF', fontSize: 16, fontFamily: 'Outfit_400Regular', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 16, padding: 20, minHeight: 150, textAlignVertical: 'top', marginBottom: 20 },
  micOverlay: { position: 'absolute', bottom: 30, right: 10, width: 44, height: 44, borderRadius: 22, backgroundColor: 'rgba(255,255,255,0.1)', justifyContent: 'center', alignItems: 'center' },
  recordingText: { color: '#FF0055', fontSize: 10, textAlign: 'center', marginTop: 10, fontWeight: 'bold' },

  sendButton: { backgroundColor: '#A020F0', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 18, borderRadius: 16 },
  sendButtonText: { color: '#FFF', fontSize: 13, fontFamily: 'Outfit_700Bold', marginLeft: 10, letterSpacing: 1 },
  
  resultContainer: { width: '100%' },
  resultTitle: { color: '#00FF99', fontSize: 12, fontFamily: 'Outfit_900Black', marginBottom: 12 },
  resultJsonBox: { backgroundColor: 'rgba(0,0,0,0.3)', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  resultJson: { color: '#00FF99', fontSize: 12, fontFamily: 'monospace' },
  resetButton: { marginTop: 20, padding: 16, alignItems: 'center', borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)' },
  resetButtonText: { color: '#AAA', fontSize: 11, fontFamily: 'Outfit_700Bold', letterSpacing: 2 }
});
