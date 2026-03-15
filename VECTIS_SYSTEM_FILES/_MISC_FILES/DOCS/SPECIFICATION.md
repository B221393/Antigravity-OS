# VECTIS OS Specification

**Version**: 2.0 (Deep Link Update)
**Author**: Antigravity (Google Deepmind)
**Last Updated**: 2026-01-08

---

## 🏗️ System Architecture

VECTIS OS is a modular, agentic Operating System built on Python (Streamlit) and Batch scripts, designed to augment the user's intelligence and productivity.

### 📂 Directory Structure (User Facing)

- **`🚀 LAUNCH_VECTIS_HUB.bat`**: Main entry point. Starts the streamlined Hub dashboard.
- **`AUTO_YOUTUBE/`**: Automatic YouTube summarization tool.
  - `AUTO_YOUTUBE.txt`: Input file for URLs.
  - `RUN_WATCHER.bat`: Background service for summarization.
  - `COPY_TO_OBSIDIAN.bat`: Sync tool for Obsidian.
- **`apps/`**: Application modules.
  - `dashboard`: The central station (Launcher).
  - `job_hq`: Job hunting management & self-analysis.
  - `memory_bank`: Chat archiver & "Second Brain".
  - `youtube_channel`: YouTube digest app.
  - `book_log`: Reading log & knowledge extractor.
  - `diary`: Daily journaling.
- **`obsidian_vault/`**: Local Markdown knowledge base.
- **`_SYSTEM/`**: Behind-the-scenes scripts & assets.

---

## 📱 Application Modules

### 1. 🎖️ Job HQ (Port 8517)

- **Goal**: Manage job applications and self-analysis.
- **Features**:
  - **Skill Matrix**: Visual radar/bar chart of user skills.
  - **Company Kanban**: Manage application status (Applied, Interview, Offer).
  - **Weakness Analysis**: AI coach analyzes skill gaps.
  - **K-Card Integration**: Imports knowledge cards from other apps.

### 2. 🧠 Memory Bank (Port 8518)

- **Goal**: Archive conversational intelligence with AI (Gemini).
- **Features**:
  - **Import**: Save chat logs from Gemini.
  - **Integration**: Feeds into Persona Engine for ES generation.
  - **3D View**: (Conceptual) Visualizing memory nodes.

### 3. 📺 Channel Digest (Port 8519) + Auto Watcher

- **Goal**: Extract knowledge from videos efficiently.
- **Features**:
  - **Auto Summarization**: Paste URL -> Get Markdown summary.
  - **Channel Batch**: Summarize ALL videos in a channel.
  - **Obsidian Sync**: Export summaries to local knowledge base.

### 4. 📚 Book Insight (Port 8520)

- **Goal**: Turn reading into actionable knowledge.
- **Features**:
  - **Search**: Google Books API integration.
  - **Crystallization**: Convert notes into Knowledge Cards.

---

## 🔄 Data Flow & Deep Links

1. **YouTube -> Memory/Obsidian**
   - Video summaries are saved as Markdown in `apps/memory/data` and synced to `obsidian_vault`.

2. **Book/YouTube -> Job HQ**
   - Notes are converted to **Knowledge Cards (.kcard)**.
   - Job HQ scans these cards to generate "Self-PR" and "Strengths".

3. **Diary/Memory -> Persona Engine**
   - Diary entries and Chat logs train the AI Persona to write ES in the user's style.

---

## 🛠️ Usage Guide

### YouTube Auto Summarizer

1. Run `AUTO_YOUTUBE/RUN_WATCHER.bat`.
2. Open `AUTO_YOUTUBE/AUTO_YOUTUBE.txt`.
3. Paste a video URL or Channel URL (e.g., `https://youtube.com/@user`).
4. Save. The watcher will process all videos and save MD files.
5. (Optional) Run `COPY_TO_OBSIDIAN.bat` to sync with your Obsidian vault.

### VECTIS Hub

1. Run `🚀 LAUNCH_VECTIS_HUB.bat`.
2. Use the sidebar to navigate between apps.

---

## ⚠️ Notes for Developers

- **Environment**: Requires `.env` with `GEMINI_API_KEY`.
- **Dependencies**: `streamlit`, `google-generativeai`, `youtube-transcript-api`, `scrapetube`.
- **System Folder**: Do not touch `_SYSTEM` unless updating core logic.
