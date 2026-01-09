"""
Simple HID test - just try to receive data from Keychron V1
"""
import pywinusb.hid as hid
import time

VENDOR_ID = 0x3434
PRODUCT_ID = 0x0311

print("Looking for Keychron V1...")

# Find all devices
all_devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()

if not all_devices:
    print("ERROR: No Keychron V1 found!")
    exit(1)

print(f"Found {len(all_devices)} HID interfaces")

# Callback for incoming data
def on_data(data):
    print(f"Received {len(data)} bytes: {' '.join(f'{b:02X}' for b in data[:16])}")
    
    # Check for our event marker (0x01)
    if len(data) > 1 and data[1] == 0x01:
        event_type = data[2] if len(data) > 2 else 0
        print(f"  --> Event type: 0x{event_type:02X}")

# Try each device
for idx, device in enumerate(all_devices):
    print(f"\nTrying device {idx}: {device.device_path}")
    
    try:
        device.open()
        print("  Opened successfully")
        
        # Set callback
        device.set_raw_data_handler(on_data)
        
        print("  Listening for 10 seconds... (try rotating encoder)")
        time.sleep(10)
        
        device.close()
        print("  Closed")
        
    except Exception as e:
        print(f"  Error: {e}")

print("\nTest complete")
