# Keychron V1 Command Reference

## Normal Mode Commands

Rotate the knob to cycle through commands, press to execute:

### Command 0: Media Controls 🎵
**Execute:** Enters Media Control menu
- **Rotate Clockwise:** Next track ⏭
- **Rotate Counter-Clockwise:** Previous track ⏮
- **Single Tap:** Play/Pause ⏯
- **Double Tap:** Exit menu
- **Auto-exit:** 5 seconds of inactivity

### Command 1: Launch Cursor
**Execute:** Opens Cursor IDE

### Command 2: Window Manager 🪟
**Execute:** Enters Window submenu selector

**Submenu Selection Mode:**
- **Rotate:** Cycle through submenus (Window Cycle, Window Snap, Show Desktop)
- **Single Tap:** Enter selected submenu
- **Double Tap:** Exit to main menu
- **Visual Display:** Shows previous/current/next submenu options around cursor

**Window Cycle Submenu (Alt-Tab like):**
- **Rotate Clockwise:** Next window in list
- **Rotate Counter-Clockwise:** Previous window in list
- **Single Tap:** Switch to selected window and exit
- **Double Tap:** Exit back to Window Menu
- **Display:** Shows window titles around cursor (previous/current/next)
- **Note:** Builds list of visible windows on entry, excludes minimized windows

**Window Snap Submenu:**
- **Rotate:** Cycle through snap positions (Snap Left ◧, Snap Right ◨, Maximize ⬜)
- **Single Tap:** Snap active window to selected position
- **Double Tap:** Exit back to Window Menu

**Show Desktop (Direct Action):**
- Immediately shows desktop (Win+D)

### Command 3: Volume Control 🔊
**Execute:** Enters Volume Control menu
- **Rotate Clockwise:** Increase volume
- **Rotate Counter-Clockwise:** Decrease volume
- **Single Tap:** Toggle mute 🔇/🔊
- **Double Tap:** Exit menu
- **Auto-exit:** 5 seconds of inactivity
- **Display:** Shows live volume % and mute status

---

## How It Works

### Firmware (Keychron V1)
- Encoder rotation sends: `Ctrl+Alt+F13`, `F14`, `F15`, `F16`
- Encoder press sends: `Ctrl+Alt+Enter`
- No PC software needed - works on any PC with the AutoHotkey script

### AutoHotkey Script
- Maps firmware hotkeys to OS commands
- Manages menu modes with rotation/tap/double-tap interactions
- Auto-exits menus after 5 seconds of inactivity
- System tray shows current mode

### Installation
1. **Keyboard:** Flash `firmware/keychron_v1_ansi_knob.bin` via QMK Toolbox
2. **PC:** Install AutoHotkey v2, run `scripts/keychron_commands.ahk`

---

## Customization

### Adding New Commands

Edit `commands` array in `scripts/keychron_commands.ahk`:

```autohotkey
commands := [
    {
        name: "Your Command Name",
        action: () => Run("your-app.exe")
    },
    // ... 3 more commands
]
```

### Adding Submenus

The system now supports nested submenu structures. Example:

```autohotkey
; Define submenu array
yourSubmenus := [
    {
        name: "Submenu Option 1",
        action: () => YourSubmenu1Function()
    },
    {
        name: "Submenu Option 2",
        action: () => YourSubmenu2Function()
    }
]

; Add main menu entry
commands := [
    {
        name: "Your Menu",
        action: () => EnterYourMenuMode()
    }
]
```

### Creating Menu Modes

Add new menu modes by implementing:

1. **EnterYourMode()** function - Sets `menuMode` and shows display
2. **HandleMenuRotation()** handler - Add your mode's rotation logic
3. **HandleMenuSingleClick()** handler - Add your mode's tap action
4. **ShowMenuDisplay()** display - Add visual tooltip layout
5. **UpdateTrayMenu()** status - Add tray icon display text

### Submenu Architecture

The system supports:
- **Direct menus** (Volume, Media) - Immediate actions on rotate/tap
- **Submenu selectors** (Window Manager) - Rotate to choose submenu, tap to enter
- **Cycling menus** (Window Cycle) - Rotate through items, tap to select
- **Multi-level nesting** - Submenus can launch other submenus
