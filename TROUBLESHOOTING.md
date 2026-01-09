# Troubleshooting Guide - Keychron V1 Command Macros

## Firmware Compilation Issues

### Error: `qmk: command not found`
**Cause:** QMK CLI not installed or not in PATH

**Solution:**
1. Open QMK MSYS terminal (not regular CMD/PowerShell)
2. Run `qmk setup` to initialize environment
3. Restart QMK MSYS terminal

---

### Error: `Keyboard 'keychron/v1/ansi_encoder' does not exist`
**Cause:** QMK firmware outdated or keyboard not in repository

**Solution:**
```bash
# Update QMK firmware
cd ~/qmk_firmware
git pull
qmk setup
```

**Alternative:** Use different keyboard path:
```bash
qmk compile -kb keychron/v1/ansi/knob -km macro
```

---

### Error: File size exceeds maximum
**Cause:** Firmware too large for flash memory

**Solution:**
Edit `firmware/rules.mk` - disable features:
```make
MOUSEKEY_ENABLE = no
CONSOLE_ENABLE = no
COMMAND_ENABLE = no
```

---

## Flashing Issues

### QMK Toolbox doesn't detect keyboard in bootloader
**Symptoms:**
- Keyboard not shown in QMK Toolbox after reset
- No "STM32 device connected" message

**Solutions:**

**1. Try different bootloader method:**
```
Method A: Space + B on plug-in
1. Unplug keyboard
2. Hold Space + B
3. Plug in USB while holding
4. Release after 2 seconds

Method B: Software reset (Fn + J + Z)
1. Hold Fn + J + Z for 4 seconds
2. Keyboard disconnects briefly

Method C: Physical reset button
1. Remove keycaps near top-right
2. Look for small reset button on PCB
3. Press with paperclip while plugged in
```

**2. Check USB cable:**
- Must be data cable (not charge-only)
- Try different USB port
- Avoid USB hubs if possible

**3. Install STM32 drivers:**
- Download from: https://www.st.com/en/development-tools/stsw-stm32102.html
- Install and restart computer

---

### Flash succeeds but keyboard doesn't work
**Symptoms:**
- QMK Toolbox shows "Flash complete"
- Keyboard doesn't respond to keypresses

**Solutions:**

**1. Reflash default firmware first:**
```bash
qmk flash -kb keychron/v1/ansi_encoder -km default
```

**2. Check if keyboard is in bootloader mode still:**
- Unplug and replug keyboard
- Wait 10 seconds for initialization

**3. Try VIA firmware:**
```bash
qmk flash -kb keychron/v1/ansi_encoder -km via
```

---

## AutoHotkey Script Issues

### Script won't run (double-click does nothing)
**Cause:** AutoHotkey not installed or wrong version

**Solution:**
1. Download AutoHotkey v2 from: https://www.autohotkey.com/
2. Install (accept defaults)
3. Restart computer
4. Try running script again

---

### Script runs but commands don't execute
**Symptoms:**
- Green H icon in system tray
- Tooltip shows command names
- But pressing knob does nothing

**Diagnostic steps:**

**1. Test execution hotkey manually:**
- Press `Ctrl+Alt+Enter` on keyboard
- If command executes → firmware issue
- If nothing happens → script issue

**2. Check for script errors:**
- Right-click tray icon → **View → Error Log**
- Look for red error messages

**3. Test command manually:**
```powershell
# Open PowerShell and test your command
notepad.exe  # Should open Notepad
code         # Should open VSCode
```

**4. Simplify command for testing:**
Edit script, change first command to:
```ahk
{
    name: "Test",
    action: () => MsgBox("It works!")
}
```
Reload script and test.

---

### Hotkeys conflict with other software
**Symptoms:**
- Commands execute in wrong application
- Different action than expected

**Solution 1 - Change hotkeys:**

Edit `firmware/keymap.c` (line ~109):
```c
// Change from F13-F16 to F20-F23
register_code(KC_F20 + current_command);
```

Edit `scripts/keychron_commands.ahk`:
```ahk
^!F20:: { ... }  // Instead of ^!F13
^!F21:: { ... }
^!F22:: { ... }
^!F23:: { ... }
```

