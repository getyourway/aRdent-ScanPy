#!/usr/bin/env python3
"""
Device Information Demo
Demonstrates how to retrieve and display device information
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad import ScanPad
from ardent_scanpad.utils.constants import DeviceOrientations, KeyboardLayouts


async def main():
    """Device information demonstration"""
    print("🔗 Connecting to aRdent ScanPad...")
    
    # Connect to device
    scanpad = ScanPad()
    await scanpad.connect()
    print("✅ Connected!")
    
    try:
        print("\n📱 DEVICE INFORMATION")
        print("="*50)
        
        # Device Information Service (DIS)
        device_info = await scanpad.device.get_device_info()
        print("\n🏷️  Hardware Info:")
        print(f"  Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
        print(f"  Model: {device_info.get('model', 'Unknown')}")
        print(f"  Serial Number: {device_info.get('serial_number', 'Unknown')}")
        print(f"  Hardware Rev: {device_info.get('hardware_rev', 'Unknown')}")
        print(f"  Firmware Rev: {device_info.get('firmware_rev', 'Unknown')}")
        print(f"  Software Rev: {device_info.get('software_rev', 'Unknown')}")
        
        # Battery Information
        print("\n🔋 Battery Status:")
        battery_level = await scanpad.device.get_battery_level()
        print(f"  Level: {battery_level}%")
        
        try:
            battery_details = await scanpad.device.get_battery_status()
            print(f"  Voltage: {battery_details.get('voltage', 'N/A')}V")
            print(f"  Current: {battery_details.get('current', 'N/A')}mA")
            print(f"  Charging: {'Yes' if battery_details.get('is_charging', False) else 'No'}")
        except:
            print("  (Detailed battery info not available)")
        
        # Device Configuration
        print("\n⚙️  Configuration:")
        
        # Orientation
        orientation = await scanpad.device.get_orientation()
        orientation_names = {
            DeviceOrientations.PORTRAIT: "0° (Normal)",
            DeviceOrientations.LANDSCAPE: "90° (Right)",
            DeviceOrientations.REVERSE_PORTRAIT: "180° (Upside Down)",
            DeviceOrientations.REVERSE_LANDSCAPE: "270° (Left)"
        }
        print(f"  Orientation: {orientation_names.get(orientation, 'Unknown')}")
        
        # Language/Layout
        language = await scanpad.device.get_language()
        language_names = {
            KeyboardLayouts.WIN_US_QWERTY: "US English (QWERTY)",
            KeyboardLayouts.WIN_FR_AZERTY: "French (AZERTY)",
            KeyboardLayouts.WIN_ES_QWERTY: "Spanish (QWERTY)",
            KeyboardLayouts.WIN_IT_QWERTY: "Italian (QWERTY)",
            KeyboardLayouts.WIN_DE_QWERTZ: "German (QWERTZ)",
            KeyboardLayouts.MAC_US_QWERTY: "UK English (QWERTY)"
        }
        print(f"  Keyboard Layout: {language_names.get(language, 'Unknown')}")
        
        # Auto-shutdown settings
        try:
            auto_shutdown = await scanpad.device.get_auto_shutdown_config()
            print(f"  Auto-shutdown BLE: {auto_shutdown.get('ble_timeout', 0)}s")
            print(f"  Auto-shutdown Activity: {auto_shutdown.get('activity_timeout', 0)}s")
        except:
            print("  Auto-shutdown: Not available")
        
        # LED Status
        print("\n💡 LED Status:")
        led_states = await scanpad.leds.get_all_states()
        led_names = ["Green 1", "Green 2", "Green 3", "Red", "Blue"]
        
        for i, (name, state) in enumerate(zip(led_names, led_states)):
            status = "ON ✅" if state else "OFF ⬜"
            print(f"  LED {i+1} ({name}): {status}")
        
        # Key Configuration Summary
        print("\n⌨️  Key Configuration:")
        all_configs = await scanpad.keys.get_all_configs()
        configured_count = len(all_configs)
        total_actions = sum(config.get('action_count', 0) for config in all_configs.values())
        
        print(f"  Configured Keys: {configured_count}/20")
        print(f"  Total Actions: {total_actions}")
        
        if configured_count > 0:
            print("  Configured:")
            for key_id, config in list(all_configs.items())[:5]:  # Show first 5
                from ardent_scanpad.utils.constants import KeyIDs
                key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
                action_count = config.get('action_count', 0)
                enabled = "✓" if config.get('enabled', False) else "✗"
                print(f"    {enabled} {key_name}: {action_count} action(s)")
            
            if configured_count > 5:
                print(f"    ... and {configured_count - 5} more")
        
        print(f"\n📊 Summary: Device '{device_info.get('model', 'ScanPad')}' v{device_info.get('firmware_rev', '?')}")
        print(f"Battery: {battery_level}%, LEDs: {sum(led_states)}/5 ON, Keys: {configured_count}/20 configured")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("\n🔌 Disconnecting...")
        await scanpad.disconnect()


if __name__ == "__main__":
    asyncio.run(main())