import React from 'react';
import { StyleSheet, Text, View, ScrollView, Dimensions, Switch } from 'react-native';
import { BlurView } from 'expo-blur';
import { Settings, Cpu, Network, Database } from 'lucide-react-native';
import Animated, { FadeInUp, FadeInDown } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

const ConfigRow = ({ icon: Icon, title, desc, enabled }: any) => (
  <View style={styles.configRow}>
    <View style={styles.iconBox}>
      <Icon color="#FFF" size={20} />
    </View>
    <View style={styles.textCol}>
      <Text style={styles.rowTitle}>{title}</Text>
      <Text style={styles.rowDesc}>{desc}</Text>
    </View>
    <Switch value={enabled} trackColor={{ false: '#444', true: '#00FF99' }} thumbColor="#FFF" disabled />
  </View>
);

export default function ConfigScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <ScrollView contentContainerStyle={styles.inner} showsVerticalScrollIndicator={false}>
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <Settings color="#666" size={48} />
          <Text style={styles.title}>SYSTEM CONFIG</Text>
        </Animated.View>

        <Animated.View entering={FadeInUp.delay(200).springify()} style={styles.section}>
          <Text style={styles.sectionHeader}>AGENT CONNECTIVITY</Text>
          <BlurView intensity={60} tint="dark" style={styles.card}>
            <ConfigRow icon={Network} title="Browser-use CLI" desc="Auto Web Automation" enabled={true} />
            <View style={styles.divider} />
            <ConfigRow icon={Cpu} title="LLM Engine" desc="Google Gemini 2.5 Flash" enabled={true} />
            <View style={styles.divider} />
            <ConfigRow icon={Database} title="Local Storage" desc="External Brain Synchronization" enabled={false} />
          </BlurView>
        </Animated.View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow: { position: 'absolute', top: 50, right: -50, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#666666', opacity: 0.3, filter: 'blur(90px)' as any },
  inner: { paddingTop: 100, paddingHorizontal: 20, paddingBottom: 150 },
  header: { alignItems: 'center', marginBottom: 40 },
  title: { color: '#FFF', fontSize: 26, fontWeight: '900', fontFamily: 'Outfit_900Black', marginTop: 16, letterSpacing: 2 },
  
  section: { marginBottom: 30 },
  sectionHeader: { color: '#888', fontSize: 12, fontFamily: 'Outfit_700Bold', marginLeft: 16, marginBottom: 8, letterSpacing: 1 },
  card: { borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  configRow: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  iconBox: { width: 36, height: 36, borderRadius: 10, backgroundColor: 'rgba(102, 102, 102, 0.4)', justifyContent: 'center', alignItems: 'center' },
  textCol: { flex: 1, marginLeft: 16 },
  rowTitle: { color: '#FFF', fontSize: 16, fontFamily: 'Outfit_700Bold', marginBottom: 2 },
  rowDesc: { color: '#999', fontSize: 12, fontFamily: 'Outfit_400Regular' },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.05)', marginLeft: 68 }
});
