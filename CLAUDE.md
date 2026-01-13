# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Custom Keychron V1 ANSI Encoder keyboard firmware and Python host software. The system uses the rotary encoder knob to cycle through commands (Volume, Media, Window Management, etc.) and execute them via a hierarchical menu system. The firmware sends hotkeys to the Python host application, which provides OS-level integration via Windows APIs.

## Architecture

### Two-Component System

**1. QMK Firmware (C)** - `firmware/`
- Runs on the Keychron V1 keyboard
- Encoder rotation: cycles through commands (0-3), sends `Ctrl+Alt+F13-F16` hotkeys
- Encoder press: sends `Ctrl+Alt+Enter` to execute current command
- Supports VIA for keymap customization
- Path: `firmware/keymap.c` and `firmware/rules.mk`

**2. Python Host Application** - `python_host/`
- Listens for Raw HID events from keyboard
- Provides overlay UI (Tkinter-based, enhanced themes available)
- Integrates with Windows APIs: volume control (pycaw), window management (pywin32), media controls, Voicemeeter audio routing
- Extensible plugin system for custom commands
- System tray icon for background operation

### Communication Flow

```
Keyboard Encoder Rotate → Firmware sends Ctrl+Alt+F13-F16 → Python receives HID event → State Machine updates UI
Keyboard Encoder Press → Firmware sends Ctrl+Alt+Enter → Python executes current command → Mode Handler processes
```

### State Machine (`python_host/menu_system.py`)

Central component managing:
- **Normal Mode**: Command selection (rotate to select, press to execute)
- **Menu Modes**: Active menu contexts (Volume, Media, Window Cycle, etc.)
- Mode handlers registered dynamically via `register_mode_handler()`
- UI callbacks for overlay updates
- Timeout handling (auto-exit menus after inactivity)

### Mode Handlers (`python_host/mode_handlers.py`)

Implement specific menu behaviors:
- `MediaModeHandler`: Play/pause, next/prev track
- `WindowCycleHandler`: Alt-Tab style window switching
- `WindowSnapHandler`: Snap windows to screen edges
- `VoicemeeterModeHandler`: Audio routing control
- `ThemeMenuHandler`: UI theme selection

Each handler extends `ModeHandler` base class with `on_enter()`, `on_exit()`, `on_rotation()`, `on_press()`, `get_display_text()` methods.

### Plugin System

Plugins live in `python_host/plugins/` and auto-load at startup. Example: `game_mode.py` (toggle monitors), `app_launcher.py` (launch applications).

**Plugin Interface:**
```python
def get_commands():
    return [{"name": "Command Name", "description": "...", "callback": function}]

def get_mode_handlers(state_machine):
    return {MenuMode.CUSTOM: CustomHandler()}
```

## Common Development Commands

### Firmware Development

**Build firmware:**
```bash
# Option 1: Automated script (recommended)
setup_qmk.bat
# Choose Option 2 (Compile Only) if dependencies already installed

# Option 2: Manual QMK build
cd C:\CLIPALS\qmk_firmware
qmk compile -kb keychron/v1/ansi_encoder -km macro
```

**Flash firmware:**
1. Use QMK Toolbox: Load `.bin` file from `qmk_firmware\.build\`
2. Enter bootloader mode: Unplug keyboard, hold ESC, plug in, release ESC
3. Click "Flash" in QMK Toolbox

**Firmware files:**
- `firmware/keymap.c` - Main keymap and encoder logic
- `firmware/rules.mk` - Build configuration (enables VIA, encoder, etc.)

### Python Host Development

**Install dependencies:**
```bash
cd python_host
pip install -r requirements.txt
```

**Run application:**
```bash
python keychron_app.py

# With options:
python keychron_app.py --theme DARK    # DARK, LIGHT, CYBER
python keychron_app.py --classic-ui    # Use basic UI
python keychron_app.py --test-ui       # Test UI without keyboard
```

**Configuration:**
Edit `python_host/config.json` to adjust:
- HID device IDs (vendor_id, product_id, usage_page)
- UI theme and enhanced UI toggle
- LED feedback settings
- Reconnection behavior

**Create a plugin:**
1. Create `python_host/plugins/my_plugin.py`
2. Implement `get_commands()` returning list of command dicts
3. Optionally implement `get_mode_handlers()` for custom menu modes
4. Auto-loads on next startup

**Run tests/diagnostics:**
```bash
# List HID devices
python list_devices.py

# Test HID communication
python hid_test.py