Recompile, reflash, reload script.

**Solution 2 - Disable conflicting software:**
- Close other hotkey tools (e.g., AutoHotkey v1 scripts)
- Check gaming software (Razer Synapse, Logitech G HUB)
- Disable Windows hotkeys in Settings

---

### Script stops working after sleep/hibernate
**Cause:** AutoHotkey process terminated

**Solution:**
Add auto-restart on resume:

Edit `keychron_commands.ahk`, add at top:
```ahk
; Auto-reload on system resume
OnMessage(0x218, WM_POWERBROADCAST)
WM_POWERBROADCAST(wParam, lParam, msg, hwnd) {
    if (wParam = 0x7 || wParam = 0x8)  ; Resume events
        Reload()
}
```

---

## Encoder Behavior Issues

### Knob rotation doesn't cycle commands
**Symptoms:**
- Knob rotates but no tooltip appears
- Volume still changes instead

**Diagnostic:**

**1. Verify firmware flashed correctly:**
- Open VIA or QMK Configurator
- Check if keyboard is detected
- If not detected → reflash firmware

**2. Check AutoHotkey is running:**
- Look for green H in system tray
- If missing → double-click `keychron_commands.ahk`

**3. Test hotkeys manually:**
```
Press Ctrl+Alt+F13  → Tooltip should show "Command 0"
Press Ctrl+Alt+F14  → Tooltip should show "Command 1"
```
If tooltips work → firmware not sending hotkeys

**4. Reflash with verbose output:**
In `firmware/keymap.c`, add debug prints (requires CONSOLE_ENABLE):
```c
#ifdef CONSOLE_ENABLE
    uprintf("Encoder: command %d\n", current_command);
#endif
```

---

### Knob press doesn't execute command
**Symptoms:**
- Rotation works (tooltip changes)
- Press does nothing

**Solution:**

**1. Verify knob press is mapped:**
Check `firmware/keymap.c` line ~22:
```c
KC_EXEC,  // Make sure this is in encoder position
```

**2. Test execution hotkey:**
Press `Ctrl+Alt+Enter` manually → should execute command

**3. Check encoder press switch:**
- Encoder may have mechanical issue
- Test in VIA - assign simple key to encoder press
- If VIA doesn't register press → hardware issue

---

### Commands cycle too fast/slow
**Cause:** Encoder sensitivity

**Solution:**

Add debouncing in `firmware/keymap.c`:
```c
// Add at top
static uint16_t last_encoder_time = 0;

bool encoder_update_user(uint8_t index, bool clockwise) {
    if (index == 0) {
        // Debounce: ignore if less than 100ms since last change
        if (timer_elapsed(last_encoder_time) < 100) {
            return false;
        }
        last_encoder_time = timer_read();
        
        // Rest of encoder logic...
```

Recompile and reflash.

---

## VIA Issues

### VIA doesn't detect keyboard after flashing
**Cause:** VIA needs sideload definition or firmware issue

**Solutions:**

**1. Update VIA:**
- Download latest from https://usevia.app/
- Restart VIA completely

**2. Load keyboard definition:**
- In VIA, go to Settings → Show Design tab
- Drag and drop Keychron V1 JSON (download from Keychron website)

**3. Verify VIA_ENABLE in firmware:**
Check `firmware/rules.mk`:
```make
VIA_ENABLE = yes  # Must be present
```

**4. Reflash VIA firmware first:**
```bash
qmk flash -kb keychron/v1/ansi_encoder -km via
```
Then reflash custom firmware.

---

### VIA remapping doesn't save
**Cause:** EEPROM cleared or firmware issue

**Solution:**
1. In VIA, make changes
2. Unplug keyboard for 10 seconds
3. Plug back in
4. Check if changes persist

If issue continues:
```bash
# Reflash with EEPROM clear
qmk flash -kb keychron/v1/ansi_encoder -km macro -c
```

---

## Command Execution Issues

### Commands execute but fail
**Symptoms:**
- AutoHotkey shows execution notification
- Application doesn't open / script fails

**Diagnostic:**

