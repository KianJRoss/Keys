# Keychron V1 Python Menu System

Python implementation of the AutoHotkey menu system from `keychron_commands.ahk`.

## Features

**4 Main Commands** (rotate encoder to select, press to execute):
1. **Volume Control** - Adjust system volume and mute
2. **Media Controls** - Play/pause, next/prev track
3. **Window Manager** - Cycle through windows and snap to screen edges
4. **Launch Playnite** - Open Playnite in fullscreen mode

**Menu System:**
- Rotate encoder to navigate options
- Press to execute/select
- Double-tap to exit menu mode
- Auto-exit after 5 seconds of inactivity
- Visual overlay UI showing current options

**Implemented Menus:**
- Media Mode: Play/pause, next/prev track
- Window Cycle: Alt-Tab like window switching
- Window Snap: Snap left/right/maximize

## Architecture

```
keychron_app.py       - Main application entry point
├── hid_test.py           - Raw HID communication (reused)
├── menu_system.py        - State machine and command registry
├── mode_handlers.py      - Menu mode implementations
├── windows_api.py        - Windows API integrations
└── overlay_ui.py         - Tkinter-based overlay UI
```

### Key Components

**menu_system.py:**
- `MenuStateMachine` - Core state machine
- `CommandRegistry` - Extensible command system
- `ModeHandler` - Base class for menu modes
- State tracking (current command, menu mode, submenu index)

**windows_api.py:**
- `VolumeControl` - pycaw-based volume control
- `MediaControl` - Windows media key simulation
- `WindowManager` - Window enumeration and management
- `SystemAPI` - Unified facade

**mode_handlers.py:**
- `MediaModeHandler` - Media control implementation
- `WindowMenuHandler` - Window submenu selector
- `WindowCycleHandler` - Alt-Tab like switching
- `WindowSnapHandler` - Window snapping

**overlay_ui.py:**
- `OverlayUI` - Tkinter overlay windows
- `UIManager` - Thread-safe UI wrapper
- Wheel layout around cursor (like AHK)

## Installation

```bash
cd C:\Repos\Keyboard\python_host

# Install dependencies
pip install -r requirements.txt

# Test Windows APIs
python windows_api.py
```

**Requirements:**
- Python 3.8+
- hidapi (Raw HID communication)
- pycaw (Windows volume control)
- pywin32 (Windows APIs)
- comtypes (COM interface)
- tkinter (built-in)

## Usage

```bash
# Run the application
python keychron_app.py
```

**Controls:**
- **Rotate encoder**: Select command (0-3) in normal mode, or navigate menu options
- **Press encoder**: Execute command / select menu item
- **Double-tap**: Exit menu mode

## How It Works

### Normal Mode (Command Selection)

```
Rotate: 0 → 1 → 2 → 3 → 0 (wraps)
  0: Volume Control
  1: Media Controls
  2: Window Manager
  3: Launch Playnite

Press: Execute selected command
```

### Menu Mode (After Executing a Command)

**Media Controls:**
```
Rotate CW: Next track
Rotate CCW: Previous track
Press: Play/Pause
Double-tap: Exit
```

**Window Manager → Window Cycle:**
```
Rotate: Cycle through open windows
Press: Switch to selected window
Double-tap: Exit
```

**Window Manager → Window Snap:**
```
Rotate: Select snap position (left/right/maximize)
Press: Snap window and exit
Double-tap: Exit
```

## Encoder Event Flow

```
Firmware (C)
  ↓ Raw HID packets
keychron_app.py → _handle_encoder_event()
  ↓
MenuStateMachine → handle_rotation() / handle_press() / handle_double_tap()
  ↓
ModeHandler → on_rotation() / on_press()
  ↓
WindowsAPI / UIManager
```

## Rotation Direction Detection

The firmware sends **command indices (0-3)** on rotation. The Python code determines direction by tracking the sequence:

