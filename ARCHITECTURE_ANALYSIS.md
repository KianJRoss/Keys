# AutoHotkey vs Firmware: Architecture Decision

## Current System Analysis

**What Works Well:**
- Encoder macros via AHK (menus, submenus, click detection)
- OS-level integrations (volume, window management, media controls)
- Easy to modify and iterate
- Rich display feedback (tooltips)

**Limitations:**
- Only 4 main commands accessible via encoder
- Rest of keyboard unused for macros
- No sublayer/modifier system

---

## Option 1: Enhanced AutoHotkey Layer System ⭐ RECOMMENDED

### Architecture: Encoder Knob as Layer Key

**Concept:** Hold encoder knob = activate function layer for entire keyboard

```
NORMAL MODE:
- F1-F12: Standard function keys
- PgUp/PgDn/Home/End: Standard navigation
- Number row: Numbers
- Encoder rotate: Cycle commands
- Encoder tap: Execute command

HOLD ENCODER (Function Layer):
- F1-F12: Macro slots (launch apps, scripts, snippets)
- PgUp/PgDn: Brightness up/down
- Home/End: Volume up/down
- Number row: Quick launch apps 1-9
- Arrow keys: Window snapping (←/→ = snap, ↑ = max, ↓ = min)
- Space: Screenshot
- Enter: Toggle microphone mute
- Etc.
```

### Pros:
✅ Entire keyboard becomes programmable
✅ Keep existing encoder menu system
✅ Easy to customize (just edit AHK script)
✅ Can use OS APIs (window management, clipboard, etc.)
✅ Quick iteration - no firmware flashing
✅ Context-aware (can change based on active app)
✅ Visual feedback possible (notifications, tooltips)

### Cons:
❌ Requires AHK running on each PC
❌ Won't work in BIOS/pre-Windows environments
❌ Slightly higher latency than firmware (negligible for most uses)

---

## Option 2: Firmware QMK Layers

### Architecture: Use QMK's built-in layer system

**QMK has layers (MO(1) switches to layer 1 while held)**

```c
// Layer 0: Normal
[0] = LAYOUT(...normal keys...)

// Layer 1: Function (accessed via MO(1) or encoder hold)
[1] = LAYOUT(
    F1 = LAUNCH_APP_1,
    F2 = LAUNCH_APP_2,
    PgUp = BRIGHTNESS_UP,
    PgDn = BRIGHTNESS_DOWN,
    // etc.
)
```

### Pros:
✅ Works on any OS (Windows, Mac, Linux)
✅ Works in BIOS/bootloader
✅ Lower latency
✅ Portable - no software needed
✅ Can use QMK macros and tap dance

