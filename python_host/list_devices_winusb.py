"""
List all HID devices using pywinusb to find Keychron V1
"""
import pywinusb.hid as hid

print("Enumerating all HID devices...")
print("=" * 80)

all_devices = hid.find_all_hid_devices()

keychron_devices = []

for device in all_devices:
    vid = device.vendor_id
    pid = device.product_id
    manufacturer = device.vendor_name
    product = device.product_name
    
    print(f"VID: 0x{vid:04X}  PID: 0x{pid:04X}")
    print(f"  Manufacturer: {manufacturer}")
    print(f"  Product: {product}")
    print(f"  Path: {device.device_path}")
    print()
    
    # Look for Keychron devices
    if manufacturer and 'keychron' in manufacturer.lower():
        keychron_devices.append(device)

print("=" * 80)

if keychron_devices:
    print(f"\nFound {len(keychron_devices)} Keychron device(s):")
    for device in keychron_devices:
        print(f"  VID: 0x{device.vendor_id:04X}, PID: 0x{device.product_id:04X}")
        print(f"  Product: {device.product_name}")
        print(f"  Path: {device.device_path}")
        print()
    
    print("\nUpdate hid_test.py with these values:")
    device = keychron_devices[0]
    print(f"VENDOR_ID = 0x{device.vendor_id:04X}")
    print(f"PRODUCT_ID = 0x{device.product_id:04X}")
else:
    print("\nNo Keychron devices found!")
    print("Make sure keyboard is plugged in and custom firmware is flashed.")
