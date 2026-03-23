import React from 'react';
import { StyleSheet, Text, View, Dimensions } from 'react-native';
import { BlurView } from 'expo-blur';
import { LinearGradient } from 'expo-linear-gradient';
import { Shield, Lock, Fingerprint } from 'lucide-react-native';
import Animated, { FadeInUp, FadeInDown } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

export default function SecurityScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={100} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.inner}>
        <Animated.View entering={FadeInDown.springify()} style={styles.header}>
          <LinearGradient colors={['#FF3366', '#A020F0']} style={styles.iconCircle}>
            <Shield color="#FFF" size={32} />
          </LinearGradient>
          <Text style={styles.title}>SECURITY</Text>
          <Text style={styles.subtitle}>外部脳データ保護：稼働中</Text>
        </Animated.View>

        <View style={styles.settingsList}>
          <Animated.View entering={FadeInUp.delay(200).springify()} style={styles.settingItem}>
            <Lock color="#FF3366" size={24} />
            <View style={styles.settingTextContainer}>
              <Text style={styles.settingTitle}>Local Vector Vault</Text>
              <Text style={styles.settingDesc}>AES-256 Encrypted</Text>
            </View>
            <View style={styles.statusOn}><Text style={styles.statusText}>SECURE</Text></View>
          </Animated.View>

          <Animated.View entering={FadeInUp.delay(300).springify()} style={styles.settingItem}>
            <Fingerprint color="#FF3366" size={24} />
            <View style={styles.settingTextContainer}>
              <Text style={styles.settingTitle}>Identity Sync</Text>
              <Text style={styles.settingDesc}>Face / Touch Authentication</Text>
            </View>
            <View style={styles.statusOn}><Text style={styles.statusText}>ACTIVE</Text></View>
          </Animated.View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  bgGlow: { position: 'absolute', top: 150, left: 0, width: width*0.9, height: width*0.9, borderRadius: width, backgroundColor: '#FF3366', opacity: 0.2, filter: 'blur(90px)' as any },
  inner: { flex: 1, paddingTop: 100, paddingHorizontal: 24 },
  header: { alignItems: 'center', marginBottom: 50 },
  iconCircle: { width: 80, height: 80, borderRadius: 40, justifyContent: 'center', alignItems: 'center', shadowColor: '#FF3366', shadowOpacity: 0.8, shadowRadius: 20 },
  title: { color: '#FFF', fontSize: 28, fontWeight: '900', fontFamily: 'Outfit_900Black', marginTop: 24, letterSpacing: 2 },
  subtitle: { color: '#FF3366', fontSize: 13, fontFamily: 'Outfit_700Bold', marginTop: 6, letterSpacing: 1 },
  settingsList: { marginTop: 20 },
  settingItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(30, 20, 20, 0.6)', padding: 20, borderRadius: 20, marginBottom: 16, borderWidth: 1, borderColor: 'rgba(255, 51, 102, 0.2)' },
  settingTextContainer: { flex: 1, marginLeft: 16 },
  settingTitle: { color: '#FFF', fontSize: 16, fontFamily: 'Outfit_700Bold', marginBottom: 4 },
  settingDesc: { color: '#AAA', fontSize: 12, fontFamily: 'Outfit_400Regular' },
  statusOn: { backgroundColor: 'rgba(0, 255, 153, 0.2)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12 },
  statusText: { color: '#00FF99', fontSize: 10, fontFamily: 'Outfit_700Bold', letterSpacing: 1 }
});
