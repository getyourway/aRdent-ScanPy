#!/usr/bin/env python3
"""
Basic Usage Example for aRdent ScanPad Library

Demonstrates simple key configuration operations using the high-level API.
"""

import asyncio
import logging
from ardent_scanpad import ScanPad, HIDKeyCodes, HIDModifiers, ConsumerCodes

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def main():
    """
    Basic ScanPad usage demonstration
    """
    print("🚀 aRdent ScanPad - Basic Usage Example")
    print("=" * 50)
    
    try:
        # Connect to ScanPad device using context manager
        async with ScanPad(auto_reconnect=True, timeout=30.0) as device:
            print(f"✅ Connected to: {device.device_info['name']}")
            
            # Start with clean slate
            print("\n🧹 Performing factory reset...")
            await device.keys.factory_reset()
            await asyncio.sleep(1.0)
            
            print("\n📝 Configuring keys...")
            
            # 1. Simple text configuration
            print("   Key 0: 'Hello'")
            await device.keys.set_key_text("Hello", key_id=0)
            
            # 2. Text with delay
            print("   Key 1: 'World!' (with 500ms delay)")
            await device.keys.set_key_text("World!", key_id=1, delay=500)
            
            # 3. Keyboard shortcut (Ctrl+C)
            print("   Key 2: Ctrl+C")
            await device.keys.set_key_hotkey(
                HIDKeyCodes.C, HIDModifiers.LEFT_CTRL, key_id=2
            )
            
            # 4. Another shortcut (Ctrl+V)
            print("   Key 3: Ctrl+V")  
            await device.keys.set_key_hotkey(
                HIDKeyCodes.V, HIDModifiers.LEFT_CTRL, key_id=3
            )
            
            # 5. Media control (Volume Up)
            print("   Key 4: Volume Up")
            await device.keys.set_key_media(ConsumerCodes.VOLUME_UP, key_id=4)
            
            # 6. Media control (Play/Pause)
            print("   Key 5: Play/Pause")
            await device.keys.set_key_media(ConsumerCodes.PLAY_PAUSE, key_id=5)
            
            # 7. Function key
            print("   Key 6: F5 (Refresh)")
            await device.keys.set_key_hotkey(HIDKeyCodes.F5, key_id=6)
            
            # 8. Enter key
            print("   Key 7: Enter")
            await device.keys.set_key_hotkey(HIDKeyCodes.ENTER, key_id=7)
            
            # 9. Configure a button action (Scan Trigger Double-Press)
            print("   Button 16: Escape")
            await device.keys.set_key_hotkey(HIDKeyCodes.ESCAPE, key_id=16)
            
            print("\n💾 Saving configuration to device...")
            await device.keys.save_config()
            
            print("\n📊 Verifying configurations...")
            all_configs = await device.keys.get_all_configs()
            
            for key_id, config in all_configs.items():
                key_name = config.get('key_name', f'Key {key_id}')
                action_count = config.get('action_count', 0)
                enabled = config.get('enabled', False)
                status = "✅" if enabled else "❌"
                print(f"   {status} {key_name}: {action_count} action(s)")
            
            print(f"\n✅ Configuration complete! {len(all_configs)} keys configured.")
            
            # Demonstrate backup/restore
            print("\n💾 Creating configuration backup...")
            backup = await device.backup_config()
            print(f"   Backup contains {len(backup['keys'])} key configurations")
            
            # Optional: Test enable/disable
            print("\n🔧 Testing key enable/disable...")
            await device.keys.set_key_enabled(key_id=0, enabled=False)
            print("   Key 0 disabled")
            
            await asyncio.sleep(1.0)
            
            await device.keys.set_key_enabled(key_id=0, enabled=True)
            print("   Key 0 re-enabled")
            
            print("\n🎉 Basic usage demonstration complete!")
            print("\nYour ScanPad is now configured with:")
            print("   • Key 0: Types 'Hello'")
            print("   • Key 1: Types 'World!' (with delay)")
            print("   • Key 2: Ctrl+C (Copy)")
            print("   • Key 3: Ctrl+V (Paste)")
            print("   • Key 4: Volume Up")
            print("   • Key 5: Play/Pause")
            print("   • Key 6: F5 (Refresh)")
            print("   • Key 7: Enter")
            print("   • Button 16: Escape")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)