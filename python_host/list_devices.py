"""
List all HID devices to find Keychron V1
"""
import hid

print("Enumerating all HID devices...")
print("=" * 80)

devices = hid.enumerate()

keychron_devices = []

for device in devices:
    vid = device['vendor_id']
    pid = device['product_id']
    manufacturer = device['manufacturer_string']
    product = device['product_string']
    interface = device['interface_number']
    usage_page = device['usage_page']
    usage = device['usage']
    
    # Print all devices
    print(f"VID: 0x{vid:04X}  PID: 0x{pid:04X}  Interface: {interface}")
    print(f"  Manufacturer: {manufacturer}")
    print(f"  Product: {product}")
    print(f"  Usage Page: 0x{usage_page:04X}  Usage: 0x{usage:04X}")
    print()
    
    # Look for Keychron devices
    if manufacturer and 'keychron' in manufacturer.lower():
        keychron_devices.append(device)

print("=" * 80)

if keychron_devices:
    print(f"\nFound {len(keychron_devices)} Keychron device(s):")
    for device in keychron_devices:
        print(f"  VID: 0x{device['vendor_id']:04X}, PID: 0x{device['product_id']:04X}")
        print(f"  Interface: {device['interface_number']}")
        print(f"  Usage Page: 0x{device['usage_page']:04X}")
        print(f"  Product: {device['product_string']}")
        print()
    
    print("\nUpdate hid_test.py with these values:")
    device = keychron_devices[0]
    print(f"VENDOR_ID = 0x{device['vendor_id']:04X}")
    print(f"PRODUCT_ID = 0x{device['product_id']:04X}")
else:
    print("\nNo Keychron devices found!")
    print("Make sure keyboard is plugged in and custom firmware is flashed.")
