#!/usr/bin/env python3
"""
Generate QR Code for Duplicate Barcode Detector Lua Script

This script creates a QR code that deploys a Lua script to detect
duplicate barcode scans with LED indicators:
- LEDs 1, 3, 9: Duplicate detected (same as previous)
- LED 2: New/different barcode
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def main():
    print("🔍 Duplicate Barcode Detector - QR Code Generator")
    print("=" * 50)
    
    # Create ScanPad instance (no BLE connection needed)
    scanpad = ScanPad()
    
    # Path to the Lua script
    script_file = Path(__file__).parent / "demo_scripts" / "duplicate_detector.lua"
    
    if not script_file.exists():
        print(f"❌ Error: Script file not found: {script_file}")
        print("Creating duplicate_detector.lua...")
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
        
        # Create output directory in examples folder
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save QR code(s)
        print(f"\n💾 Saving QR code(s)...")
        
        for i, qr in enumerate(qr_commands):
            if len(qr_commands) == 1:
                filename = "duplicate_detector.png"
                print(f"   📱 Single QR code: {filename}")
            else:
                fragment_num = i + 1
                total = len(qr_commands)
                filename = f"duplicate_detector_{fragment_num:02d}_of_{total:02d}.png"
                
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
        print("   • Scan any barcode")
        print("   • If same as previous → LEDs 1,3,9 light up (⚠️ DUPLICATE)")
        print("   • If different → LED 2 lights up (✓ NEW)")
        print("   • Audio feedback for each type")
        
        print("\n3️⃣  CONTROLS:")
        print("   • Button 15: Show statistics")
        print("   • Button 14: Reset/clear memory")
        print("   • Button 13: LED test mode")
        
        print("\n4️⃣  FEATURES:")
        print("   • Real-time duplicate detection")
        print("   • Visual LED indicators")
        print("   • Audio feedback (warning for duplicates)")
        print("   • Statistics tracking")
        print("   • Memory reset function")
        
        print("\n5️⃣  USE CASES:")
        print("   • Inventory verification (prevent double scanning)")
        print("   • Quality control (detect repeated items)")
        print("   • Data entry validation")
        print("   • Warehouse picking verification")
        
        print("\n💡 TIP: Test with these sequences:")
        print("   1. Scan 'ABC123' → LED 2 (new)")
        print("   2. Scan 'ABC123' again → LEDs 1,3,9 (duplicate)")
        print("   3. Scan 'XYZ789' → LED 2 (new)")
        print("   4. Press Button 15 for statistics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()