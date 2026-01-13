# Menu System Analysis & Suggestions

## Current System Overview

### Existing Commands (Normal Mode)
1. **Volume Control** - System volume adjustment and mute
2. **Voicemeeter Control** - Audio routing (if Voicemeeter installed)
3. **Media Controls** - Play/pause, next/prev track
4. **Theme Selector** - UI customization (box, accent, text colors)
5. **Window Manager** - Window operations submenu
6. **Launch Playnite** - Game launcher
7. **Game Mode** (plugin) - Toggle bottom monitors
8. **App Launcher** (plugin) - Launch Cursor, Opera GX

### Existing Menu Modes
- Media: Play/pause, track navigation
- Volume: System volume + mute
- Window: Cycle windows, snap windows, show desktop
- Voicemeeter: Mic, routing, gain control for multiple strips
- Theme: Color customization

---

## 🎯 HIGH PRIORITY ADDITIONS

### 1. **Clipboard Manager** ⭐
**Why**: Essential productivity tool, frequently requested feature
```
Mode: CLIPBOARD_HISTORY
- Rotate: Browse clipboard history (last 10-20 items)
- Press: Paste selected item
- Long-press: Clear clipboard history
```

**Implementation:**
- Use `pyperclip` or Windows clipboard API
- Store text, images, files
- Persist history between sessions
- Show preview in UI (truncated)

---

### 2. **Virtual Desktop Switcher** ⭐
**Why**: Windows 10+ has virtual desktops but awkward keyboard shortcuts
```
Mode: VIRTUAL_DESKTOPS
- Rotate: Switch between virtual desktops
- Press: Move active window to selected desktop
- Long-press: Create new desktop
```

**Implementation:**
- Use `pyvda` library or COM interface
- Show desktop thumbnails/names
- Quick desktop creation

---

### 3. **Display/Monitor Control** ⭐
**Why**: Common use case, expand on existing game mode
```
Command: Display Manager → Submenu
- Monitor Brightness (DDC/CI control)
- Display Mode (Duplicate/Extend/Second only)
- Refresh Rate Selector
- Individual Monitor Toggle
- Monitor Arrangement
```

**Implementation:**
- Use `pyautogui` for brightness (DDC/CI)
- Windows Display API for modes
- Extend existing monitor toggling

---

### 4. **Quick Launcher** ⭐
**Why**: More flexible than app launcher plugin
```
Mode: QUICK_LAUNCHER
- Rotate: Browse pinned apps/recent files
- Press: Launch selected
- Filter by category (Apps, Files, Folders, URLs)
```

**Implementation:**
- Configurable favorites list (JSON)
- Recent files from Windows registry
- Start menu integration
- Icon display in UI

---

### 5. **Audio Device Switcher**
**Why**: Switching between headphones/speakers is common
```
Mode: AUDIO_DEVICES
- Rotate: Cycle audio output devices
- Press: Set as default device
- Show current device with icon
```

**Implementation:**
- Use `pycaw` to enumerate devices
- Set default playback device
- Visual indicator of active device

---

### 6. **System Power Menu**
**Why**: Quick access to power options
```
Mode: POWER_MENU
- Rotate: Select option (Sleep/Hibernate/Restart/Shutdown/Lock)
- Press: Execute (with confirmation)
- Safety: Require double-tap for destructive actions
```

---

## 💡 MEDIUM PRIORITY ENHANCEMENTS

### 7. **Enhanced Window Management**

**Window Resize Mode:**
```
Mode: WINDOW_RESIZE
- Rotate: Cycle preset sizes (1/3, 1/2, 2/3 screen)
- Press: Apply resize
- Show preview overlay
```

**Window Position Mode:**
```
Mode: WINDOW_POSITION
- Rotate: Move window to different monitor
- Press: Confirm move
- Show monitor layout
```

**Window Transparency:**
```
Mode: WINDOW_OPACITY
- Rotate: Adjust transparency (10%-100%)
- Press: Toggle always-on-top
- Show opacity percentage
```

---

### 8. **Productivity Tools**