### Cons:
❌ Can't do complex OS integration (window management, app switching)
❌ Limited macro capabilities (can't read clipboard, check running apps, etc.)
❌ Hard to iterate (compile + flash each time)
❌ No visual feedback beyond RGB
❌ Can't have complex menus/submenus like current system

---

## Option 3: Hybrid Approach (Best of Both)

### Architecture: Firmware + AHK working together

**Firmware Side:**
- Layer system for basic remapping
- Encoder sends layer-aware hotkeys
- Example: Encoder held = send Ctrl+Shift+Alt+[key] combinations

**AHK Side:**
- Intercept layer hotkeys
- Provide complex logic and OS integration
- Keep menu system for encoder

### Example:
```
Encoder rotates normally: Ctrl+Alt+F13-F16 (current system)
Encoder HELD + F1: Sends Ctrl+Shift+Alt+F1 → AHK launches app
Encoder HELD + PgUp: Sends Ctrl+Shift+Alt+PgUp → AHK adjusts brightness
```

### Pros:
✅ Best of both worlds
✅ Firmware provides low-latency layer switching
✅ AHK provides rich functionality
✅ Portable layer system + powerful macros

### Cons:
❌ More complex to set up
❌ Requires managing both firmware and AHK

---

## Recommended Implementation: Enhanced AHK with Encoder Hold

### Phase 1: Encoder Hold Detection

Add to AHK:
```autohotkey
global encoderHeld := false

; Detect encoder held (track press duration)
^!Enter:: {
    ; Start timer - if held >500ms, enter function layer
}

^!Enter up:: {
    ; If was held, exit function layer
    ; If was tap, handle as normal
}
```

### Phase 2: Function Layer Mappings

**F-Keys (F1-F12) when encoder held:**
- F1: Launch Browser
- F2: Launch Terminal
- F3: Launch Email
- F4: Launch Calculator
- F5: Refresh (keep)
- F6: Spotify
- F7: Discord
- F8: File Explorer
- F9: Task Manager
- F10: Lock Screen
- F11: Full Screen (keep)
- F12: Save Screenshot

**Navigation Keys when encoder held:**
- PgUp: Brightness Up
- PgDn: Brightness Down
- Home: Volume Max
- End: Volume Mute
- Insert: Paste Special
- Delete: Close Window (Alt+F4)

**Arrow Keys when encoder held:**
- Left: Snap Window Left
- Right: Snap Window Right
- Up: Maximize Window
- Down: Minimize Window

**Number Row (1-9) when encoder held:**
- Quick launch pinned apps or virtual desktops

**Modifier Combinations when encoder held:**
- Encoder + Shift + F1-F12: Secondary macro set
- Encoder + Ctrl + Arrow: Move window between monitors

### Phase 3: Context-Aware Layers

```autohotkey
; Different layer behavior based on active app
if WinActive("ahk_exe chrome.exe") {
    ; Browser-specific shortcuts when encoder held
    F1 = New Tab
    F2 = Close Tab
    F3 = Reopen Tab
    etc.
}
```

---

## Comparison Table

| Feature | AHK Layer | Firmware Layer | Hybrid |
|---------|-----------|----------------|--------|
| OS Integration | ✅ Full | ❌ None | ✅ Full |
| Easy Iteration | ✅ Yes | ❌ No | ⚠️ Medium |
| Works Pre-Boot | ❌ No | ✅ Yes | ⚠️ Partial |
| Complex Macros | ✅ Yes | ❌ Limited | ✅ Yes |
| Latency | ⚠️ ~5-10ms | ✅ ~1ms | ⚠️ ~5-10ms |
| Visual Feedback | ✅ Yes | ❌ No | ✅ Yes |
| Portability | ❌ Needs AHK | ✅ Built-in | ⚠️ Partial |
| Context-Aware | ✅ Yes | ❌ No | ✅ Yes |

---

## My Recommendation: Enhanced AutoHotkey Layer

**Why:**
1. You want complex macros (window management, app switching, etc.) - **AHK excels at this**
2. Current encoder menu system works great - **keep building on it**
3. Easy iteration - **you can test changes in seconds**
4. Full Windows integration - **clipboard, windows, audio devices, etc.**
5. Visual feedback - **tooltips, notifications work well**

**Architecture:**
```
Hold Encoder = Function Layer Active
    ↓
Every key gets alternate function
    ↓
Release Encoder = Back to normal

OR

Encoder menu system (current) + Encoder hold = layer key
```

---

## Implementation Plan

### Step 1: Add Encoder Hold Detection
Detect press duration, switch to function layer mode

### Step 2: Remap High-Value Keys
- F-keys → App launchers
- Navigation → Brightness/Volume
- Arrows → Window snapping
- Number row → Quick apps

### Step 3: Add Visual Indicator
Show "FUNCTION LAYER ACTIVE" tooltip when encoder held

### Step 4: Context-Aware Mappings
Different key functions based on active app

### Step 5: Add Macro Recording
Let user record key sequences and bind to encoder + key

---

## Should We Rebuild Firmware?

**No, unless:**
- You need it to work on Mac/Linux (AHK is Windows-only)
- You want it to work in BIOS
- You need <1ms latency (unlikely for macros)

**Current firmware is fine because:**
- Encoder works perfectly
- Sends hotkeys reliably
- VIA compatible for basic remapping
- Simple and stable

**Stick with AHK enhancement because:**
- Way more powerful
- Much easier to customize
- Better for your use case (complex macros, OS integration)
- Can iterate rapidly

---

## Next Steps

Want me to implement:
1. ✅ **Encoder hold = function layer** (hold knob, entire keyboard transforms)
2. ✅ **F-key macro slots** (F1-F12 launch apps/scripts when encoder held)
3. ✅ **Navigation key remapping** (PgUp/PgDn = brightness, Home/End = volume)
4. ✅ **Arrow key window snapping** (when encoder held)
5. ✅ **Context-aware layers** (different functions in browser vs IDE)

Which would you like first?
