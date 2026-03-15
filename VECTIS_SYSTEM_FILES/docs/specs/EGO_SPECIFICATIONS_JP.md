# EGO System Specifications (2026-02-02 Current)

## 1. システム概要 (System Overview)

EGO (Virtual Electronic Cybernetic Intelligence System) は、ユーザーの拡張脳として機能する統合エージェントOSです。
「端末内完結 (LocalFirst)」と「自律思考 (Agentic)」を設計思想としています。

### コアコンポーネント

- **Dashboard (OS)**: `OS/index.html` - システム全体のランチャー兼ステータスモニター。サイバーパンク調のUI。
- **Intelligence Hub**: `apps/MEDIA/INTELLIGENCE_HUB` - 情報収集の中枢。
- **Agent Skills**: `~/.gemini/skills` - 拡張可能な自律スキル群。

---

## 2. アクティブなスキル (Active Skills)

### 🧠 Deep Researcher (skill-deep-researcher)

- **機能**: 企業の「建前（公式サイト）」と「本音（口コミ）」を再帰的に調査し、分析レポートを生成。
- **現状**: KDDI, NTT, JERAの分析が完了・進行中。既存のESドラフトも知識源として統合済み。
- **出力**: `data/companies/{企業名}/REPORT_Soft_Analysis.md`

### ✍️ ES Architect (skill-es-architect)

- **機能**: ユーザーの `IDENTITY_CORE.md` を読み込み、企業ごとの「勝てるES」を代筆。
- **現状**: コマンドラインから特定の設問に対してドラフト生成が可能。

### 🎨 Universal UX Architect (apps/UX_Labs)

- **機能**: 複数のペルソナ（おばあちゃん、ハッカー、デザイナー）がアプリを操作し、辛辣なフィードバックを行う。
- **現状**: PoC（概念実証）段階。架空のSNSアプリ「Twutter」に対してエラー検出やUX指摘が可能。

---

## 3. データアーキテクチャ (Data Architecture)

収集されたデータは決して消失せず、以下の構造で蓄積されています。

- **短期記憶 (Task Inbox)**: `data/task_inbox.json` - 直近のタスクや通知。
- **長期記憶 (Universe)**: `data/universe.json` - 概念間の関係性グラフ。
- **生ログ (Raw Logs)**: `apps/MEDIA/INTELLIGENCE_HUB/data/shukatsu/` - 収集したニュースやRSSの全アーカイブ。

---

## 4. 今後のロードマップ (Next Steps)

1. **UX Agentの進化**: レポート出力機能、マルチモーダル（画像認識）対応の準備。
2. **面接対策**: 集めた企業分析データを元にした「模擬面接官」の実装。
