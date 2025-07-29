#!/usr/bin/env python3
"""
Device Discovery Demo for aRdent ScanPad

Demonstrates the new discovery features:
- Discover multiple devices
- Smart device selection 
- Device information retrieval
- Live scanning with callbacks
"""

import asyncio
import logging
from typing import Dict, Any

from ardent_scanpad import ScanPad, DeviceInfo

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_discover_devices():
    """Demo 1: Discover all available ScanPad devices"""
    print("\n🔍 === DEVICE DISCOVERY DEMO ===")
    
    try:
        # Discover all aRdent ScanPad devices
        devices = await ScanPad.discover_devices(timeout=8.0, debug=True)
        
        print(f"\n✅ Found {len(devices)} aRdent ScanPad device(s):")
        
        for i, device in enumerate(devices, 1):
            print(f"\n📱 Device {i}:")
            print(f"   Address: {device['address']}")
            print(f"   Name: {device['name']}")
            print(f"   RSSI: {device['rssi']} dBm")
            print(f"   Discovered: {device['discovered_at']}")
            
        return devices
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return []


async def demo_device_selection(devices):
    """Demo 2: Smart device selection and connection"""
    print("\n🎯 === DEVICE SELECTION DEMO ===")
    
    if not devices:
        print("⚠️  No devices found, skipping selection demo")
        return None
        
    # Method 1: Connect to specific address
    device_address = devices[0]['address']
    print(f"\n1️⃣ Connecting to specific address: {device_address}")
    
    try:
        scanpad = ScanPad(device_address=device_address)
        await scanpad.connect(timeout=10.0)
        
        print("✅ Connected using specific address!")
        
        # Show device info
        info = scanpad.device_info
        if info:
            print(f"   📱 Connected to: {info['name']} at {info['address']}")
            print(f"   🕒 Connected at: {info['connected_at']}")
        
        await scanpad.disconnect()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None
    
    # Method 2: Connect by device name
    print(f"\n2️⃣ Connecting by device name: 'aRdent ScanPad'")
    
    try:
        scanpad = ScanPad(device_name="aRdent ScanPad")
        await scanpad.connect(timeout=10.0)
        
        print("✅ Connected using device name!")
        
        await scanpad.disconnect()
        
    except Exception as e:
        print(f"❌ Name-based connection failed: {e}")
    
    return scanpad


async def demo_device_info():
    """Demo 3: Comprehensive device information"""
    print("\n📱 === DEVICE INFORMATION DEMO ===")
    
    try:
        # Connect to any available device
        async with ScanPad() as scanpad:
            # Get basic device info (cached)
            basic_info = scanpad.device_info
            if basic_info:
                print("\n📄 Basic Device Information:")
                for key, value in basic_info.items():
                    print(f"   {key}: {value}")
            
            # Refresh comprehensive device info
            print("\n🔄 Refreshing comprehensive device information...")
            detailed_info = await scanpad.refresh_device_info()
            
            print("\n📋 Detailed Device Information:")
            for key, value in detailed_info.items():
                print(f"   {key}: {value}")
                
            # Demo: Monitor battery level
            battery_level = detailed_info.get('battery_level')
            if battery_level is not None:
                print(f"\n🔋 Current battery level: {battery_level}%")
                
                if battery_level < 20:
                    print("⚠️  Battery low - consider charging!")
                elif battery_level > 80:
                    print("✅ Battery level good!")
                    
    except Exception as e:
        print(f"❌ Device info demo failed: {e}")


