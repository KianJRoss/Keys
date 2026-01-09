# Python Host Software - Keychron V1 Raw HID

Python tools for communicating with the custom Keychron V1 firmware.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
cd C:\CLIPALS\python_host
pip install -r requirements.txt
```

## Tools

### 1. HID Test Tool (`hid_test.py`)

Interactive test application for validating firmware communication.

**Features:**
- Reads encoder events in real-time
- Sends LED mode/color commands
- Automatic reconnection on USB disconnect
- Demonstrates proper threading pattern

**Usage:**
```bash
python hid_test.py
```

**What it does:**
- Connects to Keychron V1 via Raw HID
- Prints all encoder events (CW, CCW, press, long-press, double-tap)
- Auto-changes LED colors based on event type:
  - Green: Clockwise rotation
  - Red: Counter-clockwise rotation
  - Blue: Button press
  - Yellow: Long-press
  - Magenta: Double-tap

### 2. Full Menu System (Coming Soon)

- Overlay UI with menu rendering
- State machine for menu navigation
- Command execution backends:
  - Volume control (pycaw)
  - Media keys (win32)
  - Voicemeeter integration
  - Window management
  - Application launcher

## Troubleshooting

### "Failed to open device"
- Verify keyboard is plugged in
- Check VID/PID in `hid_test.py` matches your keyboard
- Windows: May need HID drivers (usually automatic)
- Try unplugging and replugging USB

### No events received
- Ensure custom firmware is flashed (not stock firmware)
- Check QMK Toolbox for successful flash
- Verify encoder is working in VIA first

### "Module not found: hidapi"
- Run `pip install hidapi`
- On some systems may need `pip install hid` instead

## VID/PID Configuration

If the default VID/PID doesn't work:

1. Check Device Manager (Windows):
   - View → Devices by connection
   - Find "HID-compliant device" under your keyboard
   - Properties → Details → Hardware IDs
   - Look for `VID_XXXX&PID_YYYY`

2. Update in `hid_test.py`:
   ```python
   VENDOR_ID = 0xXXXX   # Your VID
   PRODUCT_ID = 0xYYYY  # Your PID
   ```

## Development Notes

### Threading Architecture

The HID reader uses a **blocking read pattern** for efficiency:

```python
# HID reader thread (daemon)
data = device.read(32, timeout_ms=50)  # Blocks, releases GIL

# Main thread polls queue at 60Hz
event = event_queue.get(timeout=0.1)
```

This approach:
- Minimizes CPU usage (no tight polling loops)
- Responds quickly to events (<50ms latency)
- Allows clean shutdown via threading events

### Watchdog Thread

Monitors connection status and attempts automatic reconnection every 2 seconds if disconnected.

### Queue Overflow Prevention

The event queue is unbounded by default. For production:
- Use `queue.Queue(maxsize=100)` to prevent memory buildup
- Implement queue overflow handling in reader thread

## Next Steps

1. Build overlay UI framework with proper Windows flags
2. Implement menu state machine
3. Add command execution backends
4. Create configuration system for user-defined macros
