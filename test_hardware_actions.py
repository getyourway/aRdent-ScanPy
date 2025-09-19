#!/usr/bin/env python3
"""
Test script for hardware actions support in aRdent ScanPad library
"""

import asyncio
import logging
import struct
from ardent_scanpad import ScanPad, KeyTypes, HardwareActions, KeyIDs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hardware_actions():
    """Test hardware actions configuration"""

    try:
        # Connect to device
        logger.info("🔗 Connecting to ScanPad...")
        scanpad = ScanPad()
        await scanpad.connect()

        logger.info("✅ Connected successfully!")

        # Test 1: Create scan trigger action (convenience method)
        logger.info("\n📡 Test 1: Creating scan trigger action (300ms)")
        scan_action = scanpad.keys.create_scan_trigger_action(300)
        logger.info(f"Scan action: {scan_action}")

        # Test 2: Configure key 0 with scan trigger action
        logger.info("\n⚙️  Test 2: Configuring key 0 with scan trigger action")
        success = await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_0, [scan_action])
        if success:
            logger.info("✅ Key 0 configured successfully with scan trigger!")
        else:
            logger.error("❌ Failed to configure key 0")

        # Test 3: Create different scan trigger durations
        logger.info("\n🔧 Test 3: Creating scan triggers with different durations")

        # Key 1: 500ms scan trigger
        scan_action_500ms = scanpad.keys.create_scan_trigger_action(500)
        success = await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_1, [scan_action_500ms])
        if success:
            logger.info("✅ Key 1 configured with 500ms scan trigger!")
        else:
            logger.error("❌ Failed to configure key 1")

        # Key 2: 1000ms scan trigger
        scan_action_1000ms = scanpad.keys.create_scan_trigger_action(1000)
        success = await scanpad.keys.set_key_config(KeyIDs.MATRIX_0_2, [scan_action_1000ms])
        if success:
            logger.info("✅ Key 2 configured with 1000ms scan trigger!")
        else:
            logger.error("❌ Failed to configure key 2")

        # Test 4: Read back configuration
        logger.info("\n📖 Test 4: Reading back key configurations")
        key0_config = await scanpad.keys.get_key_config(KeyIDs.MATRIX_0_0)
        if key0_config:
            logger.info(f"Key 0 config: {key0_config}")

        key1_config = await scanpad.keys.get_key_config(KeyIDs.MATRIX_0_1)
        if key1_config:
            logger.info(f"Key 1 config: {key1_config}")

        key2_config = await scanpad.keys.get_key_config(KeyIDs.MATRIX_0_2)
        if key2_config:
            logger.info(f"Key 2 config: {key2_config}")

        logger.info("\n🎯 Test completed! Press the configured keys to test hardware actions.")
        logger.info("   - Key 0: Should trigger scanner pulse (300ms)")
        logger.info("   - Key 1: Should trigger scanner pulse (500ms)")
        logger.info("   - Key 2: Should trigger scanner pulse (1000ms)")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        if 'scanpad' in locals():
            await scanpad.disconnect()
            logger.info("🔌 Disconnected")

if __name__ == "__main__":
    asyncio.run(test_hardware_actions())