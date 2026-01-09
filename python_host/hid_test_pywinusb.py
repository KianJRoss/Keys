"""
Keychron V1 Raw HID Test Tool (Windows - pywinusb version)
===========================================================

Tests bidirectional Raw HID communication with custom firmware.

Requirements:
    pip install pywinusb

Usage:
    python hid_test_pywinusb.py
"""

import pywinusb.hid as hid
import time
from dataclasses import dataclass
from typing import Optional
import threading
import queue

# ========================================
# KEYCHRON V1 USB IDENTIFIERS
# ========================================
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
    """Handles Raw HID communication with Keychron V1 firmware using pywinusb"""
    
    def __init__(self):
        self.device: Optional[hid.HidDevice] = None
        self.event_queue = queue.Queue()
        self.running = False
        
    def find_raw_hid_device(self):
        """Find the Raw HID interface (not keyboard or consumer control)"""
        # Get all Keychron V1 devices
        all_devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()
        
        if not all_devices:
            print(f"[ERR] No devices found with VID=0x{VENDOR_ID:04X}, PID=0x{PRODUCT_ID:04X}")
            return None
        
        print(f"Found {len(all_devices)} HID interface(s) for Keychron V1:")
        
        # Try to find Raw HID interface
        # Raw HID typically has usage_page 0xFF60 or similar vendor-defined page
        for idx, device in enumerate(all_devices):
            print(f"  [{idx}] Path: {device.device_path}")
            
            # Open and check reports
            device.open()
            
            # Check output reports (for sending commands)
            out_reports = device.find_output_reports()
            
            if out_reports:
                print(f"      Has output reports: {len(out_reports)}")
                # Try this device
                return device
        
        # If no device with output reports found, use the first one
        print(f"\nUsing first device (may need manual selection)")
        all_devices[0].open()
        return all_devices[0]
    
    def connect(self) -> bool:
        """Attempt to connect to the keyboard"""
        try:
            self.device = self.find_raw_hid_device()
            
            if not self.device:
                return False
            
            # Set up read callback
            self.device.set_raw_data_handler(self.on_data_received)
            
            manufacturer = self.device.vendor_name
            product = self.device.product_name
            print(f"[OK] Connected to: {manufacturer} {product}")
            print(f"  VID: 0x{VENDOR_ID:04X}, PID: 0x{PRODUCT_ID:04X}")
            return True
            
        except Exception as e:
            print(f"[ERR] Connection failed: {e}")
            self.device = None
            return False
    
    def on_data_received(self, data):
        """Callback for incoming HID data"""
        # pywinusb returns a list including report ID as first byte
        # data[0] is report ID (usually 0 for Raw HID)
        # data[1:] is the actual 32-byte packet
        
        if len(data) < 33:  # report ID + 32 bytes
            return
        
        # Parse event (skip report ID)
        packet = data[1:33]
        event = self.parse_event(packet)
        if event:
            self.event_queue.put(event)
    
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
            print("[ERR] Cannot send command: Not connected")
            return False
        
        try:
            # Create 32-byte packet
            packet = [0] * 33  # report ID + 32 bytes
            packet[0] = 0x00  # Report ID
            packet[1] = HID_CMD_MARKER
            packet[2] = sub_command
            packet[3] = arg1
            packet[4] = arg2
            packet[5] = arg3
            
            # Get output report
            out_reports = self.device.find_output_reports()
            if not out_reports:
                print("[ERR] No output reports found")
                return False
            
            # Send packet
            out_reports[0].set_raw_data(packet)
            out_reports[0].send()
            
            return True
            
        except Exception as e:
            print(f"[ERR] Send failed: {e}")
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
    
    def start(self):
        """Start the HID system"""
        if not self.device:
            print("[ERR] Not connected")
            return False
        
        self.running = True
        print("[OK] HID system started (receiving events)")
        return True
    
    def stop(self):
        """Stop and disconnect"""
        print("--> Stopping HID system...")
        self.running = False
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
    print("Keychron V1 Raw HID Test Tool (pywinusb)")
    print("=" * 60)
    print()
    
    hid_system = KeychronV1HID()
    
    # Initial connection
    if not hid_system.connect():
        print("\nMake sure:")
        print("  1. Keyboard is plugged in")
        print("  2. Custom firmware is flashed")
        print("  3. VID/PID are correct (check list_devices_winusb.py)")
        return
    
    # Start system
    if not hid_system.start():
        return
    
    print()
    print("Commands:")
    print("  1-5: Set LED mode (1=Volume, 2=Media, 3=VM, 4=Window, 5=AppLaunch)")
    print("  r/g/b: Set LED color (red/green/blue)")
    print("  Ctrl+C: Quit")
    print()
    print("Waiting for encoder events... (rotate knob or press)")
    print("-" * 60)
    
    try:
        while True:
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
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n\n--> Interrupted by user")
    
    finally:
        hid_system.stop()
        print("\nTest completed.")


if __name__ == "__main__":
    test_interactive()
