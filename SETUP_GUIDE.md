# QMK Firmware Compilation Setup Guide

## Quick Setup Steps

### Step 1: Install MSYS2

1. **Download MSYS2 installer**:
   - Visit: https://www.msys2.org/
   - Download: `msys2-x86_64-latest.exe`
   - Or direct link: https://github.com/msys2/msys2-installer/releases/latest/download/msys2-x86_64-latest.exe

2. **Run the installer**:
   - Double-click the downloaded `.exe`
   - Install to default location: `C:\msys64`
   - Check "Run MSYS2 now" at the end

3. **Update MSYS2** (in the MSYS2 terminal that opens):
   ```bash
   pacman -Syu
   ```
   - If it closes, reopen "MSYS2 MSYS" from Start Menu and run again:
   ```bash
   pacman -Su
   ```

### Step 2: Install Build Tools

Close any open MSYS2 window and open **"MSYS2 MinGW 64-bit"** from the Start Menu (important!).

Then run:

```bash
pacman -S --needed base-devel mingw-w64-x86_64-toolchain git mingw-w64-x86_64-python-pip unzip
```

Press Enter when prompted to install all packages.

### Step 3: Install QMK CLI

In the same MSYS2 MinGW 64-bit terminal:

```bash
python -m pip install qmk
```

### Step 4: Navigate to Firmware Directory

```bash
cd /c/CLIPALS/qmk_firmware
```

### Step 5: Install QMK Dependencies

```bash
qmk setup -y
```

This will install required tools (may take a few minutes).

### Step 6: Compile Your Firmware

```bash
qmk compile -kb keychron/v1/ansi_encoder -km knob_macros
```

### Step 7: Find Your Firmware

After successful compilation, look for:
```
keychron_v1_ansi_encoder_knob_macros.bin
```

It will be in the `qmk_firmware` directory.

---

## Alternative: Quick PowerShell Script

I've created an automated setup script for you. After installing MSYS2 manually (Step 1 above), you can use the automated script.

---

## Troubleshooting

### "pacman: command not found"
- Make sure you're using "MSYS2 MinGW 64-bit" terminal, not regular Windows CMD

### "python: command not found"
- Reinstall the toolchain: `pacman -S mingw-w64-x86_64-python-pip`

### "qmk: command not found"
- Reinstall QMK: `python -m pip install qmk`
- Or add to PATH: `export PATH="$HOME/.local/bin:$PATH"`

### Compilation errors
- Run `qmk doctor` to check for issues
- Make sure all dependencies installed: `pacman -S --needed base-devel mingw-w64-x86_64-toolchain`

---

## What Happens During Compilation?

The compiler will:
1. Parse your keymap configuration
2. Link with QMK core libraries
3. Build for STM32 microcontroller (Keychron V1's chip)
4. Generate `.bin` firmware file

Expected output:
```
Compiling: keyboards/keychron/v1/ansi_encoder/keymaps/knob_macros/keymap.c
Linking: .build/keychron_v1_ansi_encoder_knob_macros.elf
Creating binary load file for flashing: .build/keychron_v1_ansi_encoder_knob_macros.bin
...
Copying keychron_v1_ansi_encoder_knob_macros.bin
```

---

## Next: Flash to Keyboard

After compilation succeeds, see `FLASHING_GUIDE.md` for detailed flashing instructions.
