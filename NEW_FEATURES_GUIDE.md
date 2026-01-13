# New Features Installation & Usage Guide

## 🎉 Features Implemented

Three major features have been added to your Keychron menu system:

1. **Virtual Desktop Switcher** - Navigate Windows 10/11 virtual desktops
2. **Display Control** - Enhanced monitor management (brightness, modes, toggle)
3. **Context-Aware Commands** - App-specific shortcuts that appear automatically

---

## 📦 Installation

### Step 1: Install New Dependencies

```bash
cd C:\Keyboard\Keys\python_host
pip install psutil>=5.9.0
```

### Step 2: Verify Plugin Files

Make sure these files exist:
- `python_host/plugins/virtual_desktops.py` ✓
- `python_host/plugins/display_control.py` ✓
- `python_host/plugins/context_commands.py` ✓
- `python_host/context_aware.py` ✓

### Step 3: Restart the Application

```bash
cd C:\Keyboard\Keys\python_host
python keychron_app.py
```

The plugins will auto-load at startup. Check the log for confirmation:
```
Loading plugins from plugins...
  + Registered plugin command: Virtual Desktops
  + Registered plugin command: Display Control
  + Registered plugin command: Context Commands
```

---

## 🖥️ Feature 1: Virtual Desktop Switcher

### What It Does
Allows you to navigate between Windows virtual desktops using your encoder knob.

### How to Use

**From Normal Mode:**
1. **Rotate knob** to "Virtual Desktops" command
2. **Press knob** to enter Virtual Desktop mode

**In Virtual Desktop Mode:**
- **Rotate CW**: Switch to next desktop →
- **Rotate CCW**: Switch to previous desktop ←
- **Press**: Show desktop action menu

**Desktop Action Menu:**
- Move Window → (Move active window to next desktop)
- Move Window ← (Move active window to previous desktop)
- New Desktop (Create a new virtual desktop)
- Close Desktop (Close current desktop)

### Windows Shortcuts Used
The plugin uses Windows built-in shortcuts:
- `Win+Ctrl+Left/Right` - Switch desktops
- `Win+Ctrl+Shift+Left/Right` - Move window
- `Win+Ctrl+D` - New desktop
- `Win+Ctrl+F4` - Close desktop

### Tips
- Virtual desktops must be enabled in Windows 10/11 (they are by default)
- Create your first desktop with `Win+Ctrl+D` if you haven't already
- Works great for separating Work/Personal/Gaming workspaces

---

## 🖥️ Feature 2: Display Control

### What It Does
Comprehensive monitor management including brightness, display modes, and individual monitor toggling.

### How to Use

**From Normal Mode:**
1. **Rotate knob** to "Display Control" command
2. **Press knob** to enter Display Control menu

**Display Control Menu Options:**

#### 1. Brightness Control
- **Rotate**: Adjust brightness ±5%
- **Press**: Reset to 50%
- Shows progress bar with current percentage
- Works best on laptops (external monitors may vary)

#### 2. Display Mode
- **Rotate**: Select mode
  - 🖥️ PC Only (disable external monitors)
  - 👥 Duplicate (mirror displays)
  - 🔗 Extend (desktop across monitors) [Default]
  - 📺 Second Only (disable laptop screen)
- **Press**: Apply mode and exit
- Uses Windows display projection (Win+P)

#### 3. Toggle Monitor
- **Rotate**: Select monitor to toggle
- **Press**: Enable/disable selected monitor
- Shows monitor status [ON/OFF]
- Useful for gaming or presentations

### Comparison to Game Mode
Your existing `game_mode.py` disables the bottom two monitors specifically. Display Control gives you:
- Individual monitor selection
- Brightness control
- Display mode switching
- More flexible control

### Tips
- Brightness control uses WMI (works on most laptops)
- External monitor brightness requires DDC/CI support (varies by monitor)
- Display modes take 1-2 seconds to apply
- Monitor toggle saves previous settings for re-enabling

---

## 📱 Feature 3: Context-Aware Commands

### What It Does
Automatically detects your active application and provides relevant shortcuts via the encoder.

### How to Use

**From Normal Mode:**
1. **Rotate knob** to "Context Commands"
2. **Press knob** to see app-specific commands

**Supported Applications:**

#### 🌐 Web Browsers (Chrome, Firefox, Edge, Opera, Brave)
- **New Tab** - Opens new tab (Ctrl+T)
- **Close Tab** - Closes current tab (Ctrl+W)
- **Reopen Tab** - Reopens last closed tab (Ctrl+Shift+T)
- **Next Tab** - Switch to next tab
- **Previous Tab** - Switch to previous tab

#### 💻 Code Editors (VS Code, Cursor, PyCharm, Sublime, etc.)
- **Toggle Comment** - Comment/uncomment line (Ctrl+/)
- **Format Code** - Auto-format document (Shift+Alt+F)
- **Find in Files** - Search across project (Ctrl+Shift+F)
- **Run/Debug** - Start debugging (F5)

#### 🎮 Discord
- **Toggle Mute** - Mute/unmute mic (Ctrl+Shift+M)
- **Toggle Deafen** - Deafen/undeafen (Ctrl+Shift+D)

### How It Works
1. System detects your foreground window every 500ms
2. Matches against registered context providers
3. Shows relevant commands in the encoder menu
4. Commands execute keyboard shortcuts for that app

### Adding Your Own Context Commands

You can extend the system by editing `python_host/context_aware.py`:

