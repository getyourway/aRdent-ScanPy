#!/usr/bin/env python3
"""
Generate QR Code for Barcode Filter Lua Script

This script creates a QR code that deploys a Lua script to filter
barcodes based on prefix:
- Barcodes starting with "203": Transmitted to HID (LED 3 green)
- Other barcodes: Blocked with error sound (LED 2 red)
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def main():
    print("🔍 Barcode Filter - QR Code Generator")
    print("=" * 50)
    
    # Create ScanPad instance (no BLE connection needed)
    scanpad = ScanPad()
    
    # Path to the Lua script
    script_file = Path(__file__).parent / "demo_scripts" / "barcode_filter.lua"
    
    if not script_file.exists():
        print(f"❌ Error: Script file not found: {script_file}")
        return
    
    print(f"📜 Loading script: {script_file}")
    
    try:
        # Read the script
        with open(script_file, 'r', encoding='utf-8') as f:
            lua_script = f.read()
        
        print(f"📊 Script size: {len(lua_script)} characters")
        print(f"📊 Script lines: {len(lua_script.splitlines())} lines")
        
        # Generate QR code(s) with optimal compression
        print("\n🔗 Generating QR code(s)...")
        
        qr_commands = scanpad.qr.create_lua_script_qr(
            lua_script,
            max_qr_size=1000,  # Good balance for readability
            compression_level=9  # Maximum compression
        )
        
        # Display compression statistics
        first_qr = qr_commands[0]
        metadata = first_qr.metadata
        
        print(f"\n📈 Compression Statistics:")
        print(f"   Original: {metadata['original_size_bytes']} bytes")
        print(f"   Compressed: {metadata['compressed_size_bytes']} bytes")
        print(f"   Ratio: {metadata['compression_ratio_percent']}%")
        print(f"   QR codes needed: {len(qr_commands)}")
        
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save QR code(s)
        print(f"\n💾 Saving QR code(s)...")
        
        for i, qr in enumerate(qr_commands):
            if len(qr_commands) == 1:
                filename = "barcode_filter.png"
                print(f"   📱 Single QR code: {filename}")
            else:
                fragment_num = i + 1
                total = len(qr_commands)
                filename = f"barcode_filter_{fragment_num:02d}_of_{total:02d}.png"
                
                if qr.metadata['is_final_fragment']:
                    print(f"   📱 Fragment {fragment_num}/{total} (FINAL): {filename}")
                else:
                    print(f"   📱 Fragment {fragment_num}/{total}: {filename}")
            
            filepath = output_dir / filename
            
            # Generate QR with good settings for scanning
            qr.save(filepath, size=500, border=8)
            
            # Show QR details
            print(f"       └─ Size: {qr.metadata['qr_size_chars']} characters")
        
        print(f"\n✅ QR code(s) saved in: {output_dir.absolute()}")
        
        # Instructions
        print("\n" + "=" * 50)
        print("📖 HOW TO USE:")
        print("=" * 50)
        
        print("\n1️⃣  DEPLOYMENT:")
        if len(qr_commands) == 1:
            print("   • Scan the QR code with your aRdent ScanPad")
        else:
            print("   • Scan all QR codes IN ORDER")
            for i in range(len(qr_commands)):
                print(f"     - Fragment {i+1}")
        print("   • Script will deploy and start automatically")
        
        print("\n2️⃣  OPERATION:")
        print("   • HID transmission is intercepted by the script")
        print("   • Scan barcodes starting with '203' → Transmitted (LED 3 green)")
        print("   • Scan other barcodes → Blocked (LED 2 red + error sound)")
        print("   • Only valid barcodes appear in your application")
        
        print("\n3️⃣  CONTROLS:")
        print("   • Button 15: Disable filter (re-enable normal passthrough)")
        
        print("\n4️⃣  FEATURES:")
        print("   • Prefix-based filtering (203xxx allowed)")
        print("   • Visual feedback (green=pass, red=blocked)")
        print("   • Audio alert for blocked barcodes")
        print("   • Complete HID control")
        
        print("\n5️⃣  USE CASES:")
        print("   • Product filtering (only accept specific SKUs)")
        print("   • Department restriction (203 = electronics dept)")
        print("   • Security validation (prevent unauthorized scans)")
        print("   • Data quality control")
        
        print("\n💡 TIP: Test with these barcodes:")
        print("   • '2030004720442' → Transmitted (starts with 203)")
        print("   • '1234567890123' → Blocked (doesn't start with 203)")
        print("   • '2039999999999' → Transmitted (starts with 203)")
        print("   • Press Button 15 to disable filter")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()