**1. Test command in terminal first:**
```powershell
# Open PowerShell as Admin, test each command
C:\Path\To\Your\Script.ps1
notepad.exe
code
```

**2. Check file paths:**
- Must use full absolute paths
- Use double backslashes: `C:\\Users\\...`

**3. Check permissions:**
Some commands need admin rights:
```ahk
// Right-click script → Run as Administrator
action: () => Run("*RunAs powershell.exe -File C:\Scripts\admin_task.ps1")
```

**4. Add error handling:**
```ahk
action: () => {
    try {
        Run("your_command.exe")
    } catch Error as err {
        MsgBox("Error: " err.Message)
    }
}
```

---

### Delay between knob press and execution
**Cause:** Normal behavior (10-50ms latency)

**If delay is >500ms:**

**1. Check AutoHotkey script efficiency:**
- Avoid complex logic in `action`
- Use asynchronous operations

**2. Check system resources:**
- Task Manager → CPU/Memory usage
- Close unnecessary applications

---

## Windows-Specific Issues

### Script doesn't start on boot
**Solution:**

**1. Verify startup shortcut:**
- Press `Win + R` → `shell:startup`
- Shortcut should point to: `C:\CLIPALS\scripts\keychron_commands.ahk`

**2. Check AutoHotkey installation:**
- `.ahk` files should have green H icon
- If not → reinstall AutoHotkey v2

**3. Create scheduled task instead:**
```
Task Scheduler → Create Basic Task
Trigger: At log on
Action: Start program → C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe
Arguments: C:\CLIPALS\scripts\keychron_commands.ahk
```

---

## General Debugging Workflow

1. **Isolate the issue:**
   - Firmware → Test with VIA (does encoder work?)
   - Script → Test hotkeys manually (does `Ctrl+Alt+Enter` work?)
   - Command → Run in terminal first (does it execute?)

2. **Check logs:**
   - QMK Toolbox → Flash output
   - AutoHotkey → Error log (tray icon → View)
   - Windows Event Viewer → Application logs

3. **Test components individually:**
   - Flash default firmware → keyboard works?
   - Run simple AutoHotkey script → hotkeys work?
   - Combine both → still works?

4. **Reset to known-good state:**
   ```bash
   # Flash original VIA firmware
   qmk flash -kb keychron/v1/ansi_encoder -km via
   
   # Use minimal AutoHotkey script
   ^!Enter:: MsgBox("Test")
   ```

5. **Build complexity incrementally:**
   - Start with 1 command
   - Add encoder cycling
   - Add more commands
   - Add advanced features

---

## Getting Help

**Firmware issues:**
- QMK Discord: https://discord.gg/qmk
- r/olkb subreddit: https://reddit.com/r/olkb

**AutoHotkey issues:**
- AHK Forum: https://www.autohotkey.com/boards/
- r/AutoHotkey: https://reddit.com/r/AutoHotkey

**Keychron hardware:**
- Keychron support: support@keychron.com
- r/Keychron: https://reddit.com/r/Keychron

---

## Emergency Recovery

### Keyboard completely bricked
**Extremely rare, but if keyboard won't respond at all:**

1. **Flash original firmware:**
   - Download from: https://www.keychron.com/pages/firmware-and-json-files
   - Flash with QMK Toolbox in bootloader mode

2. **Factory reset:**
   - Unplug keyboard
   - Hold `Esc + Space + B`
   - Plug in while holding
   - Release after 5 seconds

3. **Contact Keychron support:**
   - Warranty may cover firmware issues
   - They can provide recovery firmware

---

## Preventive Measures

1. **Backup working firmware:**
   ```bash
   # After successful flash
   cp ~/qmk_firmware/.build/*.bin ~/backups/
   ```

2. **Test on non-critical system first:**
   - Use VM or secondary computer
   - Verify everything works before daily driver

3. **Keep original firmware:**
   - Download from Keychron before first flash
   - Store in safe location

4. **Version control AutoHotkey script:**
   ```bash
   cd C:\CLIPALS
   git init
   git add scripts/keychron_commands.ahk
   git commit -m "Working configuration"
   ```

5. **Document your changes:**
   - Comment your code
   - Keep changelog of modifications
