# Build and Flash Instructions - Keychron V1 Knob Macros

## Prerequisites

1. **QMK MSYS** installed (download from https://msys.qmk.fm/)
2. **QMK Toolbox** installed (download from https://github.com/qmk/qmk_toolbox/releases)
3. **AutoHotkey v2** installed (download from https://www.autohotkey.com/)

---

## Part 1: Build the Firmware

### Step 1: Set up QMK environment

Open **QMK MSYS** terminal and run:

```bash
qmk setup
```

When prompted, accept the default QMK home directory.

### Step 2: Copy firmware files to QMK directory

Navigate to your QMK keymap directory:

```bash
cd ~/qmk_firmware/keyboards/keychron/v1/ansi_encoder
```

Create your custom keymap directory:

```bash
mkdir -p keymaps/macro
```

Copy the provided files:

```bash
# Copy keymap.c
cp /c/CLIPALS/firmware/keymap.c keymaps/macro/keymap.c

# Copy rules.mk
cp /c/CLIPALS/firmware/rules.mk keymaps/macro/rules.mk
```

### Step 3: Compile the firmware

```bash
qmk compile -kb keychron/v1/ansi_encoder -km macro
```

**Expected output:**
```
Compiling: keyboards/keychron/v1/ansi_encoder/keychron_v1_ansi_encoder_macro.bin
...
Checking file size of keychron_v1_ansi_encoder_macro.bin
 * File size is fine - 27234/28672 (95.0%)
```

**Output file location:**
```
~/qmk_firmware/.build/keychron_v1_ansi_encoder_macro.bin
```

---

## Part 2: Flash the Firmware

### Step 1: Open QMK Toolbox

1. Launch **QMK Toolbox**
2. Click **Open** and select the compiled `.bin` file:
   - Default path: `C:\Users\<YourUsername>\qmk_firmware\.build\keychron_v1_ansi_encoder_macro.bin`

### Step 2: Put keyboard in bootloader mode

**Method 1: Physical reset (recommended)**
1. Unplug the keyboard
2. Hold **Space + B** keys
3. Plug in the USB cable while holding
4. Release keys after 2 seconds

**Method 2: Software reset**
1. Hold **Fn + J + Z** for 4 seconds
2. Keyboard will disconnect and reconnect in bootloader mode

**QMK Toolbox should display:**
```
*** STM32 device connected: Keychron V1 ANSI (bootloader)
```

### Step 3: Flash

1. In QMK Toolbox, verify:
   - MCU is set to **STM32F103** or **Auto-Detect**
   - Your `.bin` file is loaded
2. Click **Flash**

**Expected output:**
```
>>> Flashing keychron_v1_ansi_encoder_macro.bin
>>> Flash complete
>>> STM32 device disconnected
*** Keychron V1 ANSI connected
```

### Step 4: Test firmware

1. Rotate the knob → Windows should show volume change (default encoder behavior overridden)
2. Press the knob → Nothing happens yet (waiting for AutoHotkey script)

---

## Part 3: Set Up AutoHotkey Script

### Step 1: Install AutoHotkey v2

Download and install from: https://www.autohotkey.com/

### Step 2: Run the command handler script

Double-click:
```
C:\CLIPALS\scripts\keychron_commands.ahk
```

You should see a notification:
```
Keychron Command Macro Handler Active
```

### Step 3: Test the complete system

1. **Rotate knob clockwise** → Tooltip shows: "Open Terminal"
2. **Rotate again** → "Launch VSCode"
3. **Continue rotating** → Cycles through all 4 commands
4. **Press knob** → Executes currently selected command

---

## Part 4: Customize Commands

Edit `C:\CLIPALS\scripts\keychron_commands.ahk`

Find the `commands` array and modify:

```ahk
commands := [
    {
        name: "Your Command 1",
        action: () => Run("notepad.exe")
    },
    {
        name: "Your Command 2", 
        action: () => Run("powershell.exe -Command 'Get-Date'")
    },
    {
        name: "Your Command 3",
        action: () => Run("C:\Path\To\Your\Script.bat")
    },
    {
        name: "Your Command 4",
        action: () => MsgBox("Hello World!")
    }
]
```

**Save and reload:**
- Right-click AutoHotkey tray icon → Reload Script

---

## Part 5: Auto-Start on Windows Boot (Optional)

1. Press **Win + R**
2. Type: `shell:startup`
3. Press **Enter**
4. Create a shortcut to `C:\CLIPALS\scripts\keychron_commands.ahk` in this folder

---

## Troubleshooting

### Firmware won't compile
- Run `qmk doctor` in QMK MSYS to check environment
- Ensure you're in the correct keyboard directory

### Keyboard won't enter bootloader
- Try unplugging and replugging while holding Space + B
- Check USB cable (data cable, not charge-only)

### Knob rotation doesn't change commands
- Check if AutoHotkey script is running (look for tray icon)
- Verify hotkeys aren't blocked by another application

### Commands don't execute
- Open AutoHotkey script and check for syntax errors
- Test command manually in PowerShell/CMD first

### VIA doesn't detect keyboard
- VIA should detect automatically after flash
- If not, download latest VIA from https://usevia.app/

---

## What Each Component Does

| Component | Responsibility |
|-----------|---------------|
| **QMK Firmware** | Detects knob rotation/press, sends hotkeys to OS |
| **AutoHotkey Script** | Receives hotkeys, executes actual commands |
| **VIA Software** | Optional GUI for remapping regular keys (not encoder) |

**Key Point:** Changing commands requires **only** editing the AutoHotkey script — no reflashing needed.

---

## Success Verification

✅ Firmware compiled without errors  
✅ QMK Toolbox flashed successfully  
✅ Keyboard reconnects after flash  
✅ AutoHotkey script shows tray icon  
✅ Knob rotation cycles through commands (tooltip shows names)  
✅ Knob press executes selected command  
✅ VIA still detects keyboard  

If all checks pass, the system is fully operational.