**Pomodoro Timer:**
```
Mode: POMODORO
- Rotate: Set duration (15/25/45 min)
- Press: Start/Pause timer
- Show progress in UI
- Notification on completion
```

**Quick Calculator:**
```
Mode: CALCULATOR
- Rotate: Adjust number
- Press: Select operation (+, -, ×, ÷)
- Show result in center
```

**Screenshot Tool:**
```
Mode: SCREENSHOT
- Rotate: Select mode (Full/Window/Region)
- Press: Capture
- Show save location
```

---

### 9. **Music/Media Integration**

**Spotify Control (if running):**
```
Mode: SPOTIFY
- Rotate: Browse playlists/tracks
- Press: Select/Play
- Show album art in UI
- Like/Unlike toggle
```

**Volume Mixer (Per-App):**
```
Mode: APP_VOLUMES
- Rotate: Select running app
- Press: Enter gain adjustment mode
- Show app icons
```

---

### 10. **Macro System**

**Macro Recording:**
```
Mode: MACRO_RECORD
- Press: Start recording
- Perform actions (hotkeys, clicks)
- Press again: Save macro
- Assign to command slot
```

**Macro Playback:**
```
Mode: MACRO_MENU
- Rotate: Select saved macro
- Press: Execute macro
- Long-press: Edit/Delete
```

---

## 🔧 UI/UX IMPROVEMENTS

### 11. **Command Favorites/Recent**
- Track most-used commands
- Quick access to recent operations
- Persistent across sessions
- Configurable favorites list

### 12. **Context-Aware Menus**
Detect active application and offer relevant commands:
- **Browser active**: Tab management, bookmark, close tabs
- **IDE active**: Build, run, debug shortcuts
- **Game active**: Auto-enable game mode
- **Media player**: Enhanced media controls

### 13. **Visual Feedback Enhancements**
- Toast notifications (not just overlay)
- Sound effects (optional)
- LED color coding for different modes
- Progress animations
- Error state visuals

### 14. **Search/Filter Mode**
```
Mode: COMMAND_SEARCH
- Type to filter commands
- Show matching results
- Quick execution
```

### 15. **Command History**
- Track executed commands
- Undo/Redo capability
- Show timestamp
- Quick re-execute

---

## 🎨 CONFIGURATION IMPROVEMENTS

### 16. **Settings/Config Mode**
```
Mode: SETTINGS_MENU
Submenus:
- LED Settings (brightness, colors, patterns)
- Timeout Settings (menu auto-hide)
- Rotation Speed (sensitivity)
- Double-tap threshold
- Theme management
- Startup behavior
```

### 17. **Profile System**
Create profiles for different scenarios:
- **Work Profile**: Office apps, productivity tools
- **Gaming Profile**: Game mode, Discord, streaming
- **Creative Profile**: Design apps, music, focus mode

Switch profiles via command or automatically based on time/app.

---

## 🔌 PLUGIN SYSTEM ENHANCEMENTS

### 18. **Plugin Hot-Reload**
- Reload plugins without restart
- Auto-detect new plugins
- Plugin enable/disable toggle
- Plugin update notifications

### 19. **Plugin Configuration UI**
- Per-plugin settings
- Visual config editor
- Import/export plugin configs
- Plugin dependencies check

### 20. **Community Plugin Repository**
- Share plugins via GitHub
- Plugin discovery/search
- One-click install
- Version management

---

## 🚀 ADVANCED FEATURES

### 21. **Network Controls**
```
Mode: NETWORK_MENU
- Toggle WiFi/Ethernet
- VPN quick connect/disconnect
- Network profile switching
- Airplane mode toggle
```

### 22. **Do Not Disturb Mode**
```
Mode: DND_MODE
- Toggle notifications
- Mute microphone
- Set status (Busy/Away/etc)
- Schedule DND periods
```

### 23. **File Operations**
```
Mode: FILE_MANAGER
- Recent files browser
- Quick file actions (copy path, open location)
- File search
- Favorite folders
```

