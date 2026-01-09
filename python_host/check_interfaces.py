"""
Check HID interface details to find Raw HID endpoint
"""
import pywinusb.hid as hid

VENDOR_ID = 0x3434
PRODUCT_ID = 0x0311

print("Analyzing Keychron V1 HID interfaces...")
print("=" * 80)

all_devices = hid.HidDeviceFilter(vendor_id=VENDOR_ID, product_id=PRODUCT_ID).get_devices()

for idx, device in enumerate(all_devices):
    print(f"\n[Interface {idx}]")
    print(f"Path: {device.device_path}")
    
    try:
        device.open()
        
        # Get capabilities
        print(f"  Vendor: {device.vendor_name}")
        print(f"  Product: {device.product_name}")
        print(f"  Version: {device.version_number}")
        
        # Check input reports (device -> host)
        in_reports = device.find_input_reports()
        print(f"  Input reports: {len(in_reports)}")
        for report in in_reports:
            print(f"    Report ID: {report.report_id}, Size: {len(report)} bytes")
        
        # Check output reports (host -> device)
        out_reports = device.find_output_reports()
        print(f"  Output reports: {len(out_reports)}")
        for report in out_reports:
            print(f"    Report ID: {report.report_id}, Size: {len(report)} bytes")
        
        # Check feature reports
        feature_reports = device.find_feature_reports()
        print(f"  Feature reports: {len(feature_reports)}")
        
        device.close()
        
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 80)
print("\nLooking for Raw HID interface:")
print("  - Should have both input and output reports")
print("  - Typically 32 or 33 byte reports")
print("  - May be interface with mi_01 or specific usage page")
