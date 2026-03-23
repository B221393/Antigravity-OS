import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, Platform, Dimensions, TextInput, TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Calendar, Clock, Plus } from 'lucide-react-native';
import Animated, { FadeInUp, FadeInDown, useSharedValue, useAnimatedStyle, withRepeat, withTiming, Easing, Layout } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

const DEFAULT_LOGS = [
  { id: '1', time: '09:00 AM', title: 'Qumi OS Architecture', desc: 'UI設計とCLIエージェント層（抽象レイヤー）を独立Publicリポジトリとして分離構築。' },
  { id: '2', time: '10:30 AM', title: 'Physics UI Engine', desc: '指の弾きでコロコロ転がり吸い付く物理演算コアを実装。未知への探求心の具現化。' }
];

export default function DailyDiaryScreen() {
  const [logs, setLogs] = useState(DEFAULT_LOGS);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  
  const pulse = useSharedValue(1);

  useEffect(() => {
    pulse.value = withRepeat(withTiming(1.3, { duration: 2000, easing: Easing.inOut(Easing.ease) }), -1, true);
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const savedLogs = await AsyncStorage.getItem('@qumi_daily_logs');
      if (savedLogs !== null) setLogs(JSON.parse(savedLogs));
    } catch (e) {
      console.log('Failed to load logs');
    }
  };

  const saveLog = async () => {
    if (!newTitle.trim() && !newDesc.trim()) return;
    const now = new Date();
    let hours = now.getHours();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const min = now.getMinutes().toString().padStart(2, '0');
    
    const newEntry = {
      id: Date.now().toString(),
      time: `${hours}:${min} ${ampm}`,
      title: newTitle || 'Thought Vector',
      desc: newDesc
    };
    
    const updatedLogs = [...logs, newEntry];
    setLogs(updatedLogs);
    setNewTitle('');
    setNewDesc('');
    
    try {
      await AsyncStorage.setItem('@qumi_daily_logs', JSON.stringify(updatedLogs));
    } catch (e) {
      console.log('Failed to save log');
    }
  };

  const ringStyle = useAnimatedStyle(() => ({ transform: [{ scale: pulse.value }] }));

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow1} />
      <View style={styles.bgGlow2} />
      <BlurView intensity={Platform.OS === 'ios' ? 80 : 100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        
        <Animated.View entering={FadeInDown.delay(100).springify()} style={styles.header}>
          <View style={{ position: 'relative', width: 80, height: 80, justifyContent: 'center', alignItems: 'center' }}>
            <Animated.View style={[styles.pulseRing, ringStyle]} />
            <LinearGradient colors={['#FF5C93', '#FFAE00']} style={styles.syncCircle}>
              <Calendar color="#FFF" size={32} />
            </LinearGradient>
          </View>
          <Text style={styles.title}>DAILY LOG</Text>
          <Text style={styles.subtitle}>Memory Persisted via AsyncStorage</Text>
        </Animated.View>

        {/* Input Area (New feature to literally commit Memory) */}
        <Animated.View entering={FadeInDown.delay(200).springify()} style={styles.inputContainer}>
          <BlurView intensity={60} tint="dark" style={styles.inputBlur}>
            <TextInput 
              style={styles.inputTitle} 
              placeholder="Abstract Title..." 
              placeholderTextColor="#888" 
              value={newTitle} 
              onChangeText={setNewTitle} 
            />
            <TextInput 
              style={styles.inputDesc} 
              placeholder="Record your thoughts or events..." 
              placeholderTextColor="#666" 
              multiline 
              value={newDesc} 
              onChangeText={setNewDesc} 
            />
            <TouchableOpacity style={styles.addButton} onPress={saveLog}>
              <LinearGradient colors={['#FF5C93', '#FFAE00']} style={styles.addButtonGrad} start={{x:0, y:0}} end={{x:1, y:1}}>
                <Plus color="#FFF" size={20} />
                <Text style={styles.addButtonText}>Save Memory</Text>
              </LinearGradient>
            </TouchableOpacity>
          </BlurView>
        </Animated.View>

        <View style={styles.timeline}>
          <View style={styles.timelineLine} />
          {logs.map((log, index) => (
             /* Layout allows smooth list pushing */
            <Animated.View key={log.id} layout={Layout.springify()} entering={FadeInUp.delay(index * 100).springify().damping(15)} style={styles.cardWrapper}>
               <View style={styles.timelineDot}>
                  <View style={styles.timelineInnerDot} />
               </View>
               <BlurView intensity={60} tint="dark" style={styles.logCard}>
                  <View style={styles.cardHeader}>
                    <Clock color="#FF5C93" size={14} />
                    <Text style={styles.timeText}>{log.time}</Text>
                  </View>
                  <Text style={styles.logTitle}>{log.title}</Text>
                  <Text style={styles.logDesc}>{log.desc}</Text>
               </BlurView>
            </Animated.View>
          ))}
        </View>
        
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow1: { position: 'absolute', top: -50, left: -50, width: width, height: width, borderRadius: width, backgroundColor: '#FF5C93', opacity: 0.3, filter: 'blur(100px)' as any },
  bgGlow2: { position: 'absolute', bottom: -50, right: -50, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#FFAE00', opacity: 0.3, filter: 'blur(100px)' as any },
  
  scrollContent: { paddingHorizontal: 20, paddingTop: Platform.OS === 'web' ? 80 : 120, paddingBottom: 150 },
  
  header: { alignItems: 'center', marginBottom: 30 },
  pulseRing: { position: 'absolute', width: 100, height: 100, borderRadius: 50, backgroundColor: 'rgba(255, 92, 147, 0.4)', borderWidth: 1, borderColor: '#FF5C93' },
  syncCircle: { width: 80, height: 80, borderRadius: 40, justifyContent: 'center', alignItems: 'center', shadowColor: '#FF5C93', shadowOpacity: 0.8, shadowRadius: 20 },
  title: { color: '#FFF', fontSize: 26, fontWeight: '900', fontFamily: 'Outfit_900Black', marginTop: 24, letterSpacing: 2 },
  subtitle: { color: '#FF5C93', fontSize: 13, fontFamily: 'Outfit_700Bold', marginTop: 6, letterSpacing: 1 },

  inputContainer: { marginBottom: 40, borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255, 92, 147, 0.4)' },
  inputBlur: { padding: 16, backgroundColor: 'rgba(30, 0, 10, 0.3)' },
  inputTitle: { color: '#FFF', fontSize: 18, fontFamily: 'Outfit_700Bold', borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.1)', paddingBottom: 8, marginBottom: 12 },
  inputDesc: { color: '#FFF', fontSize: 14, fontFamily: 'Outfit_400Regular', minHeight: 60, textAlignVertical: 'top' },
  addButton: { alignSelf: 'flex-end', marginTop: 12, borderRadius: 20, overflow: 'hidden' },
  addButtonGrad: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10 },
  addButtonText: { color: '#FFF', fontFamily: 'Outfit_700Bold', marginLeft: 6 },

  timeline: { position: 'relative', marginTop: 10, paddingLeft: 24, paddingRight: 8 },
  timelineLine: { position: 'absolute', left: 8, top: 0, bottom: 0, width: 2, backgroundColor: 'rgba(255,255,255,0.1)' },
  
  cardWrapper: { position: 'relative', marginBottom: 30 },
  timelineDot: { position: 'absolute', left: -26, top: 20, width: 20, height: 20, borderRadius: 10, backgroundColor: 'rgba(255, 92, 147, 0.3)', justifyContent: 'center', alignItems: 'center' },
  timelineInnerDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#FF5C93', shadowColor: '#FF5C93', shadowOpacity: 1, shadowRadius: 8 },

  logCard: { padding: 20, borderRadius: 24, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)', overflow: 'hidden', backgroundColor: 'rgba(30, 10, 20, 0.4)' },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  timeText: { color: '#FF5C93', fontSize: 13, fontFamily: 'Outfit_700Bold', marginLeft: 6, letterSpacing: 1 },
  logTitle: { color: '#FFF', fontSize: 18, fontFamily: 'Outfit_700Bold', marginBottom: 10 },
  logDesc: { color: '#CCC', fontSize: 14, fontFamily: 'Outfit_400Regular', lineHeight: 22 }
});
