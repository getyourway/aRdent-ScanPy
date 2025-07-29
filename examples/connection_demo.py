#!/usr/bin/env python3
"""
Connection Demo - Simple connection example
Demonstrates the optimized connection workflow
"""

import asyncio
import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad import ScanPad


async def main():
    """Simple connection demonstration"""
    print("🔗 aRdent ScanPad Connection Demo")
    print("="*40)
    
    try:
        # Step 1: Create ScanPad instance
        print("1. Creating ScanPad instance...")
        scanpad = ScanPad()
        
        # Step 2: Fast connection (no automatic device info fetch)
        print("2. Connecting to device...")
        start_time = time.perf_counter()
        
        await scanpad.connect(timeout=15.0)
        
        connect_time = time.perf_counter() - start_time
        print(f"✅ Connected in {connect_time:.1f}s")
        
        # Step 3: Basic device info (cached, fast - shows structure with None values)
        print("\n📱 Basic Device Info (cached):")
        basic_info = scanpad.device_info
        if basic_info:
            print(f"  Name: {basic_info.get('name', 'Unknown')}")
            print(f"  Address: {basic_info.get('address', 'Unknown')}")
            print(f"  Status: {basic_info.get('connection_status', 'Unknown')}")
            print(f"  Battery: {basic_info.get('battery_level', 'Not fetched yet')}")
            print(f"  Firmware: {basic_info.get('firmware_version', 'Not fetched yet')}")
        
        # Step 4: Fetch detailed info (optional, user choice)
        print("\n🔄 Fetching detailed device information...")
        start_time = time.perf_counter()
        
        detailed_info = await scanpad.fetch_device_info()
        
        fetch_time = time.perf_counter() - start_time
        print(f"✅ Detailed info fetched in {fetch_time:.1f}s")
        
        print(f"  Firmware: {detailed_info.get('firmware_version', 'Unknown')}")
        print(f"  Battery: {detailed_info.get('battery_level', 'Unknown')}%")
        print(f"  Serial: {detailed_info.get('serial_number', 'Unknown')}")
        
        # Step 5: Show that cache is now updated
        print("\n📱 Cache Updated - Basic Device Info (now complete):")
        updated_basic = scanpad.device_info
        if updated_basic:
            print(f"  Battery: {updated_basic.get('battery_level', 'Still None')}%")
            print(f"  Firmware: {updated_basic.get('firmware_version', 'Still None')}")
        
        # Step 6: Simple test
        print("\n🧪 Quick LED test...")
        await scanpad.device.led.turn_on(1)
        await asyncio.sleep(1)
        await scanpad.device.led.turn_off(1)
        print("✅ LED test completed")
        
        print(f"\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if 'scanpad' in locals():
            print("\n🔌 Disconnecting...")
            await scanpad.disconnect()
            print("✅ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())