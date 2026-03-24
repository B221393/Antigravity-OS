# 📱 EGO Application Catalog (Full)

This catalog lists ALL applications, skills, and legacy tools within your EGO system.

## 🧠 Intelligence & Career (The "River")

| App Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **Deep Researcher** | `~/.gemini/skills/skill-deep-researcher` | Automatic corporate analysis & "Honne/Tatemae" detection. | ✅ Active |
| **ES Architect** | `apps/es_assistant` | Generates ES drafts using `IDENTITY_CORE` & Research data. | ✅ Active |
| **Interview Coach** | `~/.gemini/skills/skill-interview-coach` | Mock interviewer (HR/CTO personas) for terminal practice. | ✅ Active |
| **The River** | `apps/SYSTEM/river_flow.py` | **Automation Pipeline**. Runs Discover -> Research -> ES Gen automatically. | ✅ Active |
| **Shukatsu Map** | `apps/MEDIA/shukatsu_map` | Visual mapping of job hunting progress. | 🟢 Stable |
| **News Aggregator** | `apps/MEDIA/news_aggregator` | Customizable news feed for industry research. | 🟢 Stable |

## 🧪 UX & Development (EGO Dev)

| App Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **UX Labs** | `apps/UX_Labs` | **Universal UX Architect**. Simulates users (Grandma, Gen Z). | ✅ Active |
| **Data Hub** | `apps/SYSTEM/data_hub` | System backbone. Manages `universe.json` and syncs data. | ⚙️ System |
| **Neuron Lab** | `apps/AI_LAB` | Experimental AI scripts (Text Router, Intelligence Aggregator). | 🧪 Exp |
| **Moltbot** | `apps/moltbot` | GitHub-integrated autonomous coding agent (Legacy). | ⚠️ Legacy |

## 🎮 Games & Fun Zone

| App Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **DT Cannon** | `apps/GAMES/dt_cannon` | Action game for stress relief. | 🟢 Stable |
| **Typing Test** | `apps/GAMES/typing_test` | Measure your WPM with EGO flavor. | 🟢 Stable |
| **Knowledge Spire** | `apps/GAMES/knowledge_spire` | Tower defense for knowledge retention. | 🟢 Stable |
| **Fun Zone** | `apps/GAMES/fun_zone` | Collection of mini-games and experiments. | 🟢 Stable |

## 🎨 Creative & Media

| App Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **Intelligence Hub** | `apps/MEDIA/INTELLIGENCE_HUB` | Visual dashboard for gathered data (`dashboard.html`). | ✅ Active |
| **Bookshelf Gallery** | `apps/MEDIA/bookshelf_gallery_gui` | Visual gallery for your library. | 🟢 Stable |
| **Color Alchemy** | `apps/MEDIA/color_alchemy` | Generative color palette tool. | 🟢 Stable |
| **Stream** | `apps/MEDIA/stream` | "River" visualization and flow management. | 🟢 Stable |
| **Ascii Artist** | `apps/MEDIA/ascii_artist` | Convert images to ASCII art. | 🟢 Stable |
| **FX Soundboard** | `apps/MEDIA/fx_soundboard` | Sound effects panel for focused work. | 🟢 Stable |
| **YouTube Channel** | `apps/MEDIA/youtube_channel` | Manage and analyze YouTube content. | 🟢 Stable |

## ✍️ Workstation & Utilities

| App Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | `apps/UTILS/gemini_cli` | Terminal interface for direct LLM chat. | ✅ Active |
| **Kiwix Manager** | `apps/UTILS/kiwix_manager` | Offline Wikipedia/Knowledge base viewer. | ✅ Active |
| **Obsidian Writing** | `apps/OBSIDIAN_WRITING` | Markdown editor focused on "Zettelkasten". | 🟢 Stable |
| **Workstation** | `apps/WORKSTATION` | GUI launcher and workspace manager. | 🟢 Stable |
| **PDF Splicer** | `apps/MEDIA/pdf_splicer` | Split and merge PDF files. | 🟢 Stable |

---

## ⚙️ Automation & System Tools (2026-02 NEW)

| Tool Name | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| **統合ランチャー** | `Desktop/EGO統合ランチャー.bat` | 全機能統合メニュー（日本語UI） | ✅ Active |
| **情報収集パトロール** | `apps/MEDIA/INTELLIGENCE_HUB/shukatsu_patrol.py` | 自動情報収集＋AI分析 | ✅ Active |
| **壁紙ウォッチャー** | `bin/schedule_wallpaper_watcher.py` | スケジュール変更で壁紙自動更新 | ✅ Active |
| **スケジュール収集** | `apps/MEDIA/INTELLIGENCE_HUB/schedule_collector.py` | パトロールから締切を自動抽出 | ✅ Active |
| **スケジュールアーカイバ** | `bin/schedule_archiver.py` | 過ぎたイベントを自動アーカイブ | ✅ Active |
| **収集統計** | `bin/collection_stats.py` | 収集データのダッシュボード表示 | ✅ Active |
| **壁紙生成** | `bin/update_wallpaper.py` | スケジュール入り壁紙を生成 | ✅ Active |
| **UI分析** | `apps/MEDIA/INTELLIGENCE_HUB/ui_analyzer.py` | 採用ページのUI/UX分析＋教育問 | ✅ Active |

---

## 🚀 Recommended Workflows

### 1. The "River" Flow (Job Hunting)

```bash
python apps/SYSTEM/river_flow.py --discover
```

### 2. 全自動就活モード（NEW!）

```bash
EGO統合ランチャー.bat → [1] 全自動モード
```

パトロール → スケジュール収集 → 壁紙更新 が5分ごとにループ実行

**3. The "Deep Work" Flow**
Launch `Gemini CLI` for thought partnership + `Obsidian Writing` for notes.

**4. The "Creative" Flow**
Launch `Color Alchemy` for inspiration + `Ascii Artist` for visuals.
