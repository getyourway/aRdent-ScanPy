#!/usr/bin/env python3
"""
Simple Key Configuration Example
Demonstrates basic key configuration with the aRdent ScanPad
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad import ScanPad
from ardent_scanpad.utils.constants import KeyIDs, HIDKeyCodes, HIDModifiers, ConsumerCodes


async def main():
    """Simple key configuration demonstration"""
    print("🔗 Connecting to aRdent ScanPad...")
    
    # Connect to device
    scanpad = ScanPad()
    await scanpad.connect()
    print("✅ Connected!")
    
    try:
        print("\n⌨️  Configuring sample keys...")
        
        # Example 1: Simple text action
        print("1. Configuring key [0,0] to type 'Hello'")
        hello_action = scanpad.keys.create_text_action("Hello")
        await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_0, [hello_action])
        
        # Example 2: HID key with modifier
        print("2. Configuring key [0,1] for Ctrl+C (copy)")
        copy_action = scanpad.keys.create_hid_action(
            HIDKeyCodes.C, 
            HIDModifiers.LEFT_CTRL
        )
        await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_1, [copy_action])
        
        # Example 3: Consumer control
        print("3. Configuring key [0,2] for Volume Up")
        volume_action = scanpad.keys.create_consumer_action(ConsumerCodes.VOLUME_UP)
        await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_2, [volume_action])
        
        # Example 4: Multiple actions with delays
        print("4. Configuring key [0,3] for multi-action sequence")
        sequence_actions = [
            scanpad.keys.create_text_action("Hi", delay=100),
            scanpad.keys.create_hid_action(HIDKeyCodes.SPACE, delay=100),
            scanpad.keys.create_text_action("there", delay=100),
            scanpad.keys.create_hid_action(HIDKeyCodes.ENTER)
        ]
        await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_3, sequence_actions)
        
        # Example 5: Configure a button action
        print("5. Configuring power button single press for F1")
        f1_action = scanpad.keys.create_hid_action(HIDKeyCodes.F1)
        await scanpad.keys.set_key_config(KeyIDs.POWER_SINGLE, [f1_action])
        
        # Save configuration to device memory
        print("\n💾 Saving configuration to device...")
        await scanpad.keys.save_config()
        
        # Display configuration summary
        print("\n📋 Configuration Summary:")
        all_configs = await scanpad.keys.get_all_configs()
        
        for key_id, config in all_configs.items():
            key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
            action_count = config.get('action_count', 0)
            enabled = "✓" if config.get('enabled', False) else "✗"
            print(f"  {enabled} {key_name}: {action_count} action(s)")
        
        print(f"\nTotal configured keys: {len(all_configs)}")
        
        print("\n✅ Configuration complete!")
        print("\n🎯 Test your keys:")
        print("  [0,0] → Types 'Hello'")
        print("  [0,1] → Ctrl+C (copy)")
        print("  [0,2] → Volume Up")
        print("  [0,3] → Types 'Hi there' + Enter")
        print("  Power button → F1")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("\n🔌 Disconnecting...")
        await scanpad.disconnect()


if __name__ == "__main__":
    asyncio.run(main())