### 24. **API Integrations**
- **Home Assistant**: Smart home control
- **IFTTT**: Webhook triggers
- **Discord**: Status updates, voice controls
- **Notion**: Quick notes
- **Todoist**: Task creation

---

## 🏗️ ARCHITECTURAL IMPROVEMENTS

### 25. **Command Pipeline System**
Allow chaining commands:
```
Example: "Launch game" → "Enable game mode" → "Mute mic" → "Set DND"
```

### 26. **Conditional Commands**
Commands that execute based on conditions:
```
IF (Time > 10PM) THEN (Enable night theme + Reduce volume)
IF (On Battery) THEN (Reduce brightness + Enable power saver)
```

### 27. **Custom Scripting**
Allow Python scripts as commands:
```python
# custom_commands/morning_routine.py
def execute():
    set_brightness(100)
    launch_apps(['Outlook', 'Slack', 'Chrome'])
    set_voicemeeter_routing('work_profile')
```

### 28. **Web Dashboard**
- Configure commands via browser
- Monitor keyboard status
- View usage statistics
- Remote control (optional)

---

## 📊 IMPLEMENTATION PRIORITY

### Phase 1 (Quick Wins - 1-2 days)
1. Virtual Desktop Switcher
2. Audio Device Switcher
3. Power Menu
4. Enhanced Window Positioning (multi-monitor)

### Phase 2 (High Value - 3-5 days)
5. Clipboard Manager
6. Display/Monitor Control
7. Quick Launcher with favorites
8. Context-aware menus

### Phase 3 (Polish - 1 week)
9. Macro System
10. Settings/Config Mode
11. Profile System
12. Plugin hot-reload

### Phase 4 (Advanced - 2+ weeks)
13. Spotify/Music integration
14. Per-app volume mixer
15. Command pipelines
16. Web dashboard

---

## 🎯 SPECIFIC IMPLEMENTATION EXAMPLES

### Example: Virtual Desktop Switcher

**Plugin file: `python_host/plugins/virtual_desktops.py`**

```python
import pyvda  # pip install pyvda

def switch_desktop_next():
    current = pyvda.get_current_desktop()
    all_desktops = pyvda.get_virtual_desktops()
    next_idx = (all_desktops.index(current) + 1) % len(all_desktops)
    pyvda.VirtualDesktop(all_desktops[next_idx]).go()

def get_commands():
    return [{
        "name": "Virtual Desktops",
        "description": "Switch between virtual desktops",
        "callback": lambda: state_machine.enter_mode(MenuMode.VIRTUAL_DESKTOP)
    }]

def get_mode_handlers(state_machine):
    return {
        MenuMode.VIRTUAL_DESKTOP: VirtualDesktopHandler(state_machine)
    }
```

### Example: Clipboard Manager

```python
import pyperclip
import json

class ClipboardManager:
    def __init__(self, max_items=20):
        self.history = []
        self.max_items = max_items
        self.load_history()

    def add(self, text):
        if text and text not in self.history:
            self.history.insert(0, text)
            self.history = self.history[:self.max_items]
            self.save_history()

    def get_history(self):
        return self.history

    def paste(self, index):
        if 0 <= index < len(self.history):
            pyperclip.copy(self.history[index])
            # Simulate Ctrl+V
            keyboard.send_keys('{CTRL}v')
```

---

## 💭 CLOSING THOUGHTS

### Most Impactful Changes:
1. **Virtual Desktop Switcher** - Solves a common Windows pain point
2. **Clipboard Manager** - Essential productivity boost
3. **Audio Device Switcher** - Simple but highly useful
4. **Context-Aware Menus** - Makes the system feel intelligent
5. **Profile System** - Adapts to different workflows

### Best Quick Wins:
- Audio device switcher (minimal code)
- Power menu (straightforward)
- Enhanced window positioning (extend existing)
- Favorites/recent commands (simple state tracking)

### Future-Proofing:
- Plugin system is already extensible ✅
- State machine architecture is solid ✅
- UI supports dynamic content ✅
- Just need more handler implementations
