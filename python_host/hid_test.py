"""
Keychron V1 Raw HID Test Tool
==============================

Tests bidirectional Raw HID communication with custom firmware:
- Reads encoder events (CW, CCW, press, long-press, double-tap)
- Sends LED commands (mode, color)
- Implements reconnection logic
- Demonstrates proper threading pattern

Requirements:
    pip install hidapi

Usage:
    python hid_test.py
"""

import hid
import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional

# ========================================
# KEYCHRON V1 USB IDENTIFIERS
# ========================================
# Note: These are Keychron's standard VID/PID
# Verify with VIA or Device Manager if connection fails
VENDOR_ID = 0x3434   # Keychron
PRODUCT_ID = 0x0311  # V1 ANSI Encoder

# ========================================
# PROTOCOL CONSTANTS
# ========================================

# Device -> Host Event Marker
HID_EVT_MARKER = 0x01

# Event Types
EVT_ENCODER_CW = 0x01
EVT_ENCODER_CCW = 0x02
EVT_ENCODER_PRESS = 0x03
EVT_ENCODER_RELEASE = 0x04
EVT_ENCODER_LONG = 0x05
EVT_ENCODER_DOUBLE = 0x06

EVENT_NAMES = {
    EVT_ENCODER_CW: "CW",
    EVT_ENCODER_CCW: "CCW",
    EVT_ENCODER_PRESS: "PRESS",
    EVT_ENCODER_RELEASE: "RELEASE",
    EVT_ENCODER_LONG: "LONG_PRESS",
    EVT_ENCODER_DOUBLE: "DOUBLE_TAP"
}

# Host -> Device Command Marker
HID_CMD_MARKER = 0x02

# Command Types
CMD_SET_MODE = 0x10
CMD_SET_COLOR = 0x11

# LED Modes
MODE_DEFAULT = 0
MODE_VOLUME = 1
MODE_MEDIA = 2
MODE_VOICEMEETER = 3
MODE_WINDOW_MGMT = 4
MODE_APP_LAUNCH = 5

MODE_NAMES = {
    MODE_DEFAULT: "DEFAULT",
    MODE_VOLUME: "VOLUME",
    MODE_MEDIA: "MEDIA",
    MODE_VOICEMEETER: "VOICEMEETER",
    MODE_WINDOW_MGMT: "WINDOW_MGMT",
    MODE_APP_LAUNCH: "APP_LAUNCH"
}

# ========================================
# DATA STRUCTURES
# ========================================

@dataclass
class EncoderEvent:
    """Represents a parsed encoder event"""
    event_type: int
    encoder_id: int
    value: int
    timestamp: int
    
    def __str__(self):
        event_name = EVENT_NAMES.get(self.event_type, f"UNKNOWN({self.event_type:02X})")
        return f"[{self.timestamp:5d}ms] Encoder {self.encoder_id}: {event_name} (val={self.value})"


# ========================================
# HID COMMUNICATION CLASS
# ========================================

