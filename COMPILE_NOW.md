# Quick Compile Guide - Choose Your Method

Your firmware files are ready at:
- `C:\CLIPALS\firmware\keymap.c`
- `C:\CLIPALS\firmware\rules.mk`

They have been copied to:
- `C:\CLIPALS\qmk_firmware\keyboards\keychron\v1\ansi_encoder\keymaps\macro\`

---

## Method 1: QMK MSYS (Recommended)

### Step 1: Open QMK MSYS Terminal
1. Press **Windows key**
2. Type **"QMK MSYS"**
3. Click **QMK MSYS** (should have a green icon)

**If you don't see QMK MSYS:**
Download from: https://msys.qmk.fm/
Install, then come back here.

### Step 2: Run Build Command

In the QMK MSYS terminal, copy and paste this:

```bash
cd /c/CLIPALS/qmk_firmware
qmk compile -kb keychron/v1/ansi_encoder -km macro
```

### Step 3: Wait for Compilation

You'll see output like:
```
Compiling: keyboards/keychron/v1/ansi_encoder/keymaps/macro/keymap.c
...
Linking: .build/keychron_v1_ansi_encoder_macro.elf
Creating binary load file: .build/keychron_v1_ansi_encoder_macro.bin
```

**Build time:** ~30-60 seconds

### Step 4: Success!

When you see:
```
Checking file size of keychron_v1_ansi_encoder_macro.bin
 * File size is fine - XXXXX/28672 (XX.X%)
```

Your firmware is ready at:
```
C:\CLIPALS\qmk_firmware\.build\keychron_v1_ansi_encoder_macro.bin
```

---

## Method 2: Use the Batch Script (Windows)

### Step 1: Start Docker Desktop
1. Open Docker Desktop
2. Wait for it to fully start (whale icon should be stable)

### Step 2: Run Docker Build

Open **PowerShell** or **Command Prompt** and run:

```powershell
cd C:\CLIPALS
docker run --rm -v "${PWD}/qmk_firmware:/qmk_firmware" qmkfm/qmk_cli qmk compile -kb keychron/v1/ansi_encoder -km macro
```

**First time:** Docker will download the QMK build environment (~2GB)  
**After that:** Builds take ~30 seconds

---

## Method 3: WSL (If You Have Linux Subsystem)

```bash
cd /mnt/c/CLIPALS/qmk_firmware
qmk compile -kb keychron/v1/ansi_encoder -km macro
```

---

## Troubleshooting

### "qmk: command not found"
→ You're not in QMK MSYS terminal. Use Method 1 instructions.

### "Keyboard not found"
→ Run `qmk setup` first in QMK MSYS

### "Permission denied"
→ Close VIA or any software using the keyboard
→ Run terminal as Administrator

### Docker errors
→ Start Docker Desktop first
→ On first run, it downloads QMK image (~2GB)

---

## After Successful Build

You'll have:
```
C:\CLIPALS\qmk_firmware\.build\keychron_v1_ansi_encoder_macro.bin
```

**Next step:** Flash with QMK Toolbox (see `docs/BUILD_AND_FLASH.md` section "Part 2: Flash the Firmware")

---

## Quick Flash Steps

1. Open **QMK Toolbox**
2. Click **Open** → select the `.bin` file above
3. **Unplug keyboard**
4. Hold **Space + B**
5. **Plug in keyboard** while holding
6. Release keys after 2 seconds
7. Click **Flash** in QMK Toolbox

Done! Your knob now controls commands.
