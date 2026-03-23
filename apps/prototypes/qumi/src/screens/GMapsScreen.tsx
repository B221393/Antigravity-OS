import React from 'react';
import { StyleSheet, Text, View, Dimensions } from 'react-native';
import { BlurView } from 'expo-blur';
import { Map as MapIcon, Navigation } from 'lucide-react-native';
import Animated, { FadeInUp, withRepeat, withTiming, useSharedValue, useAnimatedStyle, Easing } from 'react-native-reanimated';

const { width } = Dimensions.get('window');

export default function GMapsScreen() {
  const pulse = useSharedValue(1);
  const opacity = useSharedValue(1);

  React.useEffect(() => {
    pulse.value = withRepeat(withTiming(3, { duration: 2000, easing: Easing.out(Easing.quad) }), -1, false);
    opacity.value = withRepeat(withTiming(0, { duration: 2000, easing: Easing.out(Easing.quad) }), -1, false);
  }, []);

  const ringStyle = useAnimatedStyle(() => ({ transform: [{ scale: pulse.value }], opacity: opacity.value }));

  return (
    <View style={styles.container}>
      {/* モックマップグリッド背景 */}
      <View style={styles.gridBg} />
      <View style={styles.bgGlow} />

      <View style={styles.mapCenter}>
        <Animated.View style={[styles.pulseRing, ringStyle]} />
        <View style={styles.locationDot}>
          <View style={styles.locationDotInner} />
        </View>
      </View>

      {/* Apple Maps風 フローティングボトムシート */}
      <Animated.View entering={FadeInUp.delay(300).springify().damping(15)} style={styles.bottomSheet}>
        <BlurView intensity={90} tint="dark" style={styles.sheetBlur}>
          <View style={styles.sheetHandle} />
          <Text style={styles.sheetTitle}>Tracking Vectors</Text>
          <Text style={styles.sheetSubtitle}>Current Geo-Context Synchronized</Text>
          
          <View style={styles.actionRow}>
            <View style={styles.actionBtn}>
              <Navigation color="#FFF" size={20} />
            </View>
            <View style={{ flex: 1, marginLeft: 16 }}>
              <Text style={styles.actionText}>Physical Journey Sync</Text>
              <Text style={styles.actionSubText}>Recording real-world insights...</Text>
            </View>
          </View>
        </BlurView>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#001A1A' },
  gridBg: { ...StyleSheet.absoluteFillObject, opacity: 0.1, backgroundImage: 'linear-gradient(#00F5D4 1px, transparent 1px), linear-gradient(90deg, #00F5D4 1px, transparent 1px)', backgroundSize: '40px 40px' as any },
  bgGlow: { position: 'absolute', top: 200, left: 100, width: width*0.8, height: width*0.8, borderRadius: width, backgroundColor: '#00F5D4', opacity: 0.1, filter: 'blur(90px)' as any },
  
  mapCenter: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  pulseRing: { position: 'absolute', width: 60, height: 60, borderRadius: 30, backgroundColor: 'rgba(0, 245, 212, 0.4)' },
  locationDot: { width: 24, height: 24, borderRadius: 12, backgroundColor: 'rgba(0, 245, 212, 0.3)', justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: '#00F5D4', shadowColor: '#00F5D4', shadowOpacity: 1, shadowRadius: 15 },
  locationDotInner: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#FFF' },

  bottomSheet: { position: 'absolute', bottom: 0, left: 0, right: 0, borderTopLeftRadius: 32, borderTopRightRadius: 32, overflow: 'hidden', height: 250 },
  sheetBlur: { flex: 1, padding: 24 },
  sheetHandle: { width: 50, height: 5, backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: 3, alignSelf: 'center', marginBottom: 20 },
  sheetTitle: { color: '#FFF', fontSize: 24, fontFamily: 'Outfit_700Bold', marginBottom: 4 },
  sheetSubtitle: { color: '#00F5D4', fontSize: 13, fontFamily: 'Outfit_400Regular', marginBottom: 24 },
  actionRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(0, 245, 212, 0.1)', padding: 16, borderRadius: 20 },
  actionBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#00F5D4', justifyContent: 'center', alignItems: 'center' },
  actionText: { color: '#FFF', fontSize: 15, fontFamily: 'Outfit_700Bold' },
  actionSubText: { color: '#AAA', fontSize: 12, fontFamily: 'Outfit_400Regular', marginTop: 4 }
});
