#!/usr/bin/env python3
"""
Test Clear Functionality

This script helps test the Lua clear functionality by:
1. First deploying a simple test script
2. Then generating the clear command QR
3. Instructions for manual testing
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def main():
    print("🧪 Testing Lua Clear Functionality")
    print("=" * 50)
    
    scanpad = ScanPad()
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Create a simple test script
        print("\n📝 Creating simple test script...")
        
        test_script = """
-- Simple LED test script
function setup()
    scanner_set_passthrough(false)  -- Disable normal HID
    led_all_off()
    led(1, true)  -- Turn on LED 1 to show script is active
    print("Test script loaded - LED 1 should be ON")
end

function on_scan(barcode)
    led_all_off()
    led(2, true)  -- LED 2 on scan
    print("Scanned: " .. barcode)
    -- Note: barcode won't reach HID (passthrough disabled)
end
"""
        
        # Generate test script QR
        print("📱 Generating test script QR code...")
        test_qr = scanpad.qr.create_lua_script_command(
            script_content=test_script,
            script_name="test_led_script"
        )
        
        test_filepath = output_dir / "test_script.png"
        test_qr.save(test_filepath, size=500, border=8)
        
        # 2. Generate clear command QR
        print("🧹 Generating clear command QR code...")
        clear_qr = scanpad.qr.create_lua_clear_command()
        clear_filepath = output_dir / "clear_lua_script.png"
        clear_qr.save(clear_filepath, size=500, border=8)
        
        print(f"\n✅ QR codes generated in: {output_dir.absolute()}")
        
        # 3. Testing instructions
        print("\n" + "=" * 50)
        print("🔬 MANUAL TESTING PROCEDURE")
        print("=" * 50)
        
        print("\n1️⃣ DEPLOY TEST SCRIPT:")
        print(f"   • Scan: {test_filepath.name}")
        print("   • Expected: LED 1 should turn ON")
        print("   • Test scan any barcode → LED 2 should flash")
        print("   • Important: Barcodes WON'T reach computer (passthrough disabled)")
        
        print("\n2️⃣ CLEAR SCRIPT:")
        print(f"   • Scan: {clear_filepath.name}")
        print("   • Expected: All LEDs turn OFF")
        print("   • Script should be completely removed")
        
        print("\n3️⃣ VERIFY NORMAL MODE:")
        print("   • Scan any barcode")
        print("   • Expected: Barcode reaches computer normally")
        print("   • LEDs should NOT show custom behavior")
        print("   • This confirms passthrough is re-enabled")
        
        print("\n🎯 SUCCESS CRITERIA:")
        print("   ✅ Test script works (LED 1 ON, LED 2 on scan)")
        print("   ✅ Clear command removes script (LEDs OFF)")
        print("   ✅ Normal scanning resumes (barcodes reach computer)")
        print("   ✅ Script doesn't persist after reboot")
        
        print("\n⚠️ TROUBLESHOOTING:")
        print("   • If script persists: Check both storage systems are cleared")
        print("   • If barcodes don't work: Verify passthrough reset to true")
        print("   • If LEDs stay on: Ensure lua_engine_clear_script() called")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()