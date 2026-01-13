"""Quick test to verify monitor detection after fix"""
import sys
sys.path.insert(0, 'C:\\Keyboard\\Keys\\python_host')

# Set up logging first
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Now import and test
from plugins.display_control import DisplayManager

print("Testing DisplayManager...")
manager = DisplayManager()

print(f"\n✓ Found {manager.get_monitor_count()} monitor(s):")
for i, mon in enumerate(manager.monitors):
    status = "ACTIVE" if mon['active'] else "INACTIVE"
    print(f"  {i+1}. [{status}] {mon['device_string']}")
    print(f"     Resolution: {mon['width']}x{mon['height']}")
    print(f"     Position: ({mon['position_x']}, {mon['position_y']})")

if manager.get_monitor_count() == 0:
    print("\n✗ ERROR: No monitors found!")
    print("  Check the enumeration logic.")
else:
    print(f"\n✓ SUCCESS: Monitor detection working!")

print("\nNow restart your app and try 'Display Control → Toggle Monitor'")