```python
# CW: 0→1, 1→2, 2→3, 3→0
# CCW: 0→3, 3→2, 2→1, 1→0

is_clockwise = (curr == prev + 1) or (prev == 3 and curr == 0)
```

## Extending the System

### Add a New Command

```python
# In keychron_app.py setup()
state_machine.commands.register(
    "My Command",
    "Description",
    my_command_function
)
```

### Add a New Menu Mode

1. Add enum to `MenuMode` in `menu_system.py`
2. Create handler class in `mode_handlers.py`:

```python
class MyModeHandler(ModeHandler):
    def on_enter(self, state): pass
    def on_exit(self, state): pass
    def on_rotation(self, state, clockwise): pass
    def on_press(self, state): pass
    def get_display_text(self, state): return {...}
```

3. Register in `create_handlers()` in `mode_handlers.py`

## Comparison: AutoHotkey vs Python

| Feature | AutoHotkey | Python |
|---------|------------|--------|
| **Hotkey Approach** | Ctrl+Alt+F13-F16 | Raw HID events |
| **Communication** | Keyboard shortcuts | Bidirectional HID |
| **Voicemeeter** | Full integration ✓ | Not yet implemented |
| **Volume Control** | System calls ✓ | pycaw ✓ |
| **Media Keys** | Send command ✓ | win32api ✓ |
| **Window Management** | Win32 API ✓ | win32gui ✓ |
| **UI Overlay** | GUI objects ✓ | tkinter ✓ |
| **State Machine** | Global vars | Clean OOP ✓ |
| **Extensibility** | Edit arrays | Plugin system ✓ |

## Future Enhancements

**Not Yet Implemented:**
- [ ] Voicemeeter integration (DLL API)
- [ ] Volume mode as standalone (currently in commands)
- [ ] Configurable key mappings
- [ ] Settings file (JSON/YAML)
- [ ] System tray icon
- [ ] LED feedback refinement
- [ ] Long-press alternative actions

**Planned:**
- [ ] Custom command plugins
- [ ] Profile switching
- [ ] Macro recording
- [ ] Multi-monitor support
- [ ] Keyboard shortcuts overlay

## Troubleshooting

**"Raw HID interface not found"**
- Make sure you flashed the Raw HID firmware (not the hotkey firmware)
- Check `list_devices.py` output for Keychron devices

**"Volume control not available"**
- Install pycaw: `pip install pycaw comtypes`
- Check Windows Audio service is running

**"Window management not available"**
- Install pywin32: `pip install pywin32`
- Run `python -m pywin32_postinstall -install` if needed

**UI doesn't appear**
- Make sure tkinter is available (built-in with Python)
- Check if overlay windows are being created (transparent, might be hard to see)

**Encoder events not working**
- Verify HID connection with `hid_test.py` first
- Check firmware is sending Raw HID packets
- Look for console output showing events

## Development Notes

**Threading:**
- HID reader runs in separate thread (blocking reads)
- Timeout checker runs in separate thread (menu auto-exit)
- UI runs in main thread (tkinter requirement)
- All UI updates use `root.after()` for thread safety

**State Management:**
- Single `AppState` dataclass holds all state
- State machine is the single source of truth
- Handlers receive state, don't own it

**Event Processing:**
- Firmware sends indices (0-3), not raw CW/CCW
- Python determines direction from sequence
- Supports wrap-around (3→0 is CW, 0→3 is CCW)

## Files

| File | Purpose | Lines |
|------|---------|-------|
| keychron_app.py | Main application | ~350 |
| menu_system.py | State machine core | ~350 |
| mode_handlers.py | Menu implementations | ~250 |
| windows_api.py | System APIs | ~300 |
| overlay_ui.py | UI overlay | ~250 |
| hid_test.py | HID communication (reused) | ~350 |
| **Total** | | **~1850** |

## License

Same as parent project.

## Credits

Based on `keychron_commands.ahk` AutoHotkey v2 implementation.
