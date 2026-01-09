# Build and Flash Guide - Keychron V1 Raw HID Firmware

Complete guide for building and flashing the custom firmware to your Keychron V1 ANSI Encoder.

## ⚠️ Important Warnings

1. **Backup your current firmware** - Flash the stock firmware again if anything goes wrong
2. **Verify your keyboard variant** - This is for **ANSI Encoder** variant only
3. **Keep bootloader access** - Know how to enter bootloader mode before flashing
4. **VIA settings will be reset** - Backup VIA configuration if needed

## Prerequisites

### Required Software

1. **QMK MSYS** (Windows) or QMK CLI (Mac/Linux)
   - Download: https://msys.qmk.fm/
   - Install to default location

2. **QMK Toolbox** (for flashing)
   - Download: https://github.com/qmk/qmk_toolbox/releases
   - Install latest version

3. **Python 3.8+** (for host software)
   - Download: https://www.python.org/downloads/
   - Check "Add to PATH" during installation

### Verify Your Keyboard Variant

Open VIA or check your keyboard box to confirm:
- Model: **Keychron V1**
- Layout: **ANSI** (not ISO or JIS)
- Has: **Rotary encoder knob** (top-right corner)

## Step 1: Build the Firmware

### Option A: Using the Build Script (Recommended)

1. Open **QMK MSYS** from Start Menu
2. Navigate to the keymap directory:
   ```bash
   cd /c/CLIPALS/qmk_firmware/keyboards/keychron/v1/ansi_encoder/keymaps/raw_hid_menu
   ```
3. Run the build script:
   ```bash
   ./build.bat
   ```

### Option B: Manual Build

1. Open **QMK MSYS** terminal
2. Navigate to QMK directory:
   ```bash
   cd /c/CLIPALS/qmk_firmware
   ```
3. Compile:
   ```bash
   qmk compile -kb keychron/v1/ansi_encoder -km raw_hid_menu
   ```

### Build Output

If successful, you'll see:
```
Compiling: keyboards/keychron/v1/ansi_encoder/keymaps/raw_hid_menu/keymap.c
...
Linking: .build/keychron_v1_ansi_encoder_raw_hid_menu.elf
Creating binary load file for flashing: .build/keychron_v1_ansi_encoder_raw_hid_menu.bin
```

**Output location:** `C:\CLIPALS\qmk_firmware\.build\keychron_v1_ansi_encoder_raw_hid_menu.bin`

## Step 2: Enter Bootloader Mode

### Method 1: ESC Key Method (Easiest)
1. Unplug your keyboard
2. Hold down **ESC** key
3. While holding ESC, plug in the USB cable
4. Release ESC after 2 seconds
5. Keyboard should appear as "STM32 BOOTLOADER" in Device Manager

### Method 2: Physical Reset Button
1. Flip keyboard over or remove keycaps
2. Locate small reset button on PCB (usually near USB port)
3. Press reset button with paperclip
4. Keyboard enters bootloader mode

### Verify Bootloader Mode
- **Windows:** Device Manager shows "STM32 BOOTLOADER" or "DFU Device"
- **QMK Toolbox:** Shows "STM32 device connected"
- **Keyboard:** All LEDs off, no keypresses work

## Step 3: Flash the Firmware

### Using QMK Toolbox

1. Open **QMK Toolbox**

2. **Select Firmware File:**
   - Click "Open" button
   - Navigate to: `C:\CLIPALS\qmk_firmware\.build\`
   - Select: `keychron_v1_ansi_encoder_raw_hid_menu.bin`

3. **Configure Flash Settings:**
   - MCU: Should auto-detect as `STM32L432`
   - Check "Auto-Flash" (optional, flashes when bootloader detected)

4. **Put keyboard in bootloader mode** (see Step 2)

5. **Flash:**
   - QMK Toolbox should show "STM32 device connected"
   - Click **"Flash"** button
   - Wait for "Flash complete" message
   - Keyboard will automatically restart

### Expected Output
```
*** STM32 device connected: STM32 BOOTLOADER
*** Attempting to flash, please don't remove device
>>> dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D keychron_v1_ansi_encoder_raw_hid_menu.bin
...
File downloaded successfully
*** Flash complete
*** STM32 device disconnected
```

## Step 4: Verify Firmware

### Check Basic Functionality
1. Keyboard should reconnect automatically
2. Try typing - all keys should work
3. Rotate encoder - should produce volume change (default behavior on FN layer)
4. Press encoder - should produce mute

### Check VIA Recognition (Optional)
1. Open VIA (https://usevia.app/ or desktop app)
2. Keyboard should be recognized
3. Basic key remapping should work
4. Note: Custom encoder behavior won't show in VIA

### Check Raw HID Communication
1. Open Command Prompt/PowerShell
2. Navigate to Python host:
   ```bash
   cd C:\CLIPALS\python_host
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run test tool:
   ```bash
   python hid_test.py
   ```
