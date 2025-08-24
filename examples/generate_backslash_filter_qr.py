#!/usr/bin/env python3
"""
Generate QR Code for Backslash Filter Lua Script

This script creates a QR code that deploys a Lua script to filter out
backslash-n sequences (\\n) from scanned barcodes before transmission.
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def main():
    print("🔧 Backslash Filter Script - QR Code Generator")
    print("=" * 55)
    
    # Read the Lua script
    script_path = Path(__file__).parent / "demo_scripts" / "backslash_filter.lua"
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
        
    with open(script_path, 'r') as f:
        lua_script = f.read()
    
    print(f"📜 Script loaded: {script_path.name} ({len(lua_script)} chars)")
    
    # Create ScanPad instance (no BLE connection needed)  
    scanpad = ScanPad()
    
    try:
        # Generate QR command using the professional method
        print("\n🔗 Generating QR code for Lua script deployment...")
        
        qr_command = scanpad.qr.create_lua_script_qr(
            lua_script,
            max_qr_size=2000,  # Single large QR
            compression_level=9  # Maximum compression
        )[0]  # Take first (and only) QR code
        
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save QR code
        print(f"\n💾 Saving QR code...")
        
        filename = "backslash_filter_script.png"
        filepath = output_dir / filename
        
        # Generate and save QR image
        qr_command.save(filepath, size=500, border=8)
        
        print(f"   📱 QR code: {filename}")
        print(f"       └─ Script: backslash_filter.lua")  
        print(f"       └─ Size: {len(lua_script)} characters")
        print(f"\n✅ QR code saved in: {output_dir.absolute()}")
        
        # Instructions
        print("\n" + "=" * 55)
        print("📖 HOW TO USE:")
        print("=" * 55)
        
        print("\n1️⃣  DEPLOY SCRIPT:")
        print("   • Scan the QR code with your aRdent ScanPad")
        print("   • LED 2 (Green) will turn ON to show filter is active")
        print("   • Script will intercept all barcode scanning")
        
        print("\n2️⃣  FILTERING BEHAVIOR:")
        print("   • Removes all \\\\n sequences from barcodes")
        print("   • Removes literal newline/carriage return characters")
        print("   • Sends cleaned barcode to computer via HID")
        print("   • LED 3 flashes during processing")
        print("   • LED 1 flashes to confirm transmission")
        
        print("\n3️⃣  VISUAL FEEDBACK:")
        print("   • LED 2 ON: Filter script active")
        print("   • LED 3 flash: Processing barcode")  
        print("   • LED 1 flash: Clean barcode sent")
        
        print("\n4️⃣  EXAMPLES:")
        print("   • Input:  'ABC\\\\nDEF123'  →  Output: 'ABCDEF123'")
        print("   • Input:  'TEST\\\\n\\\\nEND' →  Output: 'TESTEND'")
        print("   • Input:  'CLEAN123'     →  Output: 'CLEAN123'")
        
        print("\n5️⃣  TO REMOVE:")
        print("   • Use clear_lua_script.png to restore normal scanning")
        print("   • Or deploy a different Lua script")
        
        print("\n💡 USE CASE:")
        print("   • Fix barcodes from systems that inject \\\\n sequences")
        print("   • Clean up data before sending to applications")
        print("   • Ensure consistent barcode format")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()