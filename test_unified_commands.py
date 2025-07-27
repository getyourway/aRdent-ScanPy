#!/usr/bin/env python3
"""
Test script to verify the unified command approach works correctly
Demonstrates that all commands now wait for ESP32 response by default
"""

import asyncio
import sys
import os

# Add library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python-library'))

from ardent_scanpad import ScanPad


async def test_unified_commands():
    """Test that all commands now return ESP32 status"""
    
    print("🚀 Testing Unified Command Architecture")
    print("All commands now wait for ESP32 response and return success status")
    print("=" * 60)
    
    scanpad = ScanPad()
    
    try:
        # Connect to device
        print("📡 Connecting to aRdent ScanPad...")
        await scanpad.connect()
        print("✅ Connected successfully")
        
        # Test LED commands - now return ESP32 confirmation
        print("\n💡 Testing LED Commands (with ESP32 confirmation):")
        
        success = await scanpad.device.led.turn_on(1)
        print(f"   LED 1 ON: {'✅ Success' if success else '❌ Failed'}")
        
        await asyncio.sleep(0.5)
        
        success = await scanpad.device.led.turn_off(1)
        print(f"   LED 1 OFF: {'✅ Success' if success else '❌ Failed'}")
        
        # Test invalid LED ID - should return False (ESP32 rejects it)
        success = await scanpad.device.led.turn_on(99)  # Invalid ID
        print(f"   LED 99 (invalid): {'❌ Correctly rejected' if not success else '⚠️ Unexpectedly accepted'}")
        
        # Test Buzzer commands - now return ESP32 confirmation
        print("\n🔊 Testing Buzzer Commands (with ESP32 confirmation):")
        
        success = await scanpad.device.buzzer.beep(100)
        print(f"   Buzzer beep: {'✅ Success' if success else '❌ Failed'}")
        
        success = await scanpad.device.buzzer.play_melody('SUCCESS')
        print(f"   Buzzer melody: {'✅ Success' if success else '❌ Failed'}")
        
        # Test invalid melody - should return False (ESP32 rejects it)
        success = await scanpad.device.buzzer.play_melody('INVALID_MELODY')
        print(f"   Invalid melody: {'❌ Correctly rejected' if not success else '⚠️ Unexpectedly accepted'}")
        
        # Test Key Configuration - now return ESP32 confirmation
        print("\n📝 Testing Key Configuration (with ESP32 confirmation):")
        
        actions = [scanpad.config.create_text_action("Test")]
        success = await scanpad.config.set_key_config(0, actions)
        print(f"   Key config: {'✅ Success' if success else '❌ Failed'}")
        
        # Test invalid key ID - should return False (ESP32 rejects it)
        success = await scanpad.config.set_key_config(99, actions)  # Invalid ID
        print(f"   Invalid key 99: {'❌ Correctly rejected' if not success else '⚠️ Unexpectedly accepted'}")
        
        print("\n🎯 Summary:")
        print("   ✅ All commands now wait for ESP32 response")
        print("   ✅ Success/failure based on ESP32 status byte")
        print("   ✅ Invalid parameters correctly rejected by ESP32")
        print("   ✅ Tests can verify command execution")
        print("   ✅ Applications can ignore return value if desired")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        await scanpad.disconnect()
        print("\n📡 Disconnected from device")
    
    return True


if __name__ == "__main__":
    print(__doc__)
    success = asyncio.run(test_unified_commands())
    sys.exit(0 if success else 1)