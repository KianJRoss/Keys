# Encoder Behavior Diagnostic Test

## Purpose
This test script shows **exactly** what your knob sends to Windows for each action.

## How to Run

### Step 1: Stop the main script
Right-click **AutoHotkey tray icon** (green H) → **Exit**

### Step 2: Run diagnostic script
Double-click: `C:\CLIPALS\scripts\keychron_test_encoder.ahk`

A tooltip will appear showing a live log.

### Step 3: Test each action

**Actions to test:**

1. **Slow clockwise rotation** (one click at a time)
2. **Slow counter-clockwise rotation** (one click at a time)
3. **Fast clockwise rotation** (spin it)
4. **Fast counter-clockwise rotation** (spin it)
5. **Single tap** (quick press & release)
6. **Double-tap** (two quick presses)
7. **Press and hold** (hold for 2-3 seconds)

---

## What We're Looking For

### Rotation Direction
The log will show:
- `CLOCKWISE ➡` - Knob rotated clockwise
- `COUNTER-CLOCKWISE ⬅` - Knob rotated counter-clockwise
- Which F-key was sent (F13/F14/F15/F16)

**Question: Does clockwise always go F13→F14→F15→F16→F13?**

---

### Single Click/Tap
The log will show:
- `PRESS DOWN | Click 1` - When you press the knob
- `RELEASE (tap) | XXms` - When you release

**Questions:**
- Does it trigger once or multiple times?
- What's the typical duration? (should be <200ms for tap)

---

### Double-Click
The log will show:
- `DOUBLE-CLICK | Detected!` - If two clicks within 300ms

**Questions:**
- Does double-click detection work reliably?
- What's the max time between clicks that still counts as double?

---

### Press and Hold
The log will show:
- `PRESS DOWN` - Initial press
- `HOLDING | 500ms` - After holding for 500ms
- `STILL HOLDING | 1000ms` - Updates every 500ms while held
- `RELEASE (after hold) | XXXXms` - When you release

**CRITICAL QUESTION:**
- Does the firmware send **one** `Ctrl+Alt+Enter` on press, or does it **repeat** while held?
- If it repeats, how often?

---

## Expected Behavior Patterns

### Pattern 1: Firmware sends signal ONCE on press
```
PRESS DOWN → RELEASE (tap) → Done
```
**Use case:** Single action per click (like selecting a menu item)

### Pattern 2: Firmware REPEATS signal while held
```
PRESS DOWN → (repeat) → (repeat) → RELEASE
```
**Use case:** Hold for continuous action (like volume adjustment)

---

## Menu Design Based on Results

Once we know the behavior, we can design:

### If hold works (repeats):
- **Rotate:** Select menu item
- **Tap:** Confirm selection
- **Double-tap:** Back/Cancel
- **Hold:** Alternative action (e.g., enter settings)

### If hold doesn't work (single trigger):
- **Rotate:** Select menu item
- **Tap:** Confirm selection
- **Double-tap:** Alternative action
- **Hold:** (Not usable, same as tap)

---

## Example Log Output

```
=== KEYCHRON ENCODER DIAGNOSTIC ===
Rotate knob, press/hold/double-click to see behavior

--- LAST 20 ACTIONS ---
14:23:45 | F13 (Command 0) | CLOCKWISE ➡
14:23:46 | F14 (Command 1) | CLOCKWISE ➡
14:23:47 | F15 (Command 2) | CLOCKWISE ➡
14:23:48 | F16 (Command 3) | CLOCKWISE ➡
14:23:49 | F13 (Command 0) | CLOCKWISE ➡
14:23:50 | PRESS DOWN | Click 1
14:23:50 | RELEASE (tap) | 120ms
14:23:52 | PRESS DOWN | Click 1
14:23:52 | HOLDING | 500ms
14:23:53 | STILL HOLDING | 1000ms
14:23:54 | STILL HOLDING | 1500ms
14:23:54 | RELEASE (after hold) | 2340ms
```

---

## After Testing

### Report back what you see for:
1. **Clockwise rotation** - Does it go F13→F14→F15→F16 consistently?
2. **Counter-clockwise** - Does it go F16→F15→F14→F13?
3. **Single tap** - One trigger or multiple?
4. **Hold** - Does it repeat? How often?
5. **Double-click** - Reliable detection?

This will tell us exactly how to design the menu system!

---

## Exit Diagnostic Mode

Close the tooltip or right-click tray icon → Exit

Then restart your normal script:
```
C:\CLIPALS\scripts\keychron_commands.ahk
```
