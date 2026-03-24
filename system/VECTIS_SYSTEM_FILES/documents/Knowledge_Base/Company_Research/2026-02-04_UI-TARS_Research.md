# Research: UI-TARS (GUI Agent Model)

**Source**: ByteDance (Open Source)
**Type**: Vision-Language Model (VLM) for GUI Automation
**Key Features**:

- **Native GUI Agent**: Designed to see screenshots and click/type like a human.
- **End-to-End**: No need for HTML parsing; uses vision.
- **Python Integration**: `pip install ui-tars`. Outputs `pyautogui` code.
- **Models**: 2B, 7B, 72B parameters.

## Integration Potential for EGO

- **Patrol Automation**: innovative way to browse complex sites without specific API scraping.
- **System Control**: Could hypothetically control the "EGO" dashboard itself.

## Architecture

- **Perception**: "See" the screen (Button at x,y).
- **Reasoning**: "I need to click the search bar to find X".
- **Action**: `pyautogui.click(x, y)`.

**Status**: Highly Trending (2026-02). A must-watch technology for "System EGO".