5. Expected output:
   ```
   ✓ Connected to: Keychron Keychron V1
   → HID reader thread started
   → Watchdog thread started
   Waiting for encoder events...
   ```
6. Rotate encoder and press button - events should appear

## Troubleshooting

### Build Errors

#### "qmk: command not found"
- Solution: Make sure you're using **QMK MSYS** terminal, not regular CMD/PowerShell
- Run: `qmk doctor` to check environment

#### "error: 'raw_hid_send' undeclared"
- Solution: Verify `RAW_ENABLE = yes` in `rules.mk`
- Run clean build: `qmk clean && qmk compile -kb keychron/v1/ansi_encoder -km raw_hid_menu`

#### "region 'FLASH' overflowed by X bytes"
- Solution: Firmware too large for 128KB flash
- Edit `config.h` and uncomment RGB effect disables:
  ```c
  #define DISABLE_RGB_MATRIX_DIGITAL_RAIN
  #define DISABLE_RGB_MATRIX_PIXEL_RAIN
  // ... etc
  ```
- Or disable VIA: Change `VIA_ENABLE = no` in `rules.mk`

### Flash Errors

#### "No DFU device found"
- Solution: Keyboard not in bootloader mode
- Try different USB port
- Use ESC method instead of reset button
- Check USB cable is data-capable (not charge-only)

#### "Flash failed: dfu-util returned -1"
- Solution: Driver issue
- Install STM32 DFU drivers via Zadig (Google "STM32 DFU Zadig")
- Or use QMK Toolbox's built-in driver installer

#### "Device disconnected during flash"
- Solution: USB power issue
- Try different USB port (use USB 2.0 port if possible)
- Don't use USB hub
- Reconnect and retry flash

### Post-Flash Issues

#### Keyboard not working at all
- Solution: Wrong firmware variant flashed
- Re-flash stock firmware from Keychron website
- Verify you have ANSI Encoder variant

#### Encoder not responding
- Solution: Check encoder is working in default VIA mode first
- Verify QMK encoder map in firmware
- Check encoder pins in `config.h`

#### Python test tool can't connect
- Solution: VID/PID mismatch
- Check Device Manager for actual VID/PID
- Update `VENDOR_ID` and `PRODUCT_ID` in `hid_test.py`
- Try unplugging and replugging keyboard

#### VIA conflicts with Raw HID
- Solution: Disable VIA if only using Raw HID
- Edit `rules.mk`: Change `VIA_ENABLE = yes` to `VIA_ENABLE = no`
- Rebuild and reflash

## Recovery - Restoring Stock Firmware

If anything goes wrong:

1. Download stock firmware:
   - Visit: https://www.keychron.com/pages/firmware-and-json-files-of-the-keychron-v-series-keyboards
   - Find: Keychron V1 ANSI Knob version firmware

2. Flash stock firmware:
   - Use QMK Toolbox
   - Enter bootloader mode
   - Flash the stock `.bin` file

3. Reset VIA:
   - Open VIA
   - Settings → "Reset EEPROM"
   - Reconfigure layouts

## Next Steps

After successful flash and verification:

1. **Explore encoder gestures:**
   - Watch Python test tool output
   - Try: rotation, press, long-press, double-tap

2. **Test LED control:**
   - Modify `hid_test.py` to send different colors/modes
   - Observe LED changes on encoder area

3. **Develop host software:**
   - Implement menu state machine
   - Build overlay UI
   - Add command execution backends

4. **Customize firmware:**
   - Adjust gesture timing in `keymap.c`
   - Add more LED modes
   - Modify event protocol if needed

## Reference Links

- QMK Documentation: https://docs.qmk.fm/
- Keychron Support: https://www.keychron.com/pages/firmware-and-json-files-of-the-keychron-v-series-keyboards
- QMK Toolbox: https://github.com/qmk/qmk_toolbox
- VIA: https://usevia.app/

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review QMK firmware logs in QMK Toolbox
3. Verify hardware with stock firmware first
4. Check Python test tool output for HID communication issues
