# IOWN Edge Controller (IOWN-EC)

Innovative Optical and Wireless Network (IOWN) の低遅延・高帯域性能を活用したエッジ制御モバイル・ダッシュボード。

## 概要
本プロジェクトは、NTT西日本の IOWN 構想（オールフォトニクス・ネットワーク、エッジコンピューティング）をモバイル環境から実演・制御するためのプロトタイプ。

## 技術スタック
- **Framework**: React Native (Expo)
- **Language**: TypeScript
- **Backend Bridge**: Go (gRPC) / Rust (Warp)
- **Visualization**: Reanimated / Skia (High Performance UI)

## 主要機能
- **Real-time Latency Monitor**: IOWN APN による低遅延（<1ms）の視覚化。
- **Edge Actuator**: エッジサーバーへの高速コマンド送信インターフェース。
- **Node Status**: 分散エッジノードのヘルスチェック。

## セットアップ
```bash
cd apps/prototypes/IOWN-Edge-Controller
npm install
npx expo start
```

---
*Created by Antigravity Autonomous System Builder*