# Test Windows APIs
python windows_api.py
```

### Logging

Logs written to `python_host/logs/keychron_app.log` (works with both `python.exe` and `pythonw.exe`).

## Code Structure

### Firmware Layout
- `firmware/keymap.c` - 138 lines, contains encoder logic and keymap layers
- NUM_COMMANDS defines command count (default: 4, must match Python command registry size)
- `encoder_update_user()` handles rotation, sends F13-F16 hotkeys
- `process_record_user()` handles CMD_EXEC (knob press)

### Python Host Layout
- `keychron_app.py` - Main application entry point, HID communication, plugin loading (~606 lines)
- `menu_system.py` - State machine, command registry, menu timeout logic (~350 lines)
- `mode_handlers.py` - Built-in mode handlers (~450 lines)
- `windows_api.py` - Windows API wrappers (volume, media, window management) (~300 lines)
- `overlay_ui.py` - Basic Tkinter overlay (~250 lines)
- `overlay_enhanced.py` - Enhanced overlay with themes, icons, progress bars (~400 lines)
- `voicemeeter_api.py` - Voicemeeter Potato DLL integration (~200 lines)
- `led_feedback.py` - Keyboard LED control via Raw HID (~150 lines)
- `tray_icon.py` - System tray icon (pystray) (~100 lines)

### Key Files
- `config.json` - Runtime configuration (HID IDs, UI settings)
- `themes.json` - UI theme definitions (colors, fonts, styling)
- `requirements.txt` - Python dependencies
- `context_aware.py` - Context detection system for app-specific commands

### Plugin Files
- `plugins/virtual_desktops.py` - Windows virtual desktop navigation
- `plugins/display_control.py` - Monitor brightness, modes, and toggling
- `plugins/context_commands.py` - App-specific shortcut menu
- `plugins/game_mode.py` - Toggle bottom two monitors
- `plugins/app_launcher.py` - Launch applications

## Important Implementation Details

### HID Protocol (firmware ↔ Python)

**Outgoing (Firmware → Python):**
```c
packet[0] = 0xFD;  // Event marker
packet[1] = event_type;  // 0x01=CW, 0x02=CCW, 0x03=Press, 0x04=Release, 0x05=Long, 0x06=Double
packet[2] = encoder_id;  // Always 0 (single encoder)
packet[3] = value;       // Context-dependent
```

**Incoming (Python → Firmware):**
LED control packets use same structure (implementation in `led_feedback.py`).

### Command Registration

Commands dynamically registered in `keychron_app._register_commands()`. Command count must match firmware's NUM_COMMANDS or encoder wrapping will desync.

### Mode Handler Lifecycle

1. User presses encoder → `state_machine.handle_press()` calls current command callback
2. Command callback calls `state_machine.enter_mode(MenuMode.X)`
3. State machine calls `handler.on_enter(state)`
4. Subsequent rotations → `handler.on_rotation(state, clockwise)`
5. Subsequent presses → `handler.on_press(state)`
6. Exit via `state_machine.exit_menu_mode()` → `handler.on_exit(state)`
7. UI updates triggered via `state_machine._ui_callback()` with display dict

### UI Display Format

Handlers return display dict to UI:
```python
{
    'title': 'Menu Title',
    'center': 'Center Text',
    'left': 'Left Option',
    'right': 'Right Option',
    'icons': {'center': '🔊', 'left': '−', 'right': '+'},  # Enhanced UI only
    'progress': 0.5,  # 0.0-1.0, Enhanced UI only
    'set_theme': 'DARK',  # Change theme
}
```

### Threading Model

- **HID Reader Thread** (daemon): Blocking reads with 100ms timeout, pushes events to state machine
- **Timeout Checker Thread** (daemon): Polls menu timeout every 500ms
- **Main Thread**: Runs Tkinter UI event loop (must be main thread on Windows)
- **UI Updates**: All UI calls use `root.after()` for thread safety

### Voicemeeter Integration

Optional integration with Voicemeeter Potato (audio routing software). Loads `VoicemeeterRemote64.dll` via ctypes. If unavailable, falls back to system volume control.

## Common Issues

**Encoder rotation not cycling commands:**
- Check NUM_COMMANDS in `firmware/keymap.c` matches Python command count
- Verify HID connection with `python_host/hid_test.py`

**UI not showing:**
- Enhanced UI requires specific Tkinter features (transparency, topmost windows)
- Use `--classic-ui` flag for fallback
- Check `themes.json` is present

**Voicemeeter not detected:**
- Voicemeeter Potato must be running
- DLL path: `C:\Program Files (x86)\VB\Voicemeeter\VoicemeeterRemote64.dll`
- Falls back to system volume if unavailable

**HID device not found:**
- Verify `vendor_id` (0x3434), `product_id` (0x0311), `usage_page` (0xFF60) in `config.json`
- Check Device Manager for "HID-compliant device" under keyboard
- Run `python_host/list_devices.py` to enumerate all HID devices

**Firmware changes not reflected:**
- Ensure you flashed the new `.bin` file
- Check QMK Toolbox shows "Flash complete"
- Try unplugging/replugging keyboard after flash

## New Features (Recently Added)

### Virtual Desktop Switcher
Navigate Windows 10/11 virtual desktops with the encoder:
- Rotate: Switch between desktops
- Press: Show action menu (move window, new desktop, close desktop)
- Uses Windows shortcuts (Win+Ctrl+Arrow keys)

### Display Control
Enhanced monitor management:
- Brightness control (±5% steps)
- Display mode switching (PC only, Duplicate, Extend, Second only)
- Individual monitor toggle
- Progress bar for brightness
- Expands on existing game_mode.py

### Context-Aware Commands
Automatically detects active application and shows relevant shortcuts:
- **Browsers** (Chrome, Firefox, Edge): Tab management (new, close, reopen, next/prev)
- **Code Editors** (VS Code, Cursor, PyCharm): Comment, format, find, run/debug
- **Discord**: Mute/deafen toggles
- Extensible: Add new `ContextProvider` classes in `context_aware.py`
- Rate-limited detection (500ms) to minimize performance impact

## Development Workflow

**Adding a new command:**
1. Create callback function in `keychron_app.py` or plugin
2. Register in `_register_commands()` or plugin's `get_commands()`
3. If command needs menu mode: Create handler in `mode_handlers.py`, register with state machine
4. Update firmware NUM_COMMANDS if exceeding 4 commands

**Modifying firmware:**
1. Edit `firmware/keymap.c` or `firmware/rules.mk`
2. Run `setup_qmk.bat` → Option 2 (or `qmk compile` directly)
3. Flash with QMK Toolbox
4. Test encoder behavior with `python_host/hid_test.py`

**Debugging HID communication:**
1. Run `python_host/hid_test.py` to see raw events
2. Check logs in `python_host/logs/keychron_app.log`
3. Verify LED feedback to confirm firmware is sending events

**UI theme customization:**
Edit `python_host/themes.json` - defines colors, fonts, sizes for DARK, LIGHT, CYBER themes.
