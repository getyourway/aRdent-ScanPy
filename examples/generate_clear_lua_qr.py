#!/usr/bin/env python3
"""
Generate QR Code for Lua Script Clear Command

This script creates a QR code that sends the CMD_LUA_CLEAR_SCRIPT command
to clear/delete the currently loaded Lua script from the device.
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def main():
    print("🧹 Lua Script Clear - QR Code Generator")
    print("=" * 50)
    
    # Create ScanPad instance (no BLE connection needed)
    scanpad = ScanPad()
    
    try:
        # Create the clear command as a QR code
        print("\n🔗 Generating QR code for Lua clear command...")
        
        # Generate QR command using the professional method
        qr_command = scanpad.qr.create_lua_clear_command()
        
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save QR code
        print(f"\n💾 Saving QR code...")
        
        filename = "clear_lua_script.png"
        filepath = output_dir / filename
        
        # Generate and save QR image
        qr_command.save(filepath, size=500, border=8)
        
        print(f"   📱 QR code: {filename}")
        print(f"       └─ Command: {qr_command.command_data}")
        print(f"       └─ Description: {qr_command.description}")
        print(f"\n✅ QR code saved in: {output_dir.absolute()}")
        
        # Instructions
        print("\n" + "=" * 50)
        print("📖 HOW TO USE:")
        print("=" * 50)
        
        print("\n1️⃣  CLEAR SCRIPT:")
        print("   • Scan the QR code with your aRdent ScanPad")
        print("   • Current Lua script will be deleted immediately")
        print("   • Device returns to normal scanner mode")
        
        print("\n2️⃣  EFFECT:")
        print("   • Lua engine stopped and script removed from NVS memory")
        print("   • Scanner passthrough re-enabled (normal HID transmission)")
        print("   • LEDs return to default behavior")
        print("   • All Lua-specific configurations cleared")
        
        print("\n3️⃣  USE CASES:")
        print("   • Before deploying new Lua script")
        print("   • Reset device to factory scanner behavior") 
        print("   • Remove malfunctioning scripts")
        print("   • Quick cleanup for testing/development")
        
        print("\n4️⃣  CONFIRMATION:")
        print("   • No visual feedback (immediate clear)")
        print("   • Test by scanning any barcode → should transmit normally")
        print("   • LEDs should not show custom script behavior")
        
        print("\n💡 TIP:")
        print("   • Keep this QR handy for quick script removal")
        print("   • Use before deploying different Lua scripts")
        print("   • Safe to scan multiple times (no side effects)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()