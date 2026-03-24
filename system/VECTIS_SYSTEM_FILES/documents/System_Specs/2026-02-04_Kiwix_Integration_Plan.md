# Kiwix <-> EGO Integration Protocol

**Status**: Planning / Ready for Binary

The goal is to seamlessly integrate **Kiwix** (Offline Wikipedia/Knowledge) into the **EGO Dashboard**.
Since Kiwix provides `kiwix-serve.exe`, we can treat it as a local micro-service controlled by EGO.

## 1. Installation Requirements (User Action Needed)

To enable the "Knowledge Engine", the user must download the **Kiwix Tools** (Command Line):

1. Download `kiwix-tools_windows-x86_64.zip` from [kiwix.org](https://www.kiwix.org/en/download/).
2. Extract contents to:
    `c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\MEDIA\kiwix\bin\`
    *(Ensure `kiwix-serve.exe` is at this path)*
3. Place ZIM files (e.g., `wikipedia_ja_all_max...zim`) in:
    `c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\MEDIA\kiwix\library\`

## 2. EGO System Integration

We will create a control script (`manage_server.py`) to:

- **Start Server**: Launch `kiwix-serve` on Port 9000.
- **Stop Server**: Kill the process.
- **Search**: (Optional) Interface with the API.

## 3. UI Updates (Dashboard)

- Add "Knowledge Base" widget to **Lab** or **Library** tab.
- "Start Offline Wiki" button.
- Iframe embedding `http://localhost:9000`.

## 4. "Current State" of Kiwix (Research)

- **Version**: Active (v3.x).
- **Features**: Direct HTTP Server, powerful full-text search.
- **Fit for EGO**: Perfect match for the "Offline Standalone" philosophy.
