"""
Test monitor toggle directly
"""
import sys
sys.path.insert(0, 'C:\\Keyboard\\Keys\\python_host')

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from plugins.display_control import DisplayManager

print("=" * 60)
print("Monitor Toggle Test")
print("=" * 60)

manager = DisplayManager()

print(f"\nFound {manager.get_monitor_count()} monitor(s):\n")
for i, mon in enumerate(manager.monitors):
    status = "ON" if mon['active'] else "OFF"
    primary = " [PRIMARY]" if mon['is_primary'] else ""
    print(f"{i}. {mon['friendly_name']} [{status}]{primary}")

print("\n" + "=" * 60)
print("Testing Toggle")
print("=" * 60)

# Find first non-primary monitor
test_index = None
for i, mon in enumerate(manager.monitors):
    if not mon['is_primary']:
        test_index = i
        break

if test_index is None:
    print("\n✗ No secondary monitors to test (primary cannot be toggled)")
    input("Press Enter to exit...")
    sys.exit(0)

test_monitor = manager.monitors[test_index]
print(f"\nTest monitor: {test_monitor['friendly_name']}")
print(f"Current status: {'ON' if test_monitor['active'] else 'OFF'}")

if test_monitor['active']:
    print("\n1. Testing DISABLE...")
    result = manager.toggle_monitor(test_index)
    print(f"   Result: {result}")

    input("\n   Check if monitor is off, then press Enter to continue...")

    print("\n2. Testing RE-ENABLE...")
    result = manager.toggle_monitor(test_index)
    print(f"   Result: {result}")

    print("\n   Monitor should be back on!")
else:
    print("\n1. Testing ENABLE (monitor is currently off)...")
    result = manager.toggle_monitor(test_index)
    print(f"   Result: {result}")

    input("\n   Check if monitor is on, then press Enter to continue...")

    print("\n2. Testing DISABLE...")
    result = manager.toggle_monitor(test_index)
    print(f"   Result: {result}")

    print("\n   Monitor should be off again!")

print("\n" + "=" * 60)
print("Final state:")
manager._enumerate_monitors()
for i, mon in enumerate(manager.monitors):
    status = "ON" if mon['active'] else "OFF"
    print(f"  {mon['friendly_name']}: [{status}]")

print("\nTest complete!")
input("Press Enter to exit...")