async def demo_availability_check():
    """Demo 4: Quick device availability check"""
    print("\n⚡ === DEVICE AVAILABILITY CHECK DEMO ===")
    
    try:
        # First discover devices to get addresses
        devices = await ScanPad.discover_devices(timeout=5.0)
        
        if devices:
            device_address = devices[0]['address']
            
            print(f"\n🔍 Quick availability check for: {device_address}")
            
            # Quick check (3 second timeout)
            is_available = await ScanPad.is_device_available(device_address, timeout=3.0)
            
            if is_available:
                print("✅ Device is available and reachable!")
            else:
                print("❌ Device not found or not reachable")
                
            # Demo use case: Reconnection logic
            print("\n💡 Use case: Smart reconnection")
            if is_available:
                print(f"   → Device {device_address} is available, connecting directly")
                scanpad = ScanPad(device_address=device_address)
                await scanpad.connect()
                await scanpad.disconnect()
                print("   ✅ Fast reconnection successful!")
            else:
                print("   → Device not available, would fallback to discovery")
        
    except Exception as e:
        print(f"❌ Availability check failed: {e}")


async def demo_live_scanning():
    """Demo 5: Live scanning with callbacks"""
    print("\n📡 === LIVE SCANNING DEMO ===")
    
    discovered_count = 0
    
    def on_device_found(device_info: Dict[str, Any]):
        """Callback function for live device discovery"""
        nonlocal discovered_count
        discovered_count += 1
        
        print(f"\n🔥 Live discovery #{discovered_count}:")
        print(f"   📱 {device_info['name']}")
        print(f"   📍 {device_info['address']}")
        print(f"   📶 {device_info['rssi']} dBm")
        print(f"   🕒 {device_info['discovered_at']}")
    
    try:
        print("\n🔍 Starting live scan for 10 seconds...")
        print("   (Try turning ScanPad devices on/off to see live updates)")
        
        await ScanPad.scan_with_callback(
            callback=on_device_found,
            timeout=10.0,
            debug=False
        )
        
        print(f"\n✅ Live scan complete! Discovered {discovered_count} device(s)")
        
    except Exception as e:
        print(f"❌ Live scanning failed: {e}")


async def demo_ui_integration():
    """Demo 6: UI integration example"""
    print("\n🖥️  === UI INTEGRATION EXAMPLE ===")
    
    try:
        # Simulate UI device selection
        print("\n📋 Simulating device selection UI:")
        
        devices = await ScanPad.discover_devices(timeout=5.0)
        
        if not devices:
            print("⚠️  No devices found for UI demo")
            return
            
        # Display device list (like in a UI)
        print("\n   Device Selection Menu:")
        for i, device in enumerate(devices):
            signal_strength = "📶" if device['rssi'] > -50 else "📶" if device['rssi'] > -70 else "📶"
            print(f"   [{i+1}] {device['name']} - {device['rssi']} dBm {signal_strength}")
        
        # User selects device (simulate selecting first one)
        selected_index = 0
        selected_device = devices[selected_index]
        
        print(f"\n👆 User selected: {selected_device['name']} ({selected_device['address']})")
        
        # Connect to selected device
        scanpad = ScanPad(device_address=selected_device['address'])
        await scanpad.connect()
        
        # Display connection status (like in a UI status bar)
        info = await scanpad.refresh_device_info()
        battery = info.get('battery_level', 'Unknown')
        firmware = info.get('firmware_version', 'Unknown')
        
        print(f"\n📊 UI Status Display:")
        print(f"   Status: ✅ Connected")
        print(f"   Device: {info['name']}")
        print(f"   Battery: {battery}%")
        print(f"   Firmware: {firmware}")
        print(f"   Address: {info['address']}")
        
        await scanpad.disconnect()
        print("   Status: ❌ Disconnected")
        
    except Exception as e:
        print(f"❌ UI integration demo failed: {e}")


async def main():
    """Run all discovery demos"""
    print("🚀 aRdent ScanPad Discovery Features Demo")
    print("=" * 50)
    
    try:
        # Demo 1: Basic device discovery
        devices = await demo_discover_devices()
        
        # Demo 2: Smart device selection
        await demo_device_selection(devices)
        
        # Demo 3: Device information
        await demo_device_info()
        
        # Demo 4: Availability checking
        await demo_availability_check()
        
        # Demo 5: Live scanning
        await demo_live_scanning()
        
        # Demo 6: UI integration
        await demo_ui_integration()
        
        print("\n🎉 All discovery demos completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())