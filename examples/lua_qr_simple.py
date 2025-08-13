#!/usr/bin/env python3
"""
aRdent ScanPad - Lua Script QR Generation

Example showing how to generate QR codes from a .lua file for deployment.
"""

from ardent_scanpad import ScanPad
from pathlib import Path

def main():
    # Create ScanPad instance (no BLE connection needed for QR generation)
    scanpad = ScanPad()
    
    # Path to the Lua script file (in same directory as this Python script)
    script_file = Path(__file__).parent / "lua_script.lua"
    
    if not script_file.exists():
        print(f"❌ Error: Script file not found: {script_file}")
        print("Please create a 'lua_script.lua' file in the same directory.")
        return
    
    print(f"📜 Loading Lua script from: {script_file}")
    
    try:
        # Generate QR codes from file (automatically fragments if needed)
        qr_commands = scanpad.qr.create_lua_script_from_file(script_file)
        
        # Display compression info
        first_qr = qr_commands[0]
        original_size = first_qr.metadata['original_size_bytes']
        compressed_size = first_qr.metadata['compressed_size_bytes']
        compression_ratio = first_qr.metadata['compression_ratio_percent']
        
        print(f"📊 Compression: {original_size} → {compressed_size} bytes ({compression_ratio}%)")
        print(f"📱 Generated {len(qr_commands)} QR code(s)")
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Save QR codes with descriptive names
        for i, qr in enumerate(qr_commands):
            if len(qr_commands) == 1:
                filename = "lua_script_deploy.png"
            else:
                filename = f"lua_script_part_{i+1}_of_{len(qr_commands)}.png"
            
            filepath = output_dir / filename
            qr.save(filepath)
            print(f"💾 Saved: {filename}")
            
            # Show QR details
            if len(qr_commands) > 1:
                is_final = qr.metadata['is_final_fragment']
                fragment_info = "Final (Execute)" if is_final else f"Fragment {i+1}"
                print(f"   └─ {fragment_info}: {qr.metadata['qr_size_chars']} chars")
        
        print(f"\n✅ QR codes saved in: {output_dir.absolute()}")
        print("\n📖 How to use:")
        print("1. Flash the firmware to your aRdent ScanPad")
        if len(qr_commands) == 1:
            print("2. Scan the QR code")
        else:
            print("2. Scan the QR codes in order (1, 2, ..., Final)")
        print("3. The Lua script will be deployed and executed automatically")
        
    except Exception as e:
        print(f"❌ Error generating QR codes: {e}")

if __name__ == "__main__":
    main()