```python
class MyAppContextProvider(ContextProvider):
    """Commands for My Custom App"""

    def matches(self, context: AppContext) -> bool:
        return context.process_name == 'myapp.exe'

    def get_commands(self, context: AppContext) -> List[ContextCommand]:
        def my_action():
            # Execute your action here
            pass

        return [
            ContextCommand("My Action", "Description", my_action, "🔥")
        ]

    def get_priority(self) -> int:
        return 10

# Register it
context_manager.register_provider(MyAppContextProvider())
```

### Tips
- Context detection is rate-limited to avoid performance impact
- If no context commands are available, you'll see a brief notification
- Commands stay active as long as the app is in focus
- Perfect for frequently-used app shortcuts

---

## 🎮 Testing Checklist

### Virtual Desktop Switcher
- [ ] Create a new virtual desktop (`Win+Ctrl+D`)
- [ ] Rotate encoder to "Virtual Desktops" and press
- [ ] Rotate knob CW/CCW to switch desktops
- [ ] Press knob to see action menu
- [ ] Try "Move Window →" to move a window between desktops
- [ ] Try "New Desktop" to create another desktop
- [ ] Try "Close Desktop" to remove a desktop

### Display Control
- [ ] Rotate encoder to "Display Control" and press
- [ ] Select "Brightness" and adjust
- [ ] Verify progress bar updates
- [ ] Select "Display Mode" and try "Extend" mode
- [ ] If you have multiple monitors, select "Toggle Monitor"
- [ ] Verify monitor can be disabled and re-enabled

### Context Commands
- [ ] Open Chrome/Edge/Firefox
- [ ] Rotate to "Context Commands" and press
- [ ] Verify you see browser-specific commands
- [ ] Try "New Tab" - should open a new tab
- [ ] Try "Close Tab" - should close the tab
- [ ] Open VS Code or Cursor
- [ ] Enter "Context Commands" again
- [ ] Verify you see code editor commands
- [ ] Try "Toggle Comment" on a line of code

---

## 🐛 Troubleshooting

### Virtual Desktops Not Working
**Problem**: Desktops don't switch when rotating

**Solutions:**
1. Verify virtual desktops are enabled (Win+Tab should show desktops bar)
2. Create at least one extra desktop first
3. Check keyboard shortcuts work manually:
   - `Win+Ctrl+Right` should switch desktops
4. Run as Administrator if shortcuts are blocked

### Brightness Control Not Working
**Problem**: Brightness doesn't change

**Solutions:**
1. **Laptops**: Should work via WMI
2. **External monitors**: Requires DDC/CI support
   - Check monitor OSD settings for DDC/CI
   - Some monitors don't support brightness control
3. Try manual PowerShell test:
   ```powershell
   (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)
   ```

### Display Modes Not Applying
**Problem**: Display mode doesn't change

**Solutions:**
1. Wait 2-3 seconds for Windows to apply
2. Try manual shortcut: `Win+P` then arrow keys + Enter
3. Check Windows display settings aren't locked by policy
4. Restart application with Administrator rights

### Context Commands Not Appearing
**Problem**: "Context Commands" shows "No commands available"

**Solutions:**
1. Verify `psutil` is installed: `pip install psutil`
2. Check application is running (Task Manager)
3. Check process name in context_aware.py matches your app
4. Look for errors in log: `python_host/logs/keychron_app.log`
5. Add logging to see detected process:
   ```python
   logger.info(f"Detected: {context.process_name}")
   ```

### Plugin Not Loading
**Problem**: Commands don't appear in the menu

**Solutions:**
1. Check log file for errors: `python_host/logs/keychron_app.log`
2. Verify plugin file is in `python_host/plugins/` directory
3. Check Python syntax errors: `python -m py_compile plugins/virtual_desktops.py`
4. Restart the application completely
5. Try manually importing: `python -c "import plugins.virtual_desktops"`

---

## 📊 Command Count Update

After adding these plugins, your command count increases from **8 to 11**.

**Update firmware if needed:**
If you have more than 4 commands now, you'll need to update the firmware to support more:

1. Edit `firmware/keymap.c`:
   ```c
   #define NUM_COMMANDS 11  // Increase from 4
   ```

2. Recompile and flash firmware:
   ```bash
   setup_qmk.bat
   ```

3. Flash with QMK Toolbox

**Alternative**: Keep 4 commands max by removing less-used commands like "Launch Playnite" or using submenus.

---

## 🎨 UI Improvements

All three features integrate with the enhanced UI:

### Virtual Desktops
- Title: "🖥️ Virtual Desktops"
- Icons: ← ▼ →
- Subtitle guidance for actions

### Display Control
- Progress bar for brightness
- Descriptive icons (☀️, 🖥️, etc.)
- Status indicators [ON/OFF]

### Context Commands
- App-specific emojis (🌐 🎮 💻)
- Dynamic title showing app name
- Command descriptions

---

## 🚀 What's Next?

### Possible Enhancements

1. **Virtual Desktop Names**
   - Currently desktops are numbered
   - Could show custom names if Windows API allows

2. **Display Profiles**
   - Save monitor configurations
   - Quick switch between work/gaming setups

3. **More Context Providers**
   - Spotify (currently playing, like/skip)
   - Outlook (new email, calendar)
   - File Explorer (folder shortcuts)
   - Games (game-specific macros)

4. **Smart Context Detection**
   - Learn most-used commands per app
   - Suggest commands based on time of day
   - Profile-based context switching

---

## 📝 Summary

You now have:

✅ **11 total commands** (was 8)
✅ **Virtual desktop navigation** with window management
✅ **Complete display control** (brightness, modes, toggle)
✅ **Context-aware shortcuts** for browsers, editors, Discord

All features are plugin-based and can be:
- Customized in their plugin files
- Disabled by removing from `plugins/` folder
- Extended with new functionality

Enjoy your enhanced keyboard! 🎹✨
