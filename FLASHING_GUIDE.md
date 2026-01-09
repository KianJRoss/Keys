# Firmware Flashing Guide - Keychron V1

## Prerequisites

✓ Compiled firmware file: `keychron_v1_ansi_encoder_knob_macros.bin`
✓ QMK Toolbox installed
✓ Your Keychron V1 keyboard

## Step 1: Download QMK Toolbox

1. Visit: https://github.com/qmk/qmk_toolbox/releases/latest
2. Download: `qmk_toolbox.exe` (Windows)
3. Run the executable (no installation needed)

**Direct link**: https://github.com/qmk/qmk_toolbox/releases/latest/download/qmk_toolbox.exe

## Step 2: Open Your Firmware File

1. Launch QMK Toolbox
2. Click **"Open"** button
3. Navigate to: `C:\CLIPALS\qmk_firmware\`
4. Select: `keychron_v1_ansi_encoder_knob_macros.bin`
5. Verify the file path appears in the text box

## Step 3: Prepare Your Keyboard

### Enter Bootloader Mode (Choose One Method):

#### Method A: Physical Reset (Recommended)
1. **Unplug** the keyboard USB cable
2. **Locate** the reset button on the bottom of the keyboard (small hole)
3. **Press and hold** the reset button with a paperclip
4. **Plug in** the USB cable while holding reset
5. **Release** reset button after 2 seconds

#### Method B: Key Combination
1. **Unplug** the keyboard
2. **Press and hold** the `ESC` key (top-left)
3. **Plug in** the USB cable while holding `ESC`
4. **Release** `ESC` after 2 seconds

#### Method C: Function Layer (if available)
1. Hold `Fn` + `J` + `Z` for 4 seconds
2. Keyboard enters bootloader mode

### Confirm Bootloader Mode:

In QMK Toolbox, you should see yellow text like:
```
*** STM32 device connected: Keychron V1 (XXXX:XXXX:0000)
```

If you see this, you're ready to flash!

## Step 4: Flash the Firmware

1. In QMK Toolbox, check **"Auto-Flash"** checkbox (recommended)
   - OR click **"Flash"** button manually

2. Wait for the process to complete (10-30 seconds)

3. You'll see messages like:
   ```
   *** Attempting to flash, please don't remove device
   >>> dfu-util ...
   *** Flashing succeeded!
   *** STM32 device disconnected
   ```

4. The keyboard will automatically reboot with new firmware

## Step 5: Test Your Firmware

### Test Encoder:

1. **Turn the knob** - Cycles through macros (no visible change, just internal state)
2. **Press the knob** - Should execute Macro 0 ("Hello World")
3. **Turn knob clockwise** once
4. **Press the knob** - Should execute Macro 1 (Copy - Ctrl+C)

### Test Macros:

Open a text editor and test each macro:

| Action | Expected Result |
|--------|----------------|
| Turn knob to macro 0, press | Types "Hello World" |
| Turn knob to macro 1, press | Copy command (Ctrl+C) |
| Turn knob to macro 2, press | Paste command (Ctrl+V) |
| Turn knob to macro 3, press | Cut command (Ctrl+X) |
| Turn knob to macro 4, press | Undo (Ctrl+Z) |
| Turn knob to macro 5, press | Redo (Ctrl+Y) |
| Turn knob to macro 6, press | Select All (Ctrl+A) |
| Turn knob to macro 7, press | Save (Ctrl+S) |

### Test Regular Keys:

Type normally to verify all keys still work as expected.

## Troubleshooting

### Keyboard Not Detected

**Problem**: QMK Toolbox doesn't show device connected

**Solutions**:
- Try different USB cable (some are charge-only)
- Try different USB port (USB 2.0 ports work best)
- Try bootloader mode again
- Check Windows Device Manager for "STM32 BOOTLOADER" device
- Install STM32 DFU drivers (QMK Toolbox → Help → Install Drivers)

### Flash Failed

**Problem**: "Flashing failed" or error messages

**Solutions**:
- Put keyboard back in bootloader mode
- Try manual flash (uncheck Auto-Flash, click Flash button)
- Check .bin file is correct (not corrupted)
- Try different USB port
- Close other programs that might access keyboard

### Keyboard Not Working After Flash

**Problem**: Keys don't respond after flashing

**Solutions**:
- Unplug and replug keyboard
- Try resetting: Hold ESC, plug in, release ESC
- Reflash firmware
- As last resort, flash back to original Keychron firmware

### Encoder Not Working

**Problem**: Turning/pressing knob does nothing

**Solutions**:
- Verify you flashed to `ansi_encoder` variant (not `ansi`)
- Check `ENCODER_ENABLE = yes` in rules.mk
- Recompile and reflash
- Test encoder physically (might be hardware issue)

### Wrong Macro Executes

**Problem**: Pressing knob executes different macro than expected

**Solutions**:
- Turn knob multiple times to reset position
- Encoder might have skipped during rotation
- This is expected behavior - encoder tracks position, not absolute state

## Reverting to Original Firmware

If you want to go back to stock Keychron firmware:

1. Download original firmware from: https://www.keychron.com/pages/firmware-support
2. Find "Keychron V1 ANSI Encoder"
3. Flash using same process above

## Advanced: Command Line Flashing

If you prefer command line (requires QMK CLI):

```bash
# Put keyboard in bootloader mode first, then:
qmk flash -kb keychron/v1/ansi_encoder -km knob_macros
```

## VIA Configuration (Optional)

After flashing with VIA enabled:

1. Download VIA: https://www.caniusevia.com/
2. Launch VIA
3. Plug in keyboard - it should auto-detect
4. Remap keys visually (note: macro cycling stays in firmware)

**Note**: Encoder button is mapped to `EXEC_MACRO` custom keycode. VIA sees it but won't show macro details.

## Safety Notes

✓ **Always backup** your original firmware before flashing
✓ **Don't unplug** keyboard during flashing process
✓ **Use quality USB cable** - poor cables can cause flash failures
✓ **Keep firmware file** - you might need to reflash later

## Success Indicators

You've successfully flashed when:
- ✓ QMK Toolbox shows "Flashing succeeded"
- ✓ Keyboard reconnects and is recognized
- ✓ All keys work normally
- ✓ Encoder rotates and clicks
- ✓ Pressing encoder executes macros

---

## Quick Reference Card

**Enter Bootloader**:
- Unplug → Hold ESC → Plug in → Release ESC

**Flash**:
1. Open QMK Toolbox
2. Open .bin file
3. Put keyboard in bootloader
4. Click Flash

**Test**:
- Turn encoder → cycles macros
- Press encoder → executes macro

---

Need help? Check:
- QMK Discord: https://discord.gg/qmk
- Keychron Support: https://www.keychron.com/pages/contact-us
- QMK Docs: https://docs.qmk.fm/
