"""
Emergency script to re-enable all monitors
"""
import win32api
import win32con
import pywintypes

print("Re-enabling all monitors...")

device_num = 0
while True:
    try:
        device = win32api.EnumDisplayDevices(None, device_num, 0)
        device_name = device.DeviceName

        try:
            # Try to get registry settings
            devmode = win32api.EnumDisplaySettings(device_name, win32con.ENUM_REGISTRY_SETTINGS)

            # Apply registry settings (this re-enables the monitor)
            result = win32api.ChangeDisplaySettingsEx(device_name, devmode, win32con.CDS_UPDATEREGISTRY)

            if result == win32con.DISP_CHANGE_SUCCESSFUL:
                print(f"✓ Re-enabled {device_name}")
            else:
                print(f"  Skipped {device_name} (result: {result})")
        except:
            pass

        device_num += 1
    except pywintypes.error:
        break

print("\nAll monitors should be back on now!")
print("If not, press Win+P and select 'Extend'")
