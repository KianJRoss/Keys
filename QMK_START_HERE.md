# Keychron V1 - Rotary Encoder Macro Cycling Firmware

Complete QMK firmware implementation for Keychron V1 ANSI Encoder with rotary encoder macro cycling.

## 🎯 What This Does

- **Turn the encoder knob** → Cycle through 8 different macros
- **Press the encoder knob** → Execute the currently selected macro
- **Full VIA support** → Remap other keys using VIA app

## 🚀 Quick Start (3 Steps)

### 1️⃣ Install MSYS2

```powershell
# Run this in PowerShell (as Administrator):
powershell -ExecutionPolicy Bypass -File download_msys2.ps1
```

This downloads and helps you install MSYS2 (build environment).

**OR** download manually: https://www.msys2.org/

### 2️⃣ Setup & Compile

```batch
# Double-click or run:
setup_qmk.bat
```

Choose option **1** (Full Setup). This will:
- Install build tools
- Install QMK CLI
- Compile your firmware

Output: `keychron_v1_ansi_encoder_knob_macros.bin`

### 3️⃣ Flash to Keyboard

1. Download [QMK Toolbox](https://github.com/qmk/qmk_toolbox/releases/latest)
2. Open the `.bin` file in QMK Toolbox
3. Put keyboard in bootloader mode:
   - Unplug keyboard
   - Hold `ESC`
   - Plug in keyboard
   - Release `ESC`
4. Click **Flash**

**Done!** Your keyboard now has macro cycling.

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed MSYS2 setup instructions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical overview
- **[FLASHING_GUIDE.md](FLASHING_GUIDE.md)** - Step-by-step flashing tutorial
- **[qmk_firmware/.../knob_macros/README.md](qmk_firmware/keyboards/keychron/v1/ansi_encoder/keymaps/knob_macros/README.md)** - Firmware details & customization

## 🎨 Pre-configured Macros

| # | Macro | Function |
|---|-------|----------|
| 0 | Hello World | Types "Hello World" |
| 1 | Copy | Ctrl+C |
| 2 | Paste | Ctrl+V |
| 3 | Cut | Ctrl+X |
| 4 | Undo | Ctrl+Z |
| 5 | Redo | Ctrl+Y |
| 6 | Select All | Ctrl+A |
| 7 | Save | Ctrl+S |

## 🔧 Customization

Edit `qmk_firmware/keyboards/keychron/v1/ansi_encoder/keymaps/knob_macros/keymap.c`

### Add More Macros:

```c
// Change macro count
#define MACRO_COUNT 10  // was 8

// Add new cases
case 8:
    SEND_STRING(SS_LGUI(SS_LSFT("s")));  // Win+Shift+S (Screenshot)
    break;
case 9:
    SEND_STRING(SS_LGUI("l"));  // Win+L (Lock screen)
    break;
```

### Macro Syntax:

- `SEND_STRING("text")` - Type text
- `SS_LCTRL("x")` - Ctrl+X
- `SS_LALT("x")` - Alt+X
- `SS_LSFT("x")` - Shift+X
- `SS_LGUI("x")` - Win/Cmd+X
- `SS_TAP(X_KEY)` - Tap a key

Recompile after editing: `setup_qmk.bat` → Option 2

## 📁 Project Structure

```
C:\CLIPALS\
├── QMK_START_HERE.md (this file)
├── SETUP_GUIDE.md
├── FLASHING_GUIDE.md
├── IMPLEMENTATION_SUMMARY.md
├── download_msys2.ps1
├── setup_qmk.bat
└── qmk_firmware/
    └── keyboards/keychron/v1/ansi_encoder/keymaps/knob_macros/
        ├── keymap.c (main firmware)
        ├── rules.mk (build config)
        └── README.md (detailed docs)
```

## ⚡ Automation Scripts

### `download_msys2.ps1`
PowerShell script to download MSYS2 installer automatically.

### `setup_qmk.bat`
Automated setup and compilation:
- **Option 1**: Full setup + compile
- **Option 2**: Compile only (if already set up)

## 🔍 Troubleshooting

### Compilation Issues

```bash
# Check QMK environment health:
qmk doctor

# Reinstall dependencies:
pacman -S --needed base-devel mingw-w64-x86_64-toolchain
```

### Encoder Not Working

- Confirm using `ansi_encoder` variant (not `ansi`)
- Verify `ENCODER_ENABLE = yes` in rules.mk
- Check physical encoder connection

### Flash Failed

- Try different USB cable/port
- Reinstall drivers (QMK Toolbox → Help → Install Drivers)
- Retry bootloader mode

## 📚 Resources

- **QMK Documentation**: https://docs.qmk.fm/
- **VIA App**: https://www.caniusevia.com/
- **Keychron Support**: https://www.keychron.com/pages/firmware-support
- **QMK Discord**: https://discord.gg/qmk

## ✅ Features

- ✓ Rotary encoder macro cycling
- ✓ 8 pre-configured productivity macros
- ✓ VIA support for keymap customization
- ✓ Easy to extend with more macros
- ✓ Automated build scripts
- ✓ Comprehensive documentation

## 🎓 Learning Resources

New to QMK? Check out:
- [QMK Tutorial](https://docs.qmk.fm/#/newbs)
- [Keycode Reference](https://docs.qmk.fm/#/keycodes)
- [Macro Examples](https://docs.qmk.fm/#/feature_macros)

## 📝 License

Based on Keychron V1 default firmware.
GPL-2.0-or-later

---

## Support

Having issues? Check documentation:
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup problems
2. [FLASHING_GUIDE.md](FLASHING_GUIDE.md) - Flashing problems
3. Firmware README - Customization help

Still stuck?
- QMK Discord: https://discord.gg/qmk
- Open an issue on QMK GitHub
- Keychron support forums

---

**Made with ❤️ using QMK Firmware**
