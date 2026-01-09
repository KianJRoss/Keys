# Getting Your Keyboard Working with Python

## What's Wrong Right Now

You have **two different firmware implementations**:

1. **Simple Hotkey Firmware** (in `firmware/` folder)
   - Sends Ctrl+Alt+F13-F16 keyboard shortcuts
   - Works with AutoHotkey scripts
   - **NOT compatible with Python**

2. **Raw HID Firmware** (in `qmk_firmware/.../raw_hid_menu/` folder)
   - Sends structured HID packets
   - **IS compatible with Python**
   - This is what you need!

Your `python_host/hid_test.py` expects the **Raw HID firmware**, but your keyboard likely has the **hotkey firmware** flashed.

## Solution: Flash the Raw HID Firmware

### Step 1: Build the Firmware

Open **QMK MSYS** (from Start Menu) and run:

```bash
cd /c/Repos/Keyboard/qmk_firmware
qmk compile -kb keychron/v1/ansi_encoder -km raw_hid_menu
```

Or use the build script:
```bash
cd /c/Repos/Keyboard/qmk_firmware/keyboards/keychron/v1/ansi_encoder/keymaps/raw_hid_menu
./build.bat
```

**Output will be:** `C:\Repos\Keyboard\qmk_firmware\.build\keychron_v1_ansi_encoder_raw_hid_menu.bin`

### Step 2: Flash to Keyboard

1. Open **QMK Toolbox**
2. Click "Open" and select the `.bin` file from above
3. Put keyboard in bootloader mode:
   - Unplug keyboard
   - Hold **ESC** key
   - Plug in USB cable while holding ESC
   - Release after 2 seconds
4. Click **Flash** in QMK Toolbox
5. Wait for "Flash complete" message

### Step 3: Test Python Connection

```bash
cd C:\Repos\Keyboard\python_host

# First, find your keyboard's VID/PID
python list_devices.py

# Then test the connection
python hid_test.py
```

When you rotate or press the encoder knob, you should see events like:
```
[  123ms] Encoder 0: CW (val=1)
[  456ms] Encoder 0: PRESS (val=0)
[  789ms] Encoder 0: RELEASE (val=0)
```

## What the Raw HID Firmware Does

### Sends to Python:
- **Rotation events**: CW/CCW when you turn the knob
- **Button events**: PRESS/RELEASE/LONG_PRESS/DOUBLE_TAP when you click the knob
- **Timestamps**: So Python knows when each event happened

### Receives from Python:
- **LED mode commands**: Change the LED behavior
- **LED color commands**: Set RGB colors

### Protocol Example:
```
Firmware → Python:  [0x01][EventType][EncoderID][Value][Timestamp][...]
Python → Firmware:  [0x02][Command][Arg1][Arg2][Arg3][...]
```

## Key Files Explained

| File | Purpose |
|------|---------|
| `qmk_firmware/.../raw_hid_menu/keymap.c` | Raw HID firmware source |
| `qmk_firmware/.../raw_hid_menu/rules.mk` | Enables RAW_ENABLE=yes |
| `python_host/hid_test.py` | Python test tool |
| `python_host/list_devices.py` | Find keyboard VID/PID |
| `firmware/keymap.c` | OLD hotkey firmware (ignore this) |

## Troubleshooting

### Python can't find keyboard
Run `python list_devices.py` to see all HID devices. Look for Keychron entries and update the VID/PID in `hid_test.py`:
```python
VENDOR_ID = 0x3434   # Update if needed
PRODUCT_ID = 0x0312  # Update if needed
```

### Firmware won't compile
- Make sure you opened **QMK MSYS** (not regular Command Prompt)
- Run `qmk doctor` to check environment
- Check for errors in the output

### Keyboard won't enter bootloader
- Try the space bar method: Hold **SPACE** + **B** while plugging in
- Or check if there's a reset button on the back of the PCB

### Python sees events but LEDs don't change
This is normal in test mode. The firmware receives the commands but you need to implement the LED patterns you want.

## Next Steps After It Works

Once `hid_test.py` shows encoder events:

1. **Menu System**: Build the state machine for menu navigation
2. **Overlay UI**: Create the transparent on-screen menu
3. **Commands**: Implement volume, media, window management, etc.
4. **Configuration**: Add user-customizable macros

See `PROJECT_STATUS.md` for the full roadmap.

## Quick Reference

**Build firmware:**
```bash
cd /c/Repos/Keyboard/qmk_firmware
qmk compile -kb keychron/v1/ansi_encoder -km raw_hid_menu
```

**Test Python:**
```bash
cd C:\Repos\Keyboard\python_host
python hid_test.py
```

**Check devices:**
```bash
python list_devices.py
```
