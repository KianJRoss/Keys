# Quick Reference - Keychron V1 Command Macros

## File Locations

| File | Purpose | When to Edit |
|------|---------|--------------|
| `firmware/keymap.c` | QMK firmware logic | Change hotkeys, add more commands (requires reflash) |
| `firmware/rules.mk` | Build configuration | Rarely (already configured) |
| `scripts/keychron_commands.ahk` | Command definitions | **EDIT THIS to change what commands do** |
| `docs/BUILD_AND_FLASH.md` | Setup instructions | Reference only |

---

## Common Tasks

### Change what a command does
1. Open `scripts/keychron_commands.ahk` in any text editor
2. Find the `commands` array (around line 16)
3. Edit the `action` field:
   ```ahk
   action: () => Run("your_program.exe")
   ```
4. Save file
5. Right-click AutoHotkey tray icon → **Reload Script**

**No firmware reflash needed!**

---

### Add more commands (beyond 4)

1. Edit `firmware/keymap.c`:
   ```c
   #define NUM_COMMANDS 8  // Change from 4
   ```

2. Recompile and reflash firmware (see BUILD_AND_FLASH.md)

3. Edit `scripts/keychron_commands.ahk`:
   - Add more command objects to array
   - Add hotkey handlers: `^!F17::`, `^!F18::`, etc.

4. Reload AutoHotkey script

---

### Change hotkeys (not recommended)

If you must change from `Ctrl+Alt+F13-F16`:

1. **Firmware:** Edit `firmware/keymap.c`
   - Find encoder rotation handler (~line 109)
   - Change `KC_F13 + current_command` to your key
   
2. **Script:** Edit `scripts/keychron_commands.ahk`
   - Change `^!F13::` etc. to match firmware

3. Recompile, reflash, and reload script

---

## Hotkey Reference

| Action | Hotkey | Sent By |
|--------|--------|---------|
| Command 0 selected | `Ctrl+Alt+F13` | Firmware |
| Command 1 selected | `Ctrl+Alt+F14` | Firmware |
| Command 2 selected | `Ctrl+Alt+F15` | Firmware |
| Command 3 selected | `Ctrl+Alt+F16` | Firmware |
| Execute command | `Ctrl+Alt+Enter` | Firmware |

**AutoHotkey syntax:**
- `^` = Ctrl
- `!` = Alt
- `+` = Shift
- `#` = Win

---

## AutoHotkey Action Examples

### Launch application
```ahk
action: () => Run("notepad.exe")
action: () => Run("code")  // VSCode
action: () => Run("chrome.exe")
```

### Open file/folder
```ahk
action: () => Run("C:\MyFolder\document.txt")
action: () => Run("explorer.exe C:\Projects")
```

### Run PowerShell command
```ahk
action: () => Run("powershell.exe -Command 'Get-Process'")
action: () => Run("powershell.exe -File C:\Scripts\backup.ps1")
```

### Run batch script
```ahk
action: () => Run("C:\Scripts\deploy.bat")
```

### Open URL
```ahk
action: () => Run("https://github.com")
```

### Multiple commands in sequence
```ahk
action: () => {
    Run("notepad.exe")
    Sleep(500)  // Wait 500ms
    Send("Hello World")
}
```

### Send keypresses
```ahk
action: () => Send("^c")  // Ctrl+C
action: () => Send("{F5}")  // Press F5
```

### Show notification
```ahk
action: () => MsgBox("Task completed!")
```

---

## Workflow

```
┌─────────────┐
│ Rotate Knob │ → Firmware cycles state → Sends Ctrl+Alt+F13-F16
└─────────────┘                                     ↓
                                          AutoHotkey updates selection
                                          Shows tooltip notification

┌─────────────┐
│ Press Knob  │ → Firmware sends Ctrl+Alt+Enter
└─────────────┘                                     ↓
                                          AutoHotkey executes action
                                          Shows confirmation tooltip
```

---

## Debugging

### Check if AutoHotkey is running
- Look for green **H** icon in system tray
- If missing: Double-click `scripts/keychron_commands.ahk`

### Test individual hotkey
1. Press `Ctrl+Alt+Enter` manually on keyboard
2. If command executes → firmware is working
3. If nothing happens → AutoHotkey script has issue

### View AutoHotkey errors
- Right-click tray icon → **View → Error Log**
- Check for syntax errors in script

### Test command manually
Before adding to script, test in PowerShell/CMD:
```powershell
# Test if command works
notepad.exe
powershell -File C:\Scripts\test.ps1
```

---

## System Tray Menu

Right-click AutoHotkey icon:
- **Current Command** - Shows last selected (info only)
- **Reload Script** - Apply changes without restarting Windows
- **Exit** - Stop command handler

---

## When You Need to Reflash

**Reflash required:**
- Change number of commands
- Modify hotkeys
- Update firmware logic
- Fix firmware bugs

**Reflash NOT required:**
- Change command actions
- Rename commands
- Add/remove tooltip notifications
- Modify script logic

---

## Performance Notes

- **Latency:** ~10ms from knob press to command execution
- **Rotation speed:** No limit, cycles as fast as you rotate
- **Conflicts:** Ensure no other app uses `Ctrl+Alt+F13-F16`

---

## VIA Limitations

VIA **cannot**:
- Configure encoder behavior (use firmware)
- See or modify the 4 macro commands (use AutoHotkey script)

VIA **can:**
- Remap all regular keys
- Change RGB settings
- Configure function layer

---

## Command Ideas

- Launch terminal in specific project directory
- Git commit and push
- Lock computer
- Toggle mic mute
- Start/stop screen recording
- Open SSH session
- Run build script
- Toggle VPN
- Backup files
- Send Discord message
- Control smart home devices (via script)
- Take screenshot to clipboard

---

## Support

**Firmware issues:**
- Check QMK documentation: https://docs.qmk.fm/
- Keychron support: https://www.keychron.com/pages/support

**AutoHotkey issues:**
- AHK documentation: https://www.autohotkey.com/docs/v2/
- Test commands manually before adding to script

**This implementation:**
- All files are in `C:\CLIPALS\` with full source code
- Modify freely to fit your workflow
