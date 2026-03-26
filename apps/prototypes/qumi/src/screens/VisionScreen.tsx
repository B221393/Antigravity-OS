import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Dimensions, TouchableOpacity } from 'react-native';
import { BlurView } from 'expo-blur';
import { Camera, Sparkles, Brain, ArrowRight } from 'lucide-react-native';
import Animated, { 
  FadeInUp, FadeInDown, withRepeat, withTiming, 
  useSharedValue, useAnimatedStyle, Easing, withDelay 
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');

export default function VisionScreen() {
  const scanY = useSharedValue(0);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(true);

  useEffect(() => {
    scanY.value = withRepeat(withTiming(height * 0.4, { duration: 2000, easing: Easing.inOut(Easing.ease) }), -1, true);

    // シミュレート: 3秒後に環境から知見を発掘
    const timer = setTimeout(() => {
      setSuggestion("記憶の外部化: インフラとしての記録");
      setIsScanning(false);
    }, 4000);

    return () => clearTimeout(timer);
  }, []);

  const scanStyle = useAnimatedStyle(() => ({ 
    transform: [{ translateY: scanY.value }],
    opacity: isScanning ? 1 : 0 
  }));

  return (
    <View style={styles.container}>
      <View style={styles.bgGlow} />
      <BlurView intensity={20} tint="dark" style={StyleSheet.absoluteFillObject} />

      <View style={styles.viewfinder}>
        {/* スキャンバーのアニメーション */}
        <Animated.View style={[styles.scanLine, scanStyle]} />

        {/* 四隅のカメラフレーム */}
        <View style={styles.corners}>
          <View style={[styles.corner, styles.topLeft]} />
          <View style={[styles.corner, styles.topRight]} />
          <View style={[styles.corner, styles.bottomLeft]} />
          <View style={[styles.corner, styles.bottomRight]} />
        </View>

        <View style={styles.centerTarget}>
          <Camera color={isScanning ? "#00FF66" : "#444"} size={40} />
          <Text style={[styles.targetText, !isScanning && { color: '#444' }]}>
            {isScanning ? "EVALUATING ENVIRONMENT VECTORS..." : "VECTORS STABILIZED"}
          </Text>
        </View>
      </View>

      {/* 環境連動の提案カード */}
      {suggestion && (
        <Animated.View entering={FadeInDown.springify()} style={styles.suggestionContainer}>
          <BlurView intensity={80} tint="dark" style={styles.suggestionBlur}>
            <View style={styles.cardHeader}>
              <Sparkles color="#00FF99" size={16} />
              <Text style={styles.cardLabel}>AMBIENT INSIGHT DISCOVERED</Text>
            </View>
            <Text style={styles.suggestionText}>{suggestion}</Text>
            <TouchableOpacity style={styles.actionBtn}>
              <Text style={styles.actionText}>SYUKATU OS SYNC</Text>
              <ArrowRight color="#00FF99" size={14} />
            </TouchableOpacity>
          </BlurView>
        </Animated.View>
      )}

      {!isScanning && (
        <TouchableOpacity style={styles.rescanBtn} onPress={() => { setIsScanning(true); setSuggestion(null); }}>
          <Text style={styles.rescanText}>RE-SCAN ENVIRONMENT</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' },
  bgGlow: { position: 'absolute', width: width, height: height, backgroundColor: '#00FF66', opacity: 0.05 },
  
  viewfinder: { width: width * 0.8, height: height * 0.45, position: 'relative', justifyContent: 'center', alignItems: 'center' },
  scanLine: { position: 'absolute', top: 0, left: 0, right: 0, height: 2, backgroundColor: '#00FF66', shadowColor: '#00FF66', shadowOpacity: 1, shadowRadius: 10, zIndex: 10 },
  
  corners: { ...StyleSheet.absoluteFillObject },
  corner: { position: 'absolute', width: 30, height: 30, borderColor: '#00FF66', borderWidth: 2 },
  topLeft: { top: 0, left: 0, borderRightWidth: 0, borderBottomWidth: 0 },
  topRight: { top: 0, right: 0, borderLeftWidth: 0, borderBottomWidth: 0 },
  bottomLeft: { bottom: 0, left: 0, borderRightWidth: 0, borderTopWidth: 0 },
  bottomRight: { bottom: 0, right: 0, borderLeftWidth: 0, borderTopWidth: 0 },
  
  centerTarget: { alignItems: 'center' },
  targetText: { color: '#00FF66', fontSize: 10, fontWeight: '900', marginTop: 16, letterSpacing: 2 },

  suggestionContainer: { position: 'absolute', bottom: 100, width: width * 0.85, borderRadius: 24, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0, 255, 153, 0.2)' },
  suggestionBlur: { padding: 20, backgroundColor: 'rgba(0, 255, 153, 0.05)' },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  cardLabel: { color: '#00FF99', fontSize: 10, fontWeight: '900', marginLeft: 8, letterSpacing: 1 },
  suggestionText: { color: '#FFF', fontSize: 16, fontWeight: '700', lineHeight: 24, marginBottom: 16 },
  
  actionBtn: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start' },
  actionText: { color: '#00FF99', fontSize: 11, fontWeight: '900', marginRight: 8, letterSpacing: 1 },

  rescanBtn: { position: 'absolute', top: 60, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20, backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  rescanText: { color: '#666', fontSize: 10, fontWeight: '900', letterSpacing: 2 }
});