class KeychronV1HID:
    """Handles Raw HID communication with Keychron V1 firmware"""
    
    def __init__(self):
        self.device: Optional[hid.device] = None
        self.event_queue = queue.Queue()
        self.running = False
        self.reader_thread: Optional[threading.Thread] = None
        self.watchdog_thread: Optional[threading.Thread] = None
        
    def connect(self) -> bool:
        """Attempt to connect to the keyboard"""
        try:
            # Find the Raw HID interface (usage_page 0xFF60)
            devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
            raw_hid_path = None

            for dev in devices:
                # Look for the vendor-specific usage page (Raw HID)
                if dev['usage_page'] == 0xFF60:
                    raw_hid_path = dev['path']
                    break

            if not raw_hid_path:
                print("[ERROR] Raw HID interface not found!")
                print("Available interfaces:")
                for dev in devices:
                    print(f"  Interface {dev['interface_number']}: Usage Page 0x{dev['usage_page']:04X}")
                return False

            self.device = hid.device()
            self.device.open_path(raw_hid_path)
            self.device.set_nonblocking(0)  # Use blocking reads

            # Get device info
            manufacturer = self.device.get_manufacturer_string()
            product = self.device.get_product_string()
            print(f"[OK] Connected to: {manufacturer} {product}")
            print(f"  VID: 0x{VENDOR_ID:04X}, PID: 0x{PRODUCT_ID:04X}, Usage Page: 0xFF60")
            return True

        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            self.device = None
            return False
    
    def disconnect(self):
        """Close the HID device"""
        if self.device:
            try:
                self.device.close()
                print("[OK] Disconnected")
            except:
                pass
            self.device = None
    
    def send_command(self, sub_command: int, arg1: int = 0, arg2: int = 0, arg3: int = 0):
        """Send a command to the keyboard"""
        if not self.device:
            print("[WARN] Cannot send command: Not connected")
            return False
        
        try:
            packet = [0] * 32
            packet[0] = HID_CMD_MARKER
            packet[1] = sub_command
            packet[2] = arg1
            packet[3] = arg2
            packet[4] = arg3
            
            # HID write on Windows requires report ID as first byte (0x00 for Raw HID)
            self.device.write([0x00] + packet)
            return True
            
        except Exception as e:
            print(f"[WARN] Send failed: {e}")
            return False
    
    def set_led_mode(self, mode: int):
        """Set the LED mode"""
        mode_name = MODE_NAMES.get(mode, f"UNKNOWN({mode})")
        print(f"--> Setting LED mode: {mode_name}")
        return self.send_command(CMD_SET_MODE, mode)
    
    def set_led_color(self, r: int, g: int, b: int):
        """Set the LED color (0-255 RGB)"""
        print(f"--> Setting LED color: RGB({r}, {g}, {b})")
        return self.send_command(CMD_SET_COLOR, r, g, b)
    
    def parse_event(self, data: list) -> Optional[EncoderEvent]:
        """Parse incoming HID packet into EncoderEvent"""
        if not data or len(data) < 6:
            return None
        
        # Check for our event marker
        if data[0] != HID_EVT_MARKER:
            return None
        
        event_type = data[1]
        encoder_id = data[2]
        value = data[3]
        timestamp = data[4] | (data[5] << 8)
        
        return EncoderEvent(event_type, encoder_id, value, timestamp)
    
    def reader_worker(self):
        """HID reader thread - blocks on reads with timeout"""
        print("--> HID reader thread started")
        
        while self.running:
            try:
                if not self.device:
                    time.sleep(0.1)
                    continue
                
                # Blocking read with 50ms timeout (releases GIL)
                data = self.device.read(32, timeout_ms=50)
                
                if data:
                    event = self.parse_event(data)
                    if event:
                        self.event_queue.put(event)
                        
            except Exception as e:
                print(f"[WARN] Read error: {e}")
                self.disconnect()
                time.sleep(1)
        
        print("--> HID reader thread stopped")
    
    def watchdog_worker(self):
        """Watchdog thread - attempts reconnection if disconnected"""
        print("--> Watchdog thread started")
        
        while self.running:
            if not self.device:
                print("--> Attempting reconnection...")
                self.connect()
            time.sleep(2)  # Check every 2 seconds
        
        print("--> Watchdog thread stopped")
    
    def start(self):
        """Start the HID reader and watchdog threads"""
        if self.running:
            print("[WARN] Already running")
            return
        
        self.running = True
        
        # Start reader thread
        self.reader_thread = threading.Thread(target=self.reader_worker, daemon=True)
        self.reader_thread.start()
        
        # Start watchdog thread
        self.watchdog_thread = threading.Thread(target=self.watchdog_worker, daemon=True)
        self.watchdog_thread.start()
        
        print("[OK] HID system started")
    
    def stop(self):
        """Stop all threads and disconnect"""
        print("--> Stopping HID system...")
        self.running = False
        
        if self.reader_thread:
            self.reader_thread.join(timeout=2)
        
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=2)
        
        self.disconnect()
        print("[OK] HID system stopped")
    
    def get_event(self, timeout: float = 0.1) -> Optional[EncoderEvent]:
        """Get next event from queue (non-blocking with timeout)"""
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None


# ========================================
# TEST APPLICATION
# ========================================

def test_interactive():
    """Interactive test application"""
    print("=" * 60)
    print("Keychron V1 Raw HID Test Tool")
    print("=" * 60)
    print()
    
    hid_system = KeychronV1HID()
    
    # Initial connection
    if not hid_system.connect():
        print("\nMake sure:")
        print("  1. Keyboard is plugged in")
        print("  2. Custom firmware is flashed")
        print("  3. VID/PID are correct for your variant")
        return
    
    # Start threads
    hid_system.start()
    
    print()
    print("Commands:")
    print("  1-5: Set LED mode (1=Volume, 2=Media, 3=VM, 4=Window, 5=AppLaunch)")
    print("  r/g/b: Set LED color (red/green/blue)")
    print("  q: Quit")
    print()
    print("Waiting for encoder events... (rotate knob or press)")
    print("-" * 60)
    
    current_mode = MODE_DEFAULT
    
    try:
        while True:
            # Check for keyboard input (non-blocking would be better, but kept simple)
            # In real app, use msvcrt.kbhit() on Windows or select() on Unix
            
            # Process encoder events
            event = hid_system.get_event(timeout=0.1)
            if event:
                print(event)
                
                # Example: Auto-change LED color on different events
                if event.event_type == EVT_ENCODER_CW:
                    hid_system.set_led_color(0, 255, 0)  # Green on CW
                elif event.event_type == EVT_ENCODER_CCW:
                    hid_system.set_led_color(255, 0, 0)  # Red on CCW
                elif event.event_type == EVT_ENCODER_PRESS:
                    hid_system.set_led_color(0, 0, 255)  # Blue on press
                elif event.event_type == EVT_ENCODER_LONG:
                    hid_system.set_led_color(255, 255, 0)  # Yellow on long-press
                elif event.event_type == EVT_ENCODER_DOUBLE:
                    hid_system.set_led_color(255, 0, 255)  # Magenta on double-tap
            
            # Simple command processing (blocks, not ideal but works for testing)
            # Use input() would block - in real app use proper async input
            
    except KeyboardInterrupt:
        print("\n\n--> Interrupted by user")
    
    finally:
        hid_system.stop()
        print("\nTest completed.")


if __name__ == "__main__":
    test_interactive()
