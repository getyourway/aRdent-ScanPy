#!/usr/bin/env python3
"""
Test Export Complete Configuration Feature
==========================================

Test the new export_complete_configuration() method for both Python and comparison.
This exports keyboard configuration in standard JSON format compatible with QR codes.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    from ardent_scanpad import ScanPad
except ImportError:
    print("❌ ardent_scanpad not installed. Run: pip install -e .")
    exit(1)


async def test_export_configuration():
    """Test the new export configuration feature"""
    
    print("🧪 Testing Export Complete Configuration")
    print("=" * 50)
    
    scanpad = None
    try:
        # Initialize ScanPad
        scanpad = ScanPad()
        print("✅ ScanPad initialized")
        
        # Connect to device
        print("🔗 Connecting to device...")
        connected = await scanpad.connect()
        
        if not connected:
            print("❌ Failed to connect to device")
            print("💡 Make sure device is powered on and in range")
            return
        
        print("✅ Connected successfully!")
        
        # Get device info
        info = await scanpad.get_device_info()
        if info:
            print(f"📱 Device: {info.get('manufacturer', 'Unknown')} {info.get('model', 'Unknown')}")
            print(f"🔋 Battery: {info.get('battery', 'Unknown')}%")
        
        # Test 1: Set a test configuration first
        print("\n🧪 Setting test configuration...")
        try:
            test_action = scanpad.keys.create_text_action("Test Export " + str(asyncio.get_event_loop().time()))
            await scanpad.keys.set_key_config(0, [test_action])
            print("✅ Test configuration set on key 0")
        except Exception as e:
            print(f"⚠️ Failed to set test config: {e}")
        
        # Test 2: Export complete configuration in JSON format
        print("\n📥 Exporting complete configuration...")
        json_config = await scanpad.export_complete_configuration()
        
        print(f"✅ Export successful! Found {len(json_config)} configured keys")
        
        if json_config:
            print("\n📄 Exported Configuration:")
            print("=" * 30)
            
            for i, key_config in enumerate(json_config):
                key_id = key_config.get('parameters', {}).get('key_id')
                actions = key_config.get('parameters', {}).get('actions', [])
                print(f"🔑 Key {key_id}: {len(actions)} action(s)")
                
                for j, action in enumerate(actions[:2]):  # Show max 2 actions
                    action_type = action.get('type')
                    action_data = action.get('data', '')
                    print(f"   Action {j+1}: Type={action_type}, Data='{action_data[:20]}{'...' if len(action_data) > 20 else ''}'")
            
            # Show JSON structure
            print("\n📋 JSON Structure (first entry):")
            if json_config:
                print(json.dumps(json_config[0], indent=2))
            
            # Test 3: Verify JSON format compatibility
            print("\n✅ Format Verification:")
            for config in json_config:
                # Check required fields
                if config.get('domain') == 'keyboard_config' and config.get('action') == 'set_key_config':
                    params = config.get('parameters', {})
                    if 'key_id' in params and 'actions' in params:
                        print(f"✅ Key {params['key_id']}: Valid JSON format")
                    else:
                        print(f"❌ Key config missing parameters")
                else:
                    print(f"❌ Invalid domain/action format")
            
        else:
            print("ℹ️ No configured keys found")
        
        # Test 4: Compare with old get_all_configs
        print("\n🔄 Comparing with get_all_configs()...")
        old_format = await scanpad.keys.get_all_configs()
        print(f"📊 Old format: {len(old_format)} keys")
        print(f"📊 New format: {len(json_config)} keys")
        
        if len(old_format) == len(json_config):
            print("✅ Count matches between formats")
        else:
            print("⚠️ Count mismatch - review conversion logic")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        print(f"\n❌ Error: {e}")
    
    finally:
        if scanpad and scanpad.is_connected:
            await scanpad.disconnect()
            print("\n🔌 Disconnected from device")


async def main():
    """Main test function"""
    try:
        await test_export_configuration()
        print("\n🎉 Test completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")


if __name__ == "__main__":
    print("🚀 aRdent ScanPad - Export Configuration Test")
    print("This tests the new export_complete_configuration() feature")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")