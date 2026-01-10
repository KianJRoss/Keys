# Plugin Setup Guide

## What's New

### System Tray Icon
Your Keychron app now runs in the system tray! Look for the keyboard icon in your taskbar notification area.

**Features:**
- Right-click the tray icon for menu options
- Show Status - Check current mode and Voicemeeter connection
- Toggle LED Feedback - Control LED features
- Quit - Exit the application

**Requirements:**
- `pystray` - Already installed ✓
- `Pillow` - Already installed ✓

---

### App Launcher Plugin

Launch your favorite apps directly from the keyboard knob!

**Apps Configured:**
1. **Launch Cursor** - Opens Cursor code editor
   - Path: `C:\Program Files\cursor\Cursor.exe`

2. **Launch Playnite** - Opens Playnite in fullscreen with admin rights
   - Path: `%LOCALAPPDATA%\Playnite\Playnite.FullscreenApp.exe`

3. **Launch Opera GX** - Opens Opera GX browser
   - Path: `%LOCALAPPDATA%\Programs\Opera GX\launcher.exe`

---

## How to Use

1. **Start the app:**
   ```bash
   cd C:\Keyboard\Keys\python_host
   python keychron_app.py
   ```

2. **Look for the tray icon** in your taskbar (bottom-right)

3. **Rotate the knob** to cycle through menu options:
   - Volume Control
   - Voicemeeter Control
   - Media Controls
   - Theme Selector
   - Window Manager
   - **Launch Cursor** ← NEW!
   - **Launch Playnite** ← NEW!
   - **Launch Opera GX** ← NEW!

4. **Press the knob** to activate the selected option

---

## Customization

### Add More Apps

Edit `plugins/app_launcher.py` to add more applications:

```python
APP_PATHS = {
    "myapp": r"C:\Path\To\YourApp.exe"
}

def launch_myapp():
    path = find_app_path("myapp")
    if path:
        subprocess.Popen([path], shell=True)

# Add to get_commands():
{
    "name": "Launch MyApp",
    "description": "Open My Application",
    "callback": launch_myapp
}
```

### Create New Plugins

Create a new Python file in `plugins/` directory:

```python
# plugins/my_plugin.py

def my_function():
    print("Hello from my plugin!")

def get_commands():
    return [
        {
            "name": "My Command",
            "description": "Does something cool",
            "callback": my_function
        }
    ]
```

The plugin will automatically load on next startup!

---

## Troubleshooting

### Tray icon not showing
- Check if `pystray` and `Pillow` are installed
- The app logs will show "Tray icon unavailable" if dependencies are missing

### App won't launch
- Check the console output for path errors
- Update paths in `plugins/app_launcher.py`
- Use the full path to the .exe file

### Admin rights for Playnite
- Playnite launches with admin rights using PowerShell
- You may see a UAC prompt - click "Yes" to allow

---

## Files Created

- `python_host/tray_icon.py` - System tray icon implementation
- `python_host/plugins/app_launcher.py` - App launcher plugin
- `python_host/requirements.txt` - Updated with new dependencies

## Files Modified

- `python_host/keychron_app.py` - Integrated tray icon
