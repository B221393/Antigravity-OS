# EGO NEXUS UI Specification (v2.0)

## 1. Overview

**EGO NEXUS** is a Text User Interface (TUI) command center designed for the EGO productivity system. It serves as the primary launcher for applications, automation scripts, and games. It is built using Python's `Textual` framework to provide a responsive, keyboard-friendly, and visually immersive experience within the terminal.

## 2. Design Philosophy

- **Aesthetic**: "Professional Cyberpunk" (Modernized Hacker Terminal).
- **Palette**: Dark Grey backgrounds (#1e1e1e) with sharp White text and Professional Blue accents (#007acc).
- **Experience**: Fast, keyboard-centric, and "always-on" monitoring.

## 3. Layout Structure

The screen is divided horizontally into two main panels:

### 3.1. Left Panel (Launcher)

- **Width**: 35%
- **Background**: `#1e1e1e` (Dark Grey)
- **Border**: Heavy Line in `#4d4d4d`
- **Components**:
  - **Header Art**: ASCII Art logic of "EGO" in Green/Cyan (#00cc66).
  - **Command Categories**: Buttons organized by function (Intelligence, Dev, Games, Media).
  - **Buttons**: Custom `LauncherButton` widgets that execute shell commands on click.

### 3.2. Right Panel (Monitor)

- **Width**: 65%
- **Layout**: Vertical Split
- **Components**:
    1. **System Vitals (Top 20%)**:
        - Displays real-time system status (Time, User, Core Status).
        - Background: `#252526` (Slightly lighter grey).
    2. **Operational Log (Bottom 80%)**:
        - A rolling log of all actions taken within the Nexus.
        - Displays execution confirmations, error messages, and system alerts.

## 4. Color Palette

| Component | Hex Code | Visual Role |
| :--- | :--- | :--- |
| **Global Background** | `#0d0d0d` | Deep Black/Grey for depth |
| **Panel Background** | `#1e1e1e` | Standard VS Code-like Dark Grey |
| **Primary Text** | `#ffffff` | High readability |
| **Accent / Button** | `#007acc` | "Professional Blue" for interaction |
| **Success / Header** | `#00cc66` | Verification logic green |
| **Borders** | `#4d4d4d` | Subtle separation |

## 5. Component Specifications

### Custom Widget: `LauncherButton`

Wrapper around the standard Button widget to safely store and execute shell commands.

```python
class LauncherButton(Button):
    def __init__(self, name, command, description):
        self.command_line = command  # Stores the raw shell string
        self.tooltip = description   # Hover text
```

### State Management

- **Reactive Status**: The status box updates via `update_status()` method.
- **Logging**: All events flow through `log_write()`, ensuring a persistent record of the session.

## 6. Interaction Model

- **Mouse**: Full click support for all buttons.
- **Keyboard**: Tab navigation supported between buttons.
- **Execution**: Clicking a button triggers `subprocess.Popen(f'start cmd /k "{command}"')`.
  - *Logic*: Opens a new visible terminal window for the tool so the user can verify output and interact with it (unlike a silent background